<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { WindowControl } from '$lib/data/arcade';
	import { jumpToFragment } from '$lib/navigation';
	import { twMerge } from 'tailwind-merge';

	interface Props {
		title: string;
		icon?: string;
		children?: Snippet;
		controls?: WindowControl[];
		class?: string;
	}

	let { title, icon, children, controls = [], class: className = '' }: Props = $props();
	const controlClass =
		'inline-flex h-3.5 w-3.5 items-center justify-center bevel-raised bg-surface-variant p-0 text-[10px] leading-none font-bold text-text';
</script>

<section
	class={twMerge(
		'flex flex-col bevel-raised bg-surface-chrome p-0.5',
		className
	)}
>
	<header
		class="flex items-center justify-between bg-primary px-1 pt-0.5 pb-0.75 text-on-primary"
	>
		<div class="flex min-w-0 items-center gap-1.5">
			{#if icon}
				<img class="h-3.5 w-3.5 shrink-0" src={icon} alt="" />
			{/if}
			<h2 class="m-0 overflow-hidden text-sm font-bold text-ellipsis whitespace-nowrap">{title}</h2>
		</div>

		{#if controls.length}
			<div class="flex gap-0.75" aria-label="Window controls">
				{#each controls as control (control.label)}
					{#if control.href && !control.disabled}
						<button
							class={controlClass}
							type="button"
							aria-label={control.label}
							onclick={() => jumpToFragment(control.href ?? '#top')}
						>
							{control.symbol}
						</button>
					{:else}
						<span
							class={[controlClass, control.disabled && 'text-muted-text']}
							aria-hidden="true"
						>
							{control.symbol}
						</span>
					{/if}
				{/each}
			</div>
		{/if}
	</header>

	<div class="h-full p-0">
		{@render children?.()}
	</div>
</section>
