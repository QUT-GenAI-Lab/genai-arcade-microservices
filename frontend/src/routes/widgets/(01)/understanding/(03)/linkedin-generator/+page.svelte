<script module>
	export const title = 'LinkedIn Generator';
	export const hfSpace = 'QUT-GenAILab/server-linkedin-generator';
	export const widgetUrl = '/linkedin-generator';
</script>

<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
	import TextInput from '$lib/components/ui/TextInput.svelte';
	import Title from '$lib/components/title/title.svelte';
	import { getWidget, postWidget } from '$lib/widgets-api';
	import { Client } from '@gradio/client';
	import { onMount } from 'svelte';

	type HealthStatus = 'pending' | 'success' | 'error';

	interface HealthPayload {
		status: HealthStatus;
		message: string;
		metadata?: {
			checked_at?: string;
			gateway_url?: string | null;
			endpoint?: string;
			model_count?: number;
			models?: string[];
			error?: string;
		};
	}

	interface GenerationPayload {
		content: string;
		model?: string;
		source_text?: string;
		usage?: {
			prompt_tokens?: number;
			completion_tokens?: number;
			total_tokens?: number;
		};
	}

	interface HistoryEntry {
		id: string;
		input: string;
		output: string;
		createdAt: string;
	}

	const EXAMPLES = [
		"I'm sometimes tired at work",
		'I forgot to bring lunch today',
		'Our team just finished a big project',
		'I was too lazy to make coffee this morning'
	];

	const useAws = widgetUrl.length > 0;

	function getErrorMessage(error: unknown): string {
		return error instanceof Error ? error.message : 'Unknown error';
	}

	function firstPayload(result: unknown): unknown {
		if (result && typeof result === 'object' && 'data' in result) {
			const data = (result as { data?: unknown }).data;

			if (Array.isArray(data)) {
				return data[0];
			}

			return data;
		}

		if (Array.isArray(result)) {
			return result[0];
		}

		return result;
	}

	function parseHealthResult(result: unknown): HealthPayload {
		const payload = firstPayload(result);

		if (payload && typeof payload === 'object') {
			const candidate = payload as Partial<HealthPayload>;
			const status = candidate.status;

			if (status === 'pending' || status === 'success' || status === 'error') {
				return {
					status,
					message: candidate.message ?? 'Model connection checked.',
					metadata: candidate.metadata
				};
			}
		}

		return {
			status: 'error',
			message: 'Health endpoint returned an unexpected response.',
			metadata: { error: JSON.stringify(result) }
		};
	}

	function parseGenerationResult(result: unknown): GenerationPayload {
		const payload = firstPayload(result);

		if (payload && typeof payload === 'object') {
			const candidate = payload as Partial<GenerationPayload>;
			const content =
				typeof candidate.content === 'string'
					? candidate.content
					: JSON.stringify(candidate.content ?? '');

			return {
				content,
				model: candidate.model,
				source_text: candidate.source_text,
				usage: candidate.usage
			};
		}

		return {
			content: typeof payload === 'string' ? payload : JSON.stringify(payload ?? '')
		};
	}

	function nowLabel(): string {
		return new Intl.DateTimeFormat('en-US', {
			hour: 'numeric',
			minute: '2-digit'
		}).format(new Date());
	}

	let connecting = $state(false);
	let generating = $state(false);
	let app = $state.raw<Client | null>(null);
	let inputText = $state('');
	let outputText = $state('');
	let error = $state<string | null>(null);
	let health = $state.raw<HealthPayload | null>(null);
	let history = $state.raw<HistoryEntry[]>([]);
	let draft = $state.raw<HistoryEntry | null>(null);
	let activeEntryId = $state<string | null>(null);
	let requestId = $state(0);

	let modelStatus = $derived.by(() => {
		if (connecting) {
			return 'Checking';
		}

		if (!useAws && !app) {
			return 'Offline';
		}

		if (!health) {
			return 'Unknown';
		}

		if (health.status === 'success') {
			return 'Ready';
		}

		return health.status === 'pending' ? 'Pending' : 'Error';
	});

	let canGenerate = $derived(
		Boolean(
			(useAws || app) &&
			health?.status === 'success' &&
			inputText.trim() &&
			!connecting &&
			!generating
		)
	);

	let outputStatus = $derived.by(() => {
		if (generating) {
			return 'Generating LinkedIn version...';
		}

		if (outputText) {
			return 'Generated output';
		}

		return 'Waiting for input';
	});

	const sectionMetaClass = 'text-xs text-muted-text';
	const displayLabelClass = 'mb-1 text-xs font-bold';
	const noticeClass = 'bevel-raised-thin bg-surface-variant px-2.5 py-2 text-xs leading-6';
	const outputFrameClass =
		'min-h-42 bevel-sunken bg-white px-3.5 py-3 text-sm leading-[1.6] whitespace-pre-wrap';
	const chipButtonClass = 'min-h-7.5 px-2.5 py-1.25 text-[11px]';
	const historyButtonClass = 'w-full justify-start px-2.5 py-2 text-left text-[11px]';

	async function refreshHealth() {
		connecting = true;
		error = null;

		try {
			if (useAws) {
				const result = await getWidget(`${widgetUrl}/health`);
				health = parseHealthResult(result);
			} else {
				app = await Client.connect(hfSpace);
				const result = await app.predict('/health', {});
				health = parseHealthResult(result);
			}

			if (health.status === 'error') {
				error = health.metadata?.error
					? `${health.message} ${health.metadata.error}`
					: health.message;
			}
		} catch (errorValue) {
			app = null;
			health = {
				status: 'error',
				message: 'Could not check model gateway.',
				metadata: { error: getErrorMessage(errorValue) }
			};
			error = `Could not check model connection: ${getErrorMessage(errorValue)}`;
		} finally {
			connecting = false;
		}
	}

	function setInput(value: string) {
		inputText = value;
		outputText = '';
		activeEntryId = null;
		error = null;
	}

	function applyExample(example: string) {
		setInput(example);
	}

	function clearDraftIfSaved(input: string, output: string) {
		if (draft?.input === input && draft.output === output) {
			draft = null;
		}
	}

	function addHistory(input: string, output: string) {
		const entry: HistoryEntry = {
			id: crypto.randomUUID(),
			input,
			output,
			createdAt: nowLabel()
		};

		history = [entry, ...history.filter((item) => item.input !== input || item.output !== output)];
		activeEntryId = entry.id;
		clearDraftIfSaved(input, output);
	}

	function captureDraft() {
		if (activeEntryId || (!inputText.trim() && !outputText.trim())) {
			return;
		}

		draft = {
			id: 'draft',
			input: inputText,
			output: outputText,
			createdAt: nowLabel()
		};
	}

	function loadEntry(entry: HistoryEntry) {
		captureDraft();
		inputText = entry.input;
		outputText = entry.output;
		activeEntryId = entry.id;
		error = null;
	}

	function restoreDraft() {
		if (!draft) {
			return;
		}

		inputText = draft.input;
		outputText = draft.output;
		activeEntryId = null;
		error = null;
		draft = null;
	}

	function clearCurrent() {
		requestId += 1;
		inputText = '';
		outputText = '';
		error = null;
		activeEntryId = null;
		generating = false;
	}

	async function generateLinkedInPost() {
		if (generating) {
			return;
		}

		const prompt = inputText.trim();
		if (!prompt) {
			error = 'Enter some text before generating.';
			return;
		}

		if (!(useAws || app) || health?.status !== 'success') {
			error = 'Model gateway is not ready yet.';
			return;
		}

		const activeRequestId = ++requestId;
		generating = true;
		error = null;
		outputText = '';

		try {
			const result: unknown = useAws
				? await postWidget(`${widgetUrl}/generate`, { input_text: prompt })
				: await app!.predict('/generate', { input_text: prompt });
			const generation = parseGenerationResult(result);

			if (activeRequestId !== requestId) {
				return;
			}

			outputText = generation.content;
			addHistory(prompt, generation.content);
		} catch (errorValue) {
			if (activeRequestId !== requestId) {
				return;
			}

			error = `Generation failed: ${getErrorMessage(errorValue)}`;
		} finally {
			if (activeRequestId === requestId) {
				generating = false;
			}
		}
	}

	onMount(async () => {
		await refreshHealth();
	});
</script>

<Title value="LinkedIn Generator" />

<div class="grid gap-3 bg-surface-variant p-3 font-[Tahoma,Geneva,Verdana,sans-serif] text-text">
	<div class="grid gap-3 sm:grid-cols-[minmax(0,1fr)_18rem]">
		<section class="grid gap-2.5">
			<div class={[displayLabelClass, 'flex items-center justify-between']}>
				<span>Plain text</span>
				<span class={sectionMetaClass}>Model: {modelStatus}</span>
			</div>
			<p class={sectionMetaClass}>
				Enter a rough idea and generate a more formulaic LinkedIn-style version.
			</p>

			<TextInput
				id="linkedin-input"
				rows={3}
				placeholder="Write a plain idea, status update, or observation..."
				bind:value={() => inputText, setInput}
				disabled={generating}
			/>

			<div class="flex flex-wrap gap-2">
				<Button onclick={() => void generateLinkedInPost()} disabled={!canGenerate}>
					{generating ? 'Generating...' : 'Generate LinkedIn version'}
				</Button>
				<Button variant="secondary" onclick={clearCurrent} disabled={!inputText && !outputText}>
					Clear
				</Button>
				<Button
					variant="secondary"
					onclick={() => void refreshHealth()}
					disabled={connecting || generating}
				>
					{connecting ? 'Checking...' : 'Reconnect model'}
				</Button>
			</div>
		</section>

		<aside class="grid content-start gap-3">
			<section class="grid gap-2.5">
				<div class="flex items-baseline justify-between gap-2">
					<div class={displayLabelClass}>History</div>
					<span class={sectionMetaClass}>{history.length} saved</span>
				</div>

				{#if draft}
					<Button
						variant="secondary"
						className={historyButtonClass}
						onclick={restoreDraft}
						disabled={generating}
					>
						<span class="grid gap-1">
							<span>Draft</span>
							<span class="font-normal text-muted-text">{draft.input || 'Empty draft'}</span>
						</span>
					</Button>
				{/if}

				{#if history.length}
					<ol class="m-0 grid max-h-64 list-none gap-2 overflow-y-auto p-0">
						{#each history as entry (entry.id)}
							<li>
								<Button
									variant="secondary"
									pressed={activeEntryId === entry.id}
									className={historyButtonClass}
									onclick={() => loadEntry(entry)}
									disabled={generating}
								>
									<span class="grid gap-1">
										<span>{entry.createdAt}</span>
										<span class="font-normal text-muted-text">{entry.input}</span>
									</span>
								</Button>
							</li>
						{/each}
					</ol>
				{:else}
					<p class={[noticeClass, 'm-0']}>Generated posts will be saved here.</p>
				{/if}
			</section>
		</aside>
	</div>

	<section class="grid gap-2.5">
		<div class={displayLabelClass}>Examples</div>
		<div class="flex flex-wrap gap-2">
			{#each EXAMPLES as example (example)}
				<Button
					variant="secondary"
					className={chipButtonClass}
					onclick={() => applyExample(example)}
					disabled={generating}
				>
					{example}
				</Button>
			{/each}
		</div>
	</section>

	{#if error}
		<p class={[noticeClass, 'm-0 text-[#7f0000]']}>{error}</p>
	{/if}

	<section class="grid gap-2.5">
		<div class="flex items-baseline justify-between gap-2">
			<div class={displayLabelClass}>LinkedIn version</div>
			<span class={sectionMetaClass}>{outputStatus}</span>
		</div>

		<div class={[outputFrameClass, generating && 'text-muted-text']} aria-live="polite">
			{#if generating}
				Generating a LinkedIn-style post...
			{:else if outputText}
				{outputText}
			{:else}
				Generated text will appear here.
			{/if}
		</div>
	</section>
</div>
