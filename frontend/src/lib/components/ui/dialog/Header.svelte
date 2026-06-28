<script lang="ts">
	import type { Component, Snippet } from 'svelte';
	import { twMerge } from 'tailwind-merge';
	import * as Frame from '$lib/components/ui/frame/index.js';
	import { getDialogContext } from './context.svelte';
	import Close from './Close.svelte';

	interface Props {
		title?: string;
		icon?: string | Component;
		children?: Snippet;
		class?: string;
	}

	let { title, icon, children, class: className = '' }: Props = $props();
	const context = getDialogContext();
	let resolvedTitle = $derived(title ?? context.title ?? '');
</script>

<Frame.Header title={resolvedTitle} {icon} class={twMerge(className)}>
	{@render children?.()}
	<Close>X</Close>
</Frame.Header>
