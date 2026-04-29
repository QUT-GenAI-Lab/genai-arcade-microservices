<script lang="ts">
	import type { PagerLink } from '$lib/data/arcade';
	import { jumpToFragment } from '$lib/navigation';

	interface Props {
		previous: PagerLink | null;
		next: PagerLink | null;
	}

	let { previous, next }: Props = $props();
</script>

<div
	class="mt-6 grid [grid-template-columns:1fr_2fr_1fr] items-center gap-3 border-t-window-shadow pt-4 text-sm max-[700px]:grid-cols-1 max-[700px]:justify-items-start"
>
	<button
		class="border-0 bg-transparent p-0 text-text hover:underline focus-visible:underline"
		type="button"
		onclick={() => jumpToFragment('#top')}
	>
		⌂ Home
	</button>

	<div class="flex flex-wrap justify-center gap-6 max-[700px]:justify-start">
		{#if previous}
			<button
				class="border-0 bg-transparent p-0 text-text hover:underline focus-visible:underline"
				type="button"
				onclick={() => jumpToFragment(previous.href)}>◀ {previous.label}</button
			>
		{/if}

		{#if next}
			<button
				class="border-0 bg-transparent p-0 text-text hover:underline focus-visible:underline"
				type="button"
				onclick={() => jumpToFragment(next.href)}>{next.label} ▶</button
			>
		{/if}
	</div>

	<div aria-hidden="true"></div>
</div>
