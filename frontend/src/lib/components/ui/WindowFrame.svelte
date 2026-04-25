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
</script>

<section class={twMerge('window-frame', className)}>
	<header class="titlebar">
		<div class="titlebar__label">
			{#if icon}
				<img src={icon} alt="" />
			{/if}
			<h2>{title}</h2>
		</div>

		{#if controls.length}
			<div class="titlebar__controls" aria-label="Window controls">
				{#each controls as control (control.label)}
					{#if control.href && !control.disabled}
						<button
							class="control"
							type="button"
							aria-label={control.label}
							onclick={() => jumpToFragment(control.href ?? '#top')}
						>
							{control.symbol}
						</button>
					{:else}
						<span class={['control', control.disabled && 'control--disabled']} aria-hidden="true">
							{control.symbol}
						</span>
					{/if}
				{/each}
			</div>
		{/if}
	</header>

	<div class="window-frame__body">
		{@render children?.()}
	</div>
</section>

<style>
	.window-frame {
		background: var(--arcade-surface-chrome);
		border: 2px solid;
		border-color: var(--arcade-outline-light) var(--arcade-outline-dark) var(--arcade-outline-dark)
			var(--arcade-outline-light);
		padding: 2px;
		display: flex;
		flex-direction: column;
	}

	.titlebar {
		align-items: center;
		background: var(--arcade-primary);
		color: var(--arcade-on-primary);
		display: flex;
		justify-content: space-between;
		padding: 2px 4px 3px;
	}

	.titlebar__label {
		align-items: center;
		display: flex;
		gap: 6px;
		min-width: 0;
	}

	.titlebar__label img {
		flex: none;
		height: 14px;
		width: 14px;
	}

	h2 {
		font-size: 14px;
		font-weight: 700;
		margin: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.titlebar__controls {
		display: flex;
		gap: 3px;
	}

	.control {
		align-items: center;
		background: var(--arcade-surface-variant);
		border: 2px solid;
		border-color: var(--arcade-outline-light) var(--arcade-outline-dark) var(--arcade-outline-dark)
			var(--arcade-outline-light);
		color: var(--arcade-text);
		display: inline-flex;
		font-size: 10px;
		font-weight: 700;
		height: 14px;
		justify-content: center;
		line-height: 1;
		padding: 0;
		width: 14px;
	}

	.control--disabled {
		color: var(--arcade-muted-text);
	}

	.window-frame__body {
		padding: 0;
		height: 100%;
	}
</style>
