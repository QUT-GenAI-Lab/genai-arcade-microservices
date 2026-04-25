<script lang="ts">
	import WindowFrame from '$lib/components/ui/WindowFrame.svelte';
	import myComputerIcon from '$lib/assets/images/mycomputer.png';
	import { twMerge } from 'tailwind-merge';
	import type { Snippet } from 'svelte';

	type Props = {
		title: string;
		children: Snippet;
		class?: string;
	};

	let { title, children, class: className }: Props = $props();
</script>

<WindowFrame {title} icon={myComputerIcon} class={twMerge('size-full', className)}>
	<div class="widget-content">
		{@render children()}
	</div>
</WindowFrame>

<style>
	.widget-content {
		background: var(--arcade-surface);
		border: 2px solid;
		border-color: var(--arcade-window-shadow) var(--arcade-outline-light)
			var(--arcade-outline-light) var(--arcade-window-shadow);
		padding: 0.5rem;
	}
</style>
