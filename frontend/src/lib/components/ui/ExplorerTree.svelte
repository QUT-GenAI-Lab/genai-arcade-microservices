<script lang="ts">
	import type { ExplorerTreeItem } from '$lib/data/arcade';
	import { jumpToFragment } from '$lib/navigation';
	import { twMerge } from 'tailwind-merge';

	interface Props {
		items: ExplorerTreeItem[];
		class?: string;
	}

	let { items, class: className = '' }: Props = $props();
</script>

{#snippet navItem(item: ExplorerTreeItem)}
	<li>
		{#if item.external}
			<a class:active={item.active} href={item.href} target="_blank" rel="external noreferrer">
				<img src={item.icon} alt="" />
				<span>{item.title}</span>
			</a>
		{:else if item.href !== undefined}
			<button class:active={item.active} type="button" onclick={() => jumpToFragment(item.href!)}>
				<img src={item.icon} alt="" />
				<span>{item.title}</span>
			</button>
		{:else}
			<div class:active={item.active} class="nav-item">
				<img src={item.icon} alt="" />
				<span>{item.title}</span>
			</div>
		{/if}

		{#if item.children?.length}
			<ul class="explorer-tree__branch">
				{#each item.children as child (child.title)}
					{@render navItem(child)}
				{/each}
			</ul>
		{/if}
	</li>
{/snippet}

<nav class={twMerge('explorer-tree', className)} aria-label="Arcade explorer">
	<ul class="explorer-tree__root">
		{#each items as item (item.title)}
			{@render navItem(item)}
		{/each}
	</ul>
</nav>

<style>
	.explorer-tree {
		background: var(--arcade-surface) url('$lib/assets/images/pixel-alt.png') repeat-y 15px 0;
		border: 2px solid;
		border-color: var(--arcade-window-shadow) var(--arcade-outline-light)
			var(--arcade-outline-light) var(--arcade-window-shadow);
		min-height: 24rem;
		overflow: auto;
		padding: 5px 0;
		height: 100%;
	}

	.explorer-tree__root,
	.explorer-tree__branch {
		list-style: none;
		margin: 0;
		padding: 0;
	}

	.explorer-tree__root > li {
		padding-left: 4px;
	}

	.explorer-tree__branch li {
		background: transparent url('$lib/assets/images/pixel-alt.png') repeat-x 0 8px;
		padding-left: 1rem;
	}

	a,
	.nav-item,
	button {
		align-items: center;
		background: transparent;
		border: 0;
		color: var(--arcade-text);
		display: flex;
		gap: 6px;
		max-width: 100%;
		overflow: hidden;
		padding: 0 6px 0 0;
		text-decoration: none;
		white-space: nowrap;
		width: 100%;
	}

	img {
		flex: none;
		height: 16px;
		width: 16px;
	}

	span {
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.active,
	.nav-item:hover,
	a:hover,
	a:focus-visible,
	button:hover,
	button:focus-visible {
		background: var(--arcade-primary);
		color: var(--arcade-on-primary);
		outline: none;
	}
</style>
