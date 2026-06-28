<script module>
	export const title = 'Milkless';
	export const widgetUrl = '/milkless';
</script>

<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
	import TextInput from '$lib/components/ui/TextInput.svelte';
	import Title from '$lib/components/title/title.svelte';
	import { WidgetBackend } from '$lib/widgets/widget-backend.svelte';
	import { GenerateResponseSchema } from '$lib/widgets/schemas';
	import { onMount } from 'svelte';
	import Markdown from 'svelte-exmarkdown';
	import ChatLoader from '$lib/components/ui/ChatLoader.svelte';

	interface ChatMessage {
		role: 'user' | 'assistant';
		content: string;
	}

	const EXAMPLES = [
		{ label: 'Morning drink', prompt: "What's a good morning drink?" },
		{
			label: 'Creamy pasta sauce',
			prompt: 'How do I make a creamy pasta sauce?'
		},
		{
			label: 'Cow products',
			prompt: 'What are some common products made from cows?'
		},
		{
			label: 'Cheese making',
			prompt: 'How is cheese made?'
		},
		{
			label: 'Lactose intolerance',
			prompt: 'What is lactose intolerance and how does it affect people?'
		}
	];

	const backend = new WidgetBackend(`${widgetUrl}`);

	function getErrorMessage(error: unknown): string {
		return error instanceof Error ? error.message : 'Unknown error';
	}

	let connecting = $state(false);
	let generating = $state(false);
	let userInput = $state('');
	let error = $state<string | null>(null);
	let chatHistory = $state.raw<ChatMessage[]>([]);
	let requestId = $state(0);
	let inputRef = $state<HTMLTextAreaElement>();

	const GREETING = "Hi! I'm configured with a no-dairy rule. Ask me anything 🙂";

	let modelStatus = $derived.by(() => {
		if (connecting) return 'Checking';
		if (backend.status === 'Ready') return 'Ready';
		if (backend.status === 'Pending') return 'Pending';
		if (backend.status === 'Error') return 'Error';
		return 'Unknown';
	});

	let assistantStatusDotClass = $derived.by(() => {
		if (backend.status === 'Ready') return 'bg-emerald-500';
		if (backend.status === 'Pending' || connecting) return 'bg-amber-500';
		if (backend.status === 'Error') return 'bg-[#7f0000]';
		return 'bg-muted-text';
	});

	const sectionMetaClass = 'text-xs text-muted-text';
	const displayLabelClass = 'mb-1 text-xs font-bold';
	const noticeClass = 'bevel-raised-thin bg-surface-variant px-2.5 py-2 text-xs leading-6';
	const chipButtonClass = 'min-h-7.5 px-2.5 py-1.25 text-[11px]';
	const messageClass = 'bevel-sunken-thin bg-white px-3 py-2 text-sm leading-6 w-fit max-w-[80%]';
	const userMsgClass = 'border-r-4 border-[#6b7280] ml-auto';
	const assistantMsgClass = 'border-l-4 border-[#9ca3af]';

	async function refreshHealth() {
		connecting = true;
		error = null;
		await backend.healthCheck();
		connecting = false;

		if (backend.status === 'Error' && backend.message?.type === 'error') {
			error = backend.message.content;
		}
	}

	function sendGreetingIfEmpty() {
		if (chatHistory.length === 0) {
			chatHistory = [...chatHistory, { role: 'assistant', content: GREETING }];
		}
	}

	async function sendMessage() {
		if (generating) return;

		const trimmedInput = userInput.trim();
		if (!trimmedInput) return;

		if (backend.status !== 'Ready') {
			error = 'Model gateway is not ready yet.';
			return;
		}

		const activeRequestId = ++requestId;
		generating = true;
		error = null;

		chatHistory = [...chatHistory, { role: 'user', content: trimmedInput }];
		userInput = '';

		try {
			const { data, error: parseError } = await backend.post(
				'/generate',
				{ input_text: trimmedInput },
				{ schema: GenerateResponseSchema }
			);

			if (activeRequestId !== requestId) return;

			if (parseError || !data) {
				throw parseError ?? new Error('Failed to parse generation result');
			}

			const trimmedContent = data.content.trim();
			chatHistory = [...chatHistory, { role: 'assistant', content: trimmedContent }];
		} catch (errorValue) {
			if (activeRequestId !== requestId) return;
			error = `Generation failed: ${getErrorMessage(errorValue)}`;
		} finally {
			if (activeRequestId === requestId) {
				generating = false;
			}
		}
	}

	async function loadExample(prompt: string) {
		userInput = prompt;
		await sendMessage();
		inputRef?.focus();
	}

	function clearChat() {
		requestId += 1;
		chatHistory = [];
		userInput = '';
		error = null;
		generating = false;
		inputRef?.focus();
		sendGreetingIfEmpty();
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey && !event.ctrlKey && !event.metaKey) {
			event.preventDefault();
			void sendMessage();
		}
	}

	onMount(async () => {
		await refreshHealth();
		sendGreetingIfEmpty();
		inputRef?.focus();
	});

	let chatContainer = $state<HTMLDivElement>();

	$effect(() => {
		void chatHistory.length;
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	});
</script>

<Title value="Milkless" />

<div class="grid gap-3 bg-surface-variant p-3 font-[Tahoma,Geneva,Verdana,sans-serif] text-text">
	<section class="grid gap-2.5">
		<p class={sectionMetaClass}>
			Chat with an AI assistant that's been instructed to refuse anything dairy. Push on the rule to
			see how safely the model holds the line.
		</p>

		<section class="flex h-110 flex-col bg-white bevel-sunken">
			<div bind:this={chatContainer} class="flex-1 space-y-2 overflow-y-auto p-3">
				{#each chatHistory as entry, index (`${index}-${entry.role}-${entry.content.length}`)}
					<div class={[messageClass, entry.role === 'user' ? userMsgClass : assistantMsgClass]}>
						<div class="flex items-center gap-2">
							<p class="m-0 text-[10px] font-bold tracking-wide text-muted-text uppercase">
								{entry.role === 'user' ? 'You' : 'AI assistant'}
							</p>
							{#if entry.role === 'assistant'}
								<span
									class={['size-1.5 rounded-full', assistantStatusDotClass]}
									aria-hidden="true"
									title={`Model: ${modelStatus}`}
								></span>
							{/if}
						</div>
						<div
							class="text-sm whitespace-normal [&_li]:my-1 [&_li]:ml-2 [&_ol]:list-decimal [&_ol]:pl-4 [&_ul]:list-disc [&_ul]:pl-4"
						>
							<Markdown md={entry.content} />
						</div>
					</div>
				{/each}
				{#if generating}
					<div class={[messageClass, assistantMsgClass]}>
						<div class="flex items-center gap-2">
							<p class="m-0 text-[10px] font-bold tracking-wide text-muted-text uppercase">
								AI assistant
							</p>
							<span
								class={['size-1.5 rounded-full', assistantStatusDotClass]}
								aria-hidden="true"
								title={`Model: ${modelStatus}`}
							></span>
						</div>
						<p class="m-0 mt-1 whitespace-pre-wrap">
							<ChatLoader interval={50} length={24} maxDots={3} />
						</p>
					</div>
				{/if}
			</div>
			<div class="flex gap-1.5 border-t border-[#d8d2d8] p-2">
				<TextInput
					id="chat-input"
					rows={1}
					bind:ref={inputRef}
					placeholder="Ask the AI assistant anything..."
					bind:value={() => userInput, (value) => (userInput = value)}
					onkeydown={handleKeydown}
					onEnter={async () => {
						await sendMessage();
						inputRef?.focus();
					}}
					disabled={generating}
					class="py-1 bevel-sunken-thin focus-within:bevel-sunken-thin"
				/>
				<Button
					onclick={async () => {
						await sendMessage();
						inputRef?.focus();
					}}
					disabled={!userInput.trim() || generating || backend.status !== 'Ready'}
				>
					{generating ? 'Sending...' : 'Send'}
				</Button>
			</div>
		</section>

		{#if error}
			<p class={[noticeClass, 'm-0 text-[#7f0000]']}>{error}</p>
		{/if}
	</section>

	<div class="flex flex-wrap gap-2">
		<Button
			variant="secondary"
			onclick={clearChat}
			disabled={!chatHistory.length && !userInput && !generating}
		>
			Clear chat
		</Button>
		<Button
			variant="secondary"
			onclick={() => void refreshHealth()}
			disabled={connecting || generating}
		>
			{connecting ? 'Checking...' : 'Reconnect model'}
		</Button>
	</div>

	<section class="grid gap-2.5">
		<div class={displayLabelClass}>Try these prompts</div>
		<div class="flex flex-wrap gap-2">
			{#each EXAMPLES as example (example.label)}
				<Button
					variant="secondary"
					class={chipButtonClass}
					onclick={() => loadExample(example.prompt)}
					disabled={generating}
				>
					{example.label}
				</Button>
			{/each}
		</div>
	</section>
</div>
