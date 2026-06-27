<script lang="ts">
	import type { Snippet } from 'svelte';
	import { twMerge } from 'tailwind-merge';

	interface Props {
		children?: Snippet;
		class?: string;
	}

	let { children, class: className = '' }: Props = $props();
</script>

<section class={twMerge('flex flex-col bg-surface-chrome p-0.5 bevel-raised', className)}>
	{@render children?.()}
</section>
