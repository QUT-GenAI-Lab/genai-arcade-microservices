<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLButtonAttributes } from 'svelte/elements';
	import { twMerge } from 'tailwind-merge';

	interface Props extends Omit<HTMLButtonAttributes, 'children'> {
		children?: Snippet;
		variant?: 'primary' | 'secondary';
		pressed?: boolean;
		class?: string;
		size?: 'small' | 'medium' | 'large' | 'icon';
	}

	let {
		children,
		variant = 'primary',
		pressed = false,
		class: className = '',
		size = 'medium',
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
		'inline-flex items-center justify-center gap-2 px-3.5 py-1.75 text-center font-[Tahoma,Geneva,Verdana,sans-serif] text-xs leading-[1.2] font-bold no-underline',
		'bevel-raised',
		'bg-primary text-on-primary',
		'cursor-pointer hover:bevel-sunken focus-visible:bevel-sunken focus-visible:outline-none',
		variant === 'secondary' && 'bg-surface-variant text-text',
		pressed && 'bevel-sunken',
		disabled &&
			'cursor-default opacity-50 disabled:hover:bevel-raised disabled:focus-visible:bevel-raised',
		size === 'icon' && 'aspect-square h-fit min-h-0 pt-0.5 pr-1 pb-1 pl-0.5',
		size === 'small' && 'min-h-0.5 gap-1 pt-0.5 pr-1 pb-1 pl-0.5 text-[0.625rem] leading-[1.2]',
		size === 'large' && 'h-9 px-4 py-2 text-[0.75rem] leading-[1.2]',
		className
	])}
>
	{@render children?.()}
</button>
