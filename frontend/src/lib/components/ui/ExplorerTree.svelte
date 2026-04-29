<script lang="ts">
	import type { ExplorerTreeItem } from '$lib/data/arcade';
	import { jumpToFragment } from '$lib/navigation';
	import { twMerge } from 'tailwind-merge';

	interface Props {
		items: ExplorerTreeItem[];
		class?: string;
	}

	let { items, class: className = '' }: Props = $props();

	const navItemClass =
		'flex w-full max-w-full items-center gap-1.5 overflow-hidden whitespace-nowrap bg-transparent pr-1.5 text-text';
	const interactiveNavItemClass =
		'no-underline hover:bg-primary hover:text-on-primary focus-visible:bg-primary focus-visible:text-on-primary focus-visible:outline-none';
	const activeNavItemClass = 'bg-primary text-on-primary';
</script>

{#snippet navItem(item: ExplorerTreeItem)}
	<li>
		{#if item.external}
			<a
				class={[navItemClass, interactiveNavItemClass, item.active && activeNavItemClass]}
				href={item.href}
				target="_blank"
				rel="external noreferrer"
			>
				<img class="h-4 w-4 shrink-0" src={item.icon} alt="" />
				<span class="overflow-hidden text-ellipsis">{item.title}</span>
			</a>
		{:else if item.href !== undefined}
			<button
				class={[
					navItemClass,
					interactiveNavItemClass,
					'cursor-pointer border-0 p-0 text-left',
					item.active && activeNavItemClass
				]}
				type="button"
				onclick={() => jumpToFragment(item.href!)}
			>
				<img class="h-4 w-4 shrink-0" src={item.icon} alt="" />
				<span class="overflow-hidden text-ellipsis">{item.title}</span>
			</button>
		{:else}
			<div class={[navItemClass, item.active && activeNavItemClass]}>
				<img class="h-4 w-4 shrink-0" src={item.icon} alt="" />
				<span class="overflow-hidden text-ellipsis">{item.title}</span>
			</div>
		{/if}

		{#if item.children?.length}
			<ul
				class="explorer-tree__branch m-0 list-none p-0 [&>li]:bg-[url($lib/assets/images/pixel-alt.png)] [&>li]:bg-position-[0_8px] [&>li]:bg-repeat-x [&>li]:pl-1"
			>
				{#each item.children as child (child.title)}
					{@render navItem(child)}
				{/each}
			</ul>
		{/if}
	</li>
{/snippet}

<nav
	class={twMerge(
		'explorer-tree h-full min-h-96 overflow-auto bg-white bg-[url($lib/assets/images/pixel-alt.png)] bg-position-[15px_0] bg-repeat-y px-0 py-1.25 bevel-sunken',
		className
	)}
	aria-label="Arcade explorer"
>
	<ul class="explorer-tree__root m-0 list-none p-0 [&>li]:pl-1">
		{#each items as item (item.title)}
			{@render navItem(item)}
		{/each}
	</ul>
</nav>
