<script module>
	export const title = 'Model Gateway Chat';
	// Important: This page only works with local Gradio API, as we don't want to expose the model gateway URL publicly.
	export const hfSpace = 'http://127.0.0.1:7860';
</script>

<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
	import Dropdown from '$lib/components/ui/Dropdown.svelte';
	import TextInput from '$lib/components/ui/TextInput.svelte';
	import Title from '$lib/components/title/title.svelte';
	import { Client } from '@gradio/client';
	import { onMount } from 'svelte';

	interface ChatMessage {
		role: 'system' | 'user' | 'assistant';
		content: string;
	}

	interface UsageInfo {
		prompt_tokens: number;
		completion_tokens: number;
		total_tokens: number;
	}

	interface GenerateResponse {
		model: string;
		content: string;
		usage: UsageInfo;
	}

	interface GradioResult {
		data?: unknown;
	}

	interface ModelInfo {
		id: string;
		type: string;
		backend: string;
		max_tokens: number;
	}

	const EXAMPLES = [
		{ label: 'Greeting', prompt: 'Hello! What can you help me with?' },
		{ label: 'Math', prompt: 'What is the square root of 144?' },
		{ label: 'Code', prompt: 'Write a Python function to reverse a string.' },
		{ label: 'Creative', prompt: 'Write a haiku about programming.' },
		{ label: 'Facts', prompt: 'Explain how machine learning works in simple terms.' }
	];

	function getErrorMessage(error: unknown): string {
		if (error instanceof Error) return error.message;
		if (error && typeof error === 'object' && 'message' in error) {
			const msg = (error as { title?: string; message: string }).message;
			const title = (error as { title?: string }).title;
			return title ? `${title}: ${msg}` : msg;
		}
		return 'Unknown error';
	}

	function extractResponse(result: unknown): GenerateResponse {
		const payload = result as GradioResult | GenerateResponse | undefined;

		if (payload && typeof payload === 'object' && 'data' in payload) {
			const data = payload.data;
			if (Array.isArray(data) && data[0]) {
				const first = data[0];
				if (typeof first === 'string') {
					try {
						return JSON.parse(first) as GenerateResponse;
					} catch {
						return {
							model: 'unknown',
							content: first,
							usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 }
						};
					}
				}
				return first as GenerateResponse;
			}
			if (typeof data === 'object' && data !== null) {
				return data as GenerateResponse;
			}
		}

		if (payload && 'model' in payload && 'content' in payload) {
			return payload as GenerateResponse;
		}

		return {
			model: 'unknown',
			content: JSON.stringify(result),
			usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 }
		};
	}

	let loading = $state(false);
	let generating = $state(false);
	let app = $state.raw<Client | null>(null);
	let systemPrompt = $state('You are a helpful assistant.');
	let userInput = $state('');
	let chatHistory = $state.raw<{ message: ChatMessage; timestamp: Date }[]>([]);
	let error = $state<string | null>(null);
	let lastUsage = $state.raw<UsageInfo | null>(null);
	let requestId = $state(0);
	let models = $state.raw<ModelInfo[]>([]);
	let selectedModel = $state('');

	let modelStatus = $derived.by(() => {
		if (loading) return 'Connecting';
		if (generating) return 'Generating';
		return app ? 'Ready' : 'Offline';
	});

	let messageCount = $derived(chatHistory.length);

	const panelMetaClass = 'text-xs font-bold text-muted-text';
	const noticeClass = 'bevel-raised-thin bg-surface px-2.5 py-2 text-xs leading-6';
	const chipButtonClass = 'min-h-7.5 px-2.5 py-1.25 text-[11px]';
	const messageClass = 'bevel-sunken-thin bg-white px-3 py-2 text-sm leading-6 w-fit max-w-[80%]';
	const userMsgClass = 'border-l-4 border-primary';
	const assistantMsgClass = 'border-r-4 border-secondary ml-auto';
	const systemMsgClass = 'border-l-4 border-muted-text italic text-muted-text';

	async function fetchModels() {
		if (!app) return;
		try {
			const result = await app.predict('/models', {});
			const payload =
				result && typeof result === 'object' && 'data' in result
					? (result as GradioResult).data
					: result;
			const data = Array.isArray(payload) ? payload[0] : payload;
			if (data && typeof data === 'object' && data !== null && 'models' in data) {
				models = (data as { models: ModelInfo[] }).models;
				if (models.length > 0 && !selectedModel) {
					selectedModel = models[0].id;
				}
			}
		} catch (errorValue) {
			console.error('Failed to fetch models:', getErrorMessage(errorValue));
		}
	}

	async function connectModel() {
		loading = true;
		error = null;

		try {
			app = await Client.connect(hfSpace);
			await fetchModels();
		} catch (errorValue) {
			app = null;
			models = [];
			selectedModel = '';
			error = `Could not load model: ${getErrorMessage(errorValue)}`;
		} finally {
			loading = false;
		}
	}

	async function sendMessage() {
		if (generating) return;
		if (!app) {
			error = 'Model not connected yet.';
			return;
		}

		const trimmedInput = userInput.trim();
		if (!trimmedInput) return;

		const activeRequestId = ++requestId;
		generating = true;
		error = null;

		const messages: ChatMessage[] = [
			{ role: 'system', content: systemPrompt },
			...chatHistory.map((m) => m.message),
			{ role: 'user', content: trimmedInput }
		];

		chatHistory = [...chatHistory, { message: { role: 'user', content: trimmedInput }, timestamp: new Date() }];
		userInput = '';

		try {
			const result = await app.predict('/generate', {
				messages: messages,
				model: selectedModel,
				max_tokens: 512,
				temperature: 0.7,
				top_p: 0.9,
				stop: []
			});
			console.log('Raw response from model:', result);

			if (activeRequestId !== requestId) return;

			const response = extractResponse(result);
			chatHistory = [...chatHistory, { message: { role: 'assistant', content: response.content }, timestamp: new Date() }];
			lastUsage = response.usage;
		} catch (errorValue) {
			if (activeRequestId !== requestId) return;
			error = `Generation failed: ${getErrorMessage(errorValue)}`;
		} finally {
			if (activeRequestId === requestId) {
				generating = false;
			}
		}
	}

	function clearChat() {
		requestId += 1;
		chatHistory = [];
		lastUsage = null;
		error = null;
		generating = false;
	}

	function loadExample(prompt: string) {
		userInput = prompt;
		void sendMessage();
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey && !event.ctrlKey && !event.metaKey) {
			event.preventDefault();
			void sendMessage();
		}
	}

	onMount(async () => {
		await connectModel();
	});

	let chatContainer = $state<HTMLDivElement>();

	$effect(() => {
		void chatHistory.length;
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	});

	let currentDotIndex = $state(0);
	let direction = $state<'forward' | 'backward'>('forward');
	const LENGTH = 24;
	const MAX_DOTS = 5;
	onMount(() => {
		// Animate a moving "..." effect (e.g., "...  ", " ... ", "  ...", "...  ", etc.) to indicate the model is generating a response.
		const interval = setInterval(() => {
			// Cycle the dot index forward and backward to create a "ping-pong" effect
			if (direction === 'forward') {
				currentDotIndex += 1;
			} else {
				currentDotIndex -= 1;
			}

			// Reverse direction at the ends
			if (currentDotIndex >= LENGTH - MAX_DOTS) {
				currentDotIndex = LENGTH - MAX_DOTS;
				direction = 'backward';
			} else if (currentDotIndex <= 0) {
				currentDotIndex = 0;
				direction = 'forward';
			}
		}, 100);

		return () => clearInterval(interval);
	});
	const animatedDots = $derived.by(() => {
		return '.'
			.repeat(MAX_DOTS)
			.padStart(currentDotIndex + MAX_DOTS, ' ')
			.padEnd(LENGTH, ' ');
	});
</script>

<Title value="Model Gateway Chat" />

<div class="grid gap-3 bg-surface-variant p-3 font-[Tahoma,Geneva,Verdana,sans-serif] text-text">
	<section class="grid gap-2.5">
		<div class="flex items-start justify-between max-[760px]:block">
			<div>
				<div class="flex flex-wrap items-baseline gap-x-3 gap-y-2">
					<h2 class="m-0 text-base leading-[1.2]">Chat</h2>
					<p class={['m-0', panelMetaClass]}>Status: {modelStatus}</p>
				</div>
				<p class="mt-1 max-w-[68ch] leading-6">
					Chat with available models via the Model Gateway API. Supports multi-turn conversations
					with system prompt configuration.
				</p>
			</div>
		</div>

		<div class="grid gap-2">
			<label
				class="font-[Tahoma,Geneva,Verdana,sans-serif] text-xs font-bold tracking-[0.04em] uppercase"
				for="system-prompt"
			>
				System Prompt
			</label>
			<textarea
				id="system-prompt"
				rows={2}
				bind:value={systemPrompt}
				class="w-full resize-y bg-white px-3 py-2 text-sm leading-6 bevel-sunken focus:bg-white focus:bevel-sunken focus-visible:outline-none"
				placeholder="Set the assistant's behavior..."
			></textarea>
		</div>

		<Dropdown
			id="model-select"
			label="Model"
			hint={models.length === 0 ? 'No models available.' : `${models.length} model(s) loaded.`}
			options={models.map((m) => ({ value: m.id, label: m.id }))}
			bind:value={selectedModel}
			disabled={!app || models.length === 0}
		/>

		{#if chatHistory.length > 0}
			<div class="grid max-h-96 gap-2 overflow-y-auto" bind:this={chatContainer}>
				{#each chatHistory as entry (entry.timestamp.toISOString())}
					<div
						class={[
							messageClass,
							entry.message.role === 'user'
								? userMsgClass
								: entry.message.role === 'assistant'
									? assistantMsgClass
									: systemMsgClass
						]}
					>
						<span class="text-xs font-bold text-muted-text uppercase">{entry.message.role}</span>
						<p class="mt-1 whitespace-pre-wrap">{entry.message.content}</p>
					</div>
				{/each}
				{#if generating}
					<div class={[messageClass, assistantMsgClass]}>
						<span class="text-xs font-bold text-muted-text uppercase">assistant</span>
						<p class="mt-1 whitespace-pre-wrap">{animatedDots}</p>
					</div>
				{/if}
			</div>
		{:else}
			<p class={[noticeClass, 'm-0']}>Type a message below to start chatting with the model.</p>
		{/if}

		{#if lastUsage}
			<div class="bg-surface px-3 py-2 text-xs text-muted-text bevel-raised-thin">
				Tokens: {lastUsage.prompt_tokens} prompt + {lastUsage.completion_tokens} completion = {lastUsage.total_tokens}
				total
			</div>
		{/if}

		<div class="grid gap-2">
			<TextInput
				id="chat-input"
				rows={3}
				placeholder="Type your message..."
				bind:value={() => userInput, (value) => (userInput = value)}
				onkeydown={handleKeydown}
			/>

			<div class="flex flex-wrap gap-2">
				<Button
					onclick={() => void sendMessage()}
					disabled={loading || generating || !userInput.trim()}
				>
					{generating ? 'Generating...' : 'Send'}
				</Button>
				<Button
					variant="secondary"
					onclick={clearChat}
					disabled={!chatHistory.length && !generating}
				>
					Clear chat
				</Button>
				<Button variant="secondary" onclick={() => void connectModel()} disabled={loading}>
					Reconnect model
				</Button>
			</div>
		</div>

		{#if error}
			<p class={[noticeClass, 'm-0 text-[#7f0000]']}>{error}</p>
		{/if}
	</section>

	<section class="grid gap-2.5">
		<div class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1.5">
			<div>
				<h2 class="m-0 text-base leading-[1.2]">Example prompts</h2>
			</div>
			<p class={['m-0', panelMetaClass]}>Messages: {messageCount}</p>
		</div>

		<div class="flex flex-wrap gap-2">
			{#each EXAMPLES as example (example.label)}
				<Button
					variant="secondary"
					className={chipButtonClass}
					onclick={() => loadExample(example.prompt)}
				>
					{example.label}
				</Button>
			{/each}
		</div>
	</section>
</div>
