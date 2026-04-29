<script lang="ts">
	import type { MenuItem } from '$lib/data/arcade';
	import { jumpToFragment } from '$lib/navigation';

	interface Props {
		items: MenuItem[];
	}

	let { items }: Props = $props();
</script>

<nav class="border-b border-b-window-shadow px-1.5 py-1" aria-label="Window menu">
	<ul class="m-0 flex list-none flex-wrap gap-3 p-0">
		{#each items as item (item.label)}
			<li>
				{#if item.external}
					<a
						class="border-0 bg-transparent p-0 text-xs text-text no-underline hover:underline focus-visible:underline"
						href={item.href}
						target="_blank"
						rel="external noreferrer"
					>
						{item.label}
					</a>
				{:else}
					<button
						class="border-0 bg-transparent p-0 text-xs text-text hover:underline focus-visible:underline"
						type="button"
						onclick={() => jumpToFragment(item.href)}
					>
						{item.label}
					</button>
				{/if}
			</li>
		{/each}
	</ul>
</nav>
