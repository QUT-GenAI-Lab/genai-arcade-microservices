<script lang="ts">
	import type { Snippet } from 'svelte';
	import { twMerge } from 'tailwind-merge';
	import { getDialogContext } from './context.svelte';

	interface Props {
		children?: Snippet;
		class?: string;
	}

	let { children, class: className = '' }: Props = $props();
	const context = getDialogContext();
</script>

<button
	type="button"
	aria-label="Close"
	class={twMerge(
		'inline-flex h-3.5 w-3.5 cursor-pointer items-center justify-center bg-surface-variant p-0 pr-0.5 pb-0.5 text-[10px] leading-none font-bold text-text bevel-raised hover:bevel-sunken focus-visible:bevel-sunken focus-visible:outline-none',
		className
	)}
	onclick={() => context.setOpen(false)}
>
	{@render children?.()}
</button>
