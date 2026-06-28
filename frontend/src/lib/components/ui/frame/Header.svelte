<script lang="ts">
	import type { Component, Snippet } from 'svelte';
	import { twMerge } from 'tailwind-merge';

	interface Props {
		title: string;
		icon?: string | Component;
		children?: Snippet;
		class?: string;
	}

	let { title, children, class: className = '', ...props }: Props = $props();
</script>

<header
	class={twMerge(
		'flex items-center justify-between gap-1 bg-primary px-1 pt-0.5 pb-0.75 text-on-primary',
		className
	)}
>
	<div class="flex w-fit items-center gap-1.5">
		{#if props.icon}
			{#if typeof props.icon === 'string'}
				<img class="h-3.5 w-3.5 shrink-0" src={props.icon} alt="" />
			{:else}
				<props.icon />
			{/if}
		{/if}
		<h2 class="m-0 text-sm font-bold whitespace-nowrap">{title}</h2>
	</div>

	{#if children}
		{@render children()}
	{/if}
</header>
