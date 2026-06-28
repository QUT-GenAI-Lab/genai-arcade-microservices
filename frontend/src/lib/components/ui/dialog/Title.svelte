<script lang="ts">
	import type { Snippet } from 'svelte';
	import { getDialogContext } from './context.svelte';

	interface Props {
		children?: Snippet;
	}

	let { children }: Props = $props();
	const context = getDialogContext();
	let titleEl: HTMLElement | undefined = $state();

	$effect(() => {
		if (titleEl) {
			const text = titleEl.textContent?.trim() ?? '';
			if (text) context.setTitle(text);
		}
	});
</script>

<span bind:this={titleEl} aria-hidden="true" class="hidden">
	{@render children?.()}
</span>
