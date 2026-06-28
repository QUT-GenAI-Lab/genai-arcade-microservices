<script lang="ts">
	import type { Snippet } from 'svelte';
	import { setDialogContext } from './context.svelte';

	interface Props {
		open?: boolean;
		onOpenChange?: (open: boolean) => void;
		children?: Snippet;
	}

	let { open = $bindable(false), onOpenChange, children }: Props = $props();
	const state = setDialogContext();

	$effect(() => {
		state.setOpen(open);
	});

	$effect(() => {
		onOpenChange?.(state.open);
	});
</script>

{@render children?.()}
