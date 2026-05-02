<script module>
	export const title = 'Model Gateway Chat';
	export const hfSpace = 'http://127.0.0.1:7860';
</script>

<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
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
	let chatHistory = $state.raw<ChatMessage[]>([]);
	let error = $state<string | null>(null);
	let lastUsage = $state.raw<UsageInfo | null>(null);
	let requestId = $state(0);

	let modelStatus = $derived.by(() => {
		if (loading) return 'Connecting';
		if (generating) return 'Generating';
		return app ? 'Ready' : 'Offline';
	});

	let messageCount = $derived(chatHistory.length);

	const panelMetaClass = 'text-xs font-bold text-muted-text';
	const noticeClass = 'bevel-raised-thin bg-surface px-2.5 py-2 text-xs leading-6';
	const chipButtonClass = 'min-h-7.5 px-2.5 py-1.25 text-[11px]';
	const messageClass = 'bevel-sunken-thin bg-white px-3 py-2 text-sm leading-6';
	const userMsgClass = 'border-l-4 border-primary';
	const assistantMsgClass = 'border-l-4 border-secondary';
	const systemMsgClass = 'border-l-4 border-muted-text italic text-muted-text';

	async function connectModel() {
		loading = true;
		error = null;

		try {
			app = await Client.connect(hfSpace);
		} catch (errorValue) {
			app = null;
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
			...chatHistory,
			{ role: 'user', content: trimmedInput }
		];

		chatHistory = [...chatHistory, { role: 'user', content: trimmedInput }];
		userInput = '';

		try {
			const result = await app.predict('/generate', {
				messages: messages,
				max_tokens: 512,
				temperature: 0.7,
				top_p: 0.9,
				stop: []
			});
			console.log('Raw response from model:', result);

			if (activeRequestId !== requestId) return;

			const response = extractResponse(result);
			chatHistory = [...chatHistory, { role: 'assistant', content: response.content }];
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
</script>

<Title value="Model Gateway Chat" />

<div class="grid gap-3 bg-surface-variant p-3 font-[Tahoma,Geneva,Verdana,sans-serif] text-text">
	<section class="grid gap-2.5">
		<div class="flex items-start justify-between max-[760px]:block">
			<div>
				<div class="flex flex-wrap items-baseline gap-x-3 gap-y-2">
					<h2 class="m-0 text-base leading-[1.2]">Chat</h2>
					<p class={['m-0', panelMetaClass]}>Model: {modelStatus}</p>
				</div>
				<p class="mt-1 max-w-[68ch] leading-6">
					Chat with Llama 3.2 3B via the Model Gateway API. Supports multi-turn conversations with
					system prompt configuration.
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

		{#if chatHistory.length > 0}
			<div class="grid max-h-96 gap-2 overflow-y-auto">
				{#each chatHistory as message (message.role + '-' + message.content.slice(0, 20))}
					<div
						class={[
							messageClass,
							message.role === 'user'
								? userMsgClass
								: message.role === 'assistant'
									? assistantMsgClass
									: systemMsgClass
						]}
					>
						<span class="text-xs font-bold text-muted-text uppercase">{message.role}</span>
						<p class="mt-1 whitespace-pre-wrap">{message.content}</p>
					</div>
				{/each}
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
