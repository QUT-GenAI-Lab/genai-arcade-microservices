<script lang="ts">
	import type { MenuItem } from '$lib/data/arcade';
	import { jumpToFragment } from '$lib/navigation';

	interface Props {
		items: MenuItem[];
	}

	let { items }: Props = $props();
</script>

<nav class="menu-bar" aria-label="Window menu">
	<ul>
		{#each items as item (item.label)}
			<li>
				{#if item.external}
					<a href={item.href} target="_blank" rel="external noreferrer">{item.label}</a>
				{:else}
					<button type="button" onclick={() => jumpToFragment(item.href)}>{item.label}</button>
				{/if}
			</li>
		{/each}
	</ul>
</nav>

<style>
	.menu-bar {
		border-bottom: 1px solid var(--arcade-window-shadow);
		padding: 4px 6px;
	}

	ul {
		display: flex;
		flex-wrap: wrap;
		gap: 12px;
		list-style: none;
		margin: 0;
		padding: 0;
	}

	a,
	button {
		background: transparent;
		border: 0;
		color: var(--arcade-text);
		font-size: 12px;
		padding: 0;
		text-decoration: none;
	}

	a:hover,
	a:focus-visible,
	button:hover,
	button:focus-visible {
		text-decoration: underline;
	}
</style>
