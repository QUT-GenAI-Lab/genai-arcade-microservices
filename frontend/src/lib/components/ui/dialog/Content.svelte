<script lang="ts">
	import type { Snippet } from 'svelte';
	import { twMerge } from 'tailwind-merge';
	import * as Frame from '$lib/components/ui/frame/index.js';
	import { getDialogContext } from './context.svelte';

	interface Props {
		position?: 'center' | 'trigger';
		children?: Snippet;
		class?: string;
	}

	let { position = 'center', children, class: className = '' }: Props = $props();
	const context = getDialogContext();

	let isTriggerPosition = $derived(position === 'trigger' && context.triggerRect !== null);

	let triggerTop = $derived(
		isTriggerPosition && context.triggerRect ? `${context.triggerRect.bottom + 4}px` : undefined
	);
	let triggerLeft = $derived(
		isTriggerPosition && context.triggerRect ? `${context.triggerRect.left}px` : undefined
	);

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape' && context.open) {
			context.setOpen(false);
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

{#if context.open}
	{#if isTriggerPosition}
		<div
			role="dialog"
			aria-modal="true"
			style:position="fixed"
			style:top={triggerTop}
			style:left={triggerLeft}
		>
			<Frame.Root class={twMerge('w-80 max-w-sm overflow-auto', className)}>
				<Frame.Body>
					{@render children?.()}
				</Frame.Body>
			</Frame.Root>
		</div>
	{:else}
		<div
			role="dialog"
			aria-modal="true"
			class="fixed inset-0 z-50 flex items-center justify-center p-4"
		>
			<button
				type="button"
				tabindex="-1"
				aria-label="Close dialog"
				class="absolute inset-0 z-0 h-full w-full cursor-default border-0 bg-black/40 p-0"
				onclick={() => context.setOpen(false)}
			></button>
			<Frame.Root
				class={twMerge('relative z-10 max-h-[90vh] w-full max-w-md overflow-auto', className)}
			>
				<Frame.Body>
					{@render children?.()}
				</Frame.Body>
			</Frame.Root>
		</div>
	{/if}
{/if}
