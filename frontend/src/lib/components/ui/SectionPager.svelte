<script lang="ts">
	import type { PagerLink } from '$lib/data/arcade';
	import { jumpToFragment } from '$lib/navigation';

	interface Props {
		previous: PagerLink | null;
		next: PagerLink | null;
	}

	let { previous, next }: Props = $props();
</script>

<div class="section-pager">
	<button type="button" onclick={() => jumpToFragment('#top')}>⌂ Home</button>

	<div class="section-pager__center">
		{#if previous}
			<button type="button" onclick={() => jumpToFragment(previous.href)}>◀ {previous.label}</button
			>
		{/if}

		{#if next}
			<button type="button" onclick={() => jumpToFragment(next.href)}>{next.label} ▶</button>
		{/if}
	</div>

	<div aria-hidden="true"></div>
</div>

<style>
	.section-pager {
		align-items: center;
		border-top: 1px solid var(--arcade-window-shadow);
		display: grid;
		font-size: 14px;
		gap: 12px;
		grid-template-columns: 1fr 2fr 1fr;
		margin-top: 24px;
		padding-top: 16px;
	}

	.section-pager__center {
		display: flex;
		flex-wrap: wrap;
		gap: 24px;
		justify-content: center;
	}

	button {
		background: transparent;
		border: 0;
		color: var(--arcade-text);
		padding: 0;
		text-decoration: none;
	}

	button:hover,
	button:focus-visible {
		text-decoration: underline;
	}

	@media (max-width: 700px) {
		.section-pager {
			grid-template-columns: 1fr;
			justify-items: start;
		}

		.section-pager__center {
			justify-content: flex-start;
		}
	}
</style>
