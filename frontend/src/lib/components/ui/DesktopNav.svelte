<script lang="ts">
	import type { DesktopNavItem } from '$lib/data/arcade';
	import { jumpToFragment } from '$lib/navigation';

	interface Props {
		items: DesktopNavItem[];
	}

	let { items }: Props = $props();
</script>

<nav class="desktop-nav" aria-label="Primary page navigation">
	{#each items as item (item.label)}
		<button class:compact={item.compact} type="button" onclick={() => jumpToFragment(item.href)}>
			<div class="desktop-nav__button">
				<span class="desktop-nav__icon" aria-hidden="true">{item.icon}</span>
				<span class="desktop-nav__label">{item.label}</span>
			</div>
		</button>
	{/each}
</nav>

<style>
	.desktop-nav {
		display: flex;
		gap: 4px;
	}

	button {
		background: transparent;
		border: 0;
		color: inherit;
		display: block;
		flex: 1 1 0;
		padding: 0;
	}

	.compact {
		flex: 0 0 156px;
	}

	.desktop-nav__button {
		align-items: center;
		background: var(--arcade-surface-variant);
		border: 2px solid;
		border-color: var(--arcade-outline-light) var(--arcade-outline-dark) var(--arcade-outline-dark)
			var(--arcade-outline-light);
		color: var(--arcade-text);
		display: flex;
		flex-direction: column;
		gap: 2px;
		height: 44px;
		justify-content: center;
		padding: 0 10px;
		text-align: center;
		width: 100%;
	}

	.desktop-nav__icon {
		font-size: 18px;
		line-height: 1;
	}

	.desktop-nav__label {
		font-size: 10px;
		font-weight: 700;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		width: 100%;
	}

	button:hover .desktop-nav__button,
	button:focus-visible .desktop-nav__button {
		border-color: var(--arcade-outline-dark) var(--arcade-outline-light) var(--arcade-outline-light)
			var(--arcade-outline-dark);
		outline: none;
	}

	@media (max-width: 640px) {
		.desktop-nav {
			flex-direction: column;
		}

		.compact {
			flex-basis: auto;
		}
	}
</style>
