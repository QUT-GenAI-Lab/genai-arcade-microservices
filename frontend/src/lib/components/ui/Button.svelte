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
		'button',
		`button--${variant}`,
		pressed && 'button--pressed',
		disabled && 'button--disabled',
		className
	]}
>
	{@render children?.()}
</button>

<style>
	.button {
		align-items: center;
		background: var(--arcade-primary);
		border: 2px solid;
		border-color: var(--arcade-outline-light) var(--arcade-outline-dark) var(--arcade-outline-dark)
			var(--arcade-outline-light);
		color: var(--arcade-on-primary);
		cursor: pointer;
		display: inline-flex;
		font-family: Tahoma, Geneva, Verdana, sans-serif;
		font-size: 12px;
		font-weight: 700;
		gap: 8px;
		justify-content: center;
		line-height: 1.2;
		min-height: 34px;
		padding: 7px 14px;
		text-align: center;
		text-decoration: none;
	}

	.button--secondary {
		background: var(--arcade-surface-variant);
		color: var(--arcade-text);
	}

	.button:hover,
	.button:focus-visible,
	.button--pressed {
		border-color: var(--arcade-outline-dark) var(--arcade-outline-light) var(--arcade-outline-light)
			var(--arcade-outline-dark);
		outline: none;
	}

	.button--disabled {
		color: var(--arcade-muted-text);
		cursor: default;
	}

	.button--disabled:hover,
	.button--disabled:focus-visible {
		border-color: var(--arcade-outline-light) var(--arcade-outline-dark) var(--arcade-outline-dark)
			var(--arcade-outline-light);
		outline: none;
	}
</style>
