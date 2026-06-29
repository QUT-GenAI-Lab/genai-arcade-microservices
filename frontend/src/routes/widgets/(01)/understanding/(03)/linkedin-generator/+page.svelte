<script module>
	export const title = 'LinkedIn Generator';
	export const widgetUrl = '/linkedin-generator';
</script>

<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
	import TextInput from '$lib/components/ui/TextInput.svelte';
	import Title from '$lib/components/title/title.svelte';
	import { WidgetBackend } from '$lib/widgets/widget-backend.svelte';
	import { GenerateResponseSchema } from '$lib/widgets/schemas';
	import { onMount } from 'svelte';
	import ChatLoader from '$lib/components/ui/ChatLoader.svelte';

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

	const backend = new WidgetBackend(`${widgetUrl}`);

	function getErrorMessage(error: unknown): string {
		return error instanceof Error ? error.message : 'Unknown error';
	}

	function nowLabel(): string {
		return new Intl.DateTimeFormat('en-US', {
			hour: 'numeric',
			minute: '2-digit'
		}).format(new Date());
	}

	let connecting = $state(false);
	let generating = $state(false);
	let inputText = $state('');
	let outputText = $state('');
	let error = $state<string | null>(null);
	let history = $state.raw<HistoryEntry[]>([]);
	let draft = $state.raw<HistoryEntry | null>(null);
	let activeEntryId = $state<string | null>(null);
	let requestId = $state(0);

	let modelStatus = $derived.by(() => {
		if (connecting) return 'Checking';
		if (backend.status === 'Ready') return 'Ready';
		if (backend.status === 'Pending') return 'Pending';
		if (backend.status === 'Error') return 'Error';
		if (backend.status === 'Not Checked') return 'Unknown';
		return 'Unknown';
	});

	let canGenerate = $derived(
		Boolean(backend.status === 'Ready' && inputText.trim() && !connecting && !generating)
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
		await backend.healthCheck();
		connecting = false;

		if (backend.status === 'Error' && backend.message?.type === 'error') {
			error = backend.message.content;
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

		if (backend.status !== 'Ready') {
			error = 'Model gateway is not ready yet.';
			return;
		}

		const activeRequestId = ++requestId;
		generating = true;
		error = null;
		outputText = '';

		try {
			const { data, error: parseError } = await backend.post(
				'/generate',
				{ input_text: prompt },
				{ schema: GenerateResponseSchema }
			);

			if (activeRequestId !== requestId) {
				return;
			}

			if (parseError || !data) {
				throw parseError ?? new Error('Failed to parse generation result');
			}

			outputText = data.content;
			addHistory(prompt, data.content);
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

	onMount(() => {
		void refreshHealth();
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
						class={historyButtonClass}
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
									class={historyButtonClass}
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
					class={chipButtonClass}
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
				<ChatLoader interval={50} length={48} maxDots={3} />
			{:else if outputText}
				{outputText}
			{:else}
				Generated text will appear here.
			{/if}
		</div>
	</section>
</div>
