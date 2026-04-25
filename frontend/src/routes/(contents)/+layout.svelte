<script lang="ts">
	import type { Snippet } from 'svelte';
	import './layout.css';
	import ExplorerTree from '$lib/components/ui/ExplorerTree.svelte';
	import SiteFooter from '$lib/components/ui/SiteFooter.svelte';
	import StatusBar from '$lib/components/ui/StatusBar.svelte';
	import WindowFrame from '$lib/components/ui/WindowFrame.svelte';
	import {
		explorerItems,
		explorerStatus,
		footerContacts,
		footerCredit,
		footerLicenses
	} from '$lib/data/arcade';

	import myComputerIcon from '$lib/assets/images/mycomputer.png';

	interface Props {
		children: Snippet;
	}

	let { children }: Props = $props();
</script>

<div class="arcade-page" id="top">
	<div class="arcade-page__stack">
		<WindowFrame title="GenAI Arcade" icon={myComputerIcon} class="arcade-page__window">
			<div class="explorer-shell">
				<ExplorerTree items={explorerItems} />

				<div class="explorer-shell__cards" id="sections"></div>
			</div>

			<StatusBar left={explorerStatus.left} right={explorerStatus.right} />
		</WindowFrame>

		<WindowFrame title="Content" class="arcade-page__window">
			<div class="page-content">
				{@render children()}
			</div>
		</WindowFrame>

		<SiteFooter contacts={footerContacts} licenses={footerLicenses} credit={footerCredit} />
	</div>
</div>

<style>
	.arcade-page {
		padding: 20px 16px 32px;
	}

	.arcade-page__stack {
		display: grid;
		gap: 18px;
		margin: 0 auto;
		max-width: 800px;
	}

	:global(.arcade-page__window) {
		width: 100%;
	}

	.explorer-shell {
		display: grid;
		gap: 6px;
		grid-template-columns: minmax(220px, 28%) minmax(0, 1fr);
	}

	.explorer-shell__cards {
		background: var(--arcade-surface);
		border: 2px solid;
		border-color: var(--arcade-window-shadow) var(--arcade-outline-light)
			var(--arcade-outline-light) var(--arcade-window-shadow);
		max-height: 24rem;
		overflow: auto;
		padding: 10px;
	}

	.page-content {
		background: var(--arcade-surface);
		border: 2px solid;
		border-color: var(--arcade-window-shadow) var(--arcade-outline-light)
			var(--arcade-outline-light) var(--arcade-window-shadow);
		padding: 0.5rem;
	}

	@media (max-width: 760px) {
		.explorer-shell {
			grid-template-columns: 1fr;
		}
	}
</style>
