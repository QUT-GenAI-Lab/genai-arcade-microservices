<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLButtonAttributes } from 'svelte/elements';
	import { twMerge } from 'tailwind-merge';

	interface Props extends Omit<HTMLButtonAttributes, 'children'> {
		children?: Snippet;
		variant?: 'primary' | 'secondary';
		pressed?: boolean;
		className?: string;
	}

	let {
		children,
		variant = 'primary',
		pressed = false,
		className = '',
		type = 'button',
		disabled = false,
		...props
	}: Props = $props();
</script>

<button
	{...props}
	{type}
	{disabled}
	class={twMerge([
		'inline-flex min-h-8.5 items-center justify-center gap-2 px-3.5 py-1.75 text-center font-[Tahoma,Geneva,Verdana,sans-serif] text-xs leading-[1.2] font-bold no-underline',
		'bevel-raised',
		'bg-primary text-on-primary',
		'cursor-pointer hover:bevel-sunken focus-visible:bevel-sunken focus-visible:outline-none',
		variant === 'secondary' && 'bg-surface-variant text-text',
		pressed && 'bevel-sunken',
		disabled &&
			'cursor-default opacity-50 disabled:hover:bevel-raised disabled:focus-visible:bevel-raised',
		className
	])}
>
	{@render children?.()}
</button>
