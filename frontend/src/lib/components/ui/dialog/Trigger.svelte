<script lang="ts">
	import type { HTMLButtonAttributes } from 'svelte/elements';
	import type { Snippet } from 'svelte';
	import { twMerge } from 'tailwind-merge';
	import { getDialogContext } from './context.svelte';

	interface Props extends Omit<HTMLButtonAttributes, 'children'> {
		children?: Snippet;
		class?: string;
	}

	let { children, class: className = '', ...props }: Props = $props();
	const context = getDialogContext();

	function handleClick(event: MouseEvent) {
		context.setTriggerRect((event.currentTarget as HTMLElement).getBoundingClientRect());
		context.setOpen(true);
	}
</script>

<button
	{...props}
	type="button"
	aria-haspopup="dialog"
	class={twMerge(className)}
	onclick={handleClick}
>
	{@render children?.()}
</button>
