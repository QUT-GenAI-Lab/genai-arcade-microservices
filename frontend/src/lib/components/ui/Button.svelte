<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLButtonAttributes } from 'svelte/elements';

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
	class={[
		'inline-flex min-h-8.5 items-center justify-center gap-2 border-2 px-3.5 py-1.75 text-center font-[Tahoma,Geneva,Verdana,sans-serif] text-xs leading-[1.2] font-bold no-underline',
		'border-t-outline-light border-r-outline-dark border-b-outline-dark border-l-outline-light',
		'bg-primary text-on-primary',
		'cursor-pointer hover:border-t-outline-dark hover:border-r-outline-light hover:border-b-outline-light hover:border-l-outline-dark focus-visible:border-t-outline-dark focus-visible:border-r-outline-light focus-visible:border-b-outline-light focus-visible:border-l-outline-dark focus-visible:outline-none',
		variant === 'secondary' && 'bg-surface-variant text-text',
		pressed &&
			'border-t-outline-dark border-r-outline-light border-b-outline-light border-l-outline-dark',
		disabled &&
			'cursor-default text-muted-text disabled:hover:border-t-outline-light disabled:hover:border-r-outline-dark disabled:hover:border-b-outline-dark disabled:hover:border-l-outline-light disabled:focus-visible:border-t-outline-light disabled:focus-visible:border-r-outline-dark disabled:focus-visible:border-b-outline-dark disabled:focus-visible:border-l-outline-light',
		className
	]}
>
	{@render children?.()}
</button>
