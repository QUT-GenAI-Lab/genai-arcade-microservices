<script lang="ts">
	import type { CardItem } from '$lib/data/arcade';
	import { jumpToFragment } from '$lib/navigation';

	interface Props {
		items: CardItem[];
	}

	let { items }: Props = $props();
</script>

<div class="card-grid">
	{#each items as item (item.title)}
		{#if item.external}
			<a class="card" href={item.href} target="_blank" rel="external noreferrer">
				<div class="card__header">
					<img src={item.icon} alt="" />
					<div>
						{#if item.eyebrow}
							<p class="card__eyebrow">{item.eyebrow}</p>
						{/if}
						<h3>{item.title}</h3>
					</div>
				</div>

				<p class="card__description">{item.description}</p>

				{#if item.meta}
					<p class="card__meta">{item.meta}</p>
				{/if}
			</a>
		{:else}
			<button class="card" type="button" onclick={() => jumpToFragment(item.href)}>
				<div class="card__header">
					<img src={item.icon} alt="" />
					<div>
						{#if item.eyebrow}
							<p class="card__eyebrow">{item.eyebrow}</p>
						{/if}
						<h3>{item.title}</h3>
					</div>
				</div>

				<p class="card__description">{item.description}</p>

				{#if item.meta}
					<p class="card__meta">{item.meta}</p>
				{/if}
			</button>
		{/if}
	{/each}
</div>

<style>
	.card-grid {
		display: grid;
		gap: 12px;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
	}

	.card {
		background: var(--arcade-surface);
		border: 2px solid;
		border-color: var(--arcade-window-shadow) var(--arcade-outline-light)
			var(--arcade-outline-light) var(--arcade-window-shadow);
		cursor: pointer;
		color: var(--arcade-text);
		display: flex;
		flex-direction: column;
		gap: 10px;
		min-height: 150px;
		padding: 14px;
		text-align: left;
		text-decoration: none;
	}

	.card:hover,
	.card:focus-visible {
		background: #f5f1ff;
		outline: 2px solid var(--arcade-primary);
		outline-offset: 2px;
	}

	.card__header {
		align-items: flex-start;
		display: flex;
		gap: 10px;
	}

	img {
		height: 18px;
		margin-top: 3px;
		width: 18px;
	}

	h3,
	p {
		margin: 0;
	}

	h3 {
		font-size: 16px;
	}

	.card__eyebrow,
	.card__meta {
		color: var(--arcade-muted-text);
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
	}

	.card__description {
		font-size: 13px;
		line-height: 1.5;
	}

	.card__meta {
		margin-top: auto;
	}
</style>
