<script lang="ts">
	import type { DesktopNavItem } from '$lib/data/arcade';
	import { jumpToFragment } from '$lib/navigation';

	interface Props {
		items: DesktopNavItem[];
	}

	let { items }: Props = $props();
</script>

<nav class="flex gap-1 max-sm:flex-col" aria-label="Primary page navigation">
	{#each items as item (item.label)}
		<button
			class={[
				'group block flex-1 basis-0 border-0 bg-transparent p-0 text-inherit',
				item.compact && 'shrink-0 basis-39 max-sm:basis-auto'
			]}
			type="button"
			onclick={() => jumpToFragment(item.href)}
		>
			<div
				class="flex h-11 w-full flex-col items-center justify-center gap-0.5 border-2 border-t-outline-light border-r-outline-dark border-b-outline-dark border-l-outline-light bg-surface-variant px-2.5 text-center text-text group-hover:border-t-outline-dark group-hover:border-r-outline-light group-hover:border-b-outline-light group-hover:border-l-outline-dark group-focus-visible:border-t-outline-dark group-focus-visible:border-r-outline-light group-focus-visible:border-b-outline-light group-focus-visible:border-l-outline-dark"
			>
				<span class="text-lg leading-none" aria-hidden="true">{item.icon}</span>
				<span class="w-full overflow-hidden text-[10px] font-bold text-ellipsis whitespace-nowrap">
					{item.label}
				</span>
			</div>
		</button>
	{/each}
</nav>
