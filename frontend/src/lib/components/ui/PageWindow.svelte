<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { MenuItem, PageSection, PagerLink, WindowControl } from '$lib/data/arcade';
	import MenuBar from './MenuBar.svelte';
	import SectionPager from './SectionPager.svelte';
	import WindowFrame from './WindowFrame.svelte';

	interface Props {
		id: string;
		title: string;
		icon: string;
		menuItems: MenuItem[];
		sections: PageSection[];
		previous: PagerLink | null;
		next: PagerLink | null;
		children?: Snippet;
	}

	let { id, title, icon, menuItems, sections, previous, next, children }: Props = $props();

	let controls = $derived<WindowControl[]>([
		{ symbol: '×', label: 'Back to top', href: '#top' },
		{ symbol: '□', label: 'Previous section', href: previous?.href, disabled: !previous },
		{ symbol: '–', label: 'Next section', href: next?.href, disabled: !next }
	]);
</script>

<section class="page-window" {id}>
	<WindowFrame {title} {icon} {controls}>
		<MenuBar items={menuItems} />

		<article class="page-window__content">
			{#each sections as section (section.title)}
				<section class="page-window__section" id={section.id}>
					<h3>{section.title}</h3>

					{#if section.quote}
						<blockquote>{section.quote}</blockquote>
					{/if}

					{#each section.paragraphs as paragraph, index (`${section.title}-${index}`)}
						<p>{paragraph}</p>
					{/each}

					{#if section.bullets?.length}
						<ul>
							{#each section.bullets as bullet, index (`${section.title}-bullet-${index}`)}
								<li>{bullet}</li>
							{/each}
						</ul>
					{/if}
				</section>
			{/each}

			{@render children?.()}

			<SectionPager {previous} {next} />
		</article>
	</WindowFrame>
</section>

<style>
	.page-window__content {
		background: var(--arcade-surface);
		border: 2px solid;
		border-color: var(--arcade-window-shadow) var(--arcade-outline-light)
			var(--arcade-outline-light) var(--arcade-window-shadow);
		padding: 18px 24px;
	}

	.page-window__section + .page-window__section {
		margin-top: 28px;
	}

	h3 {
		font-size: 20px;
		margin: 0 0 12px;
	}

	p,
	li,
	blockquote {
		font-size: 14px;
		line-height: 1.6;
	}

	p,
	blockquote,
	ul {
		margin: 0 0 14px;
	}

	blockquote {
		border-left: 8px solid var(--arcade-outline-dark);
		margin-left: 0;
		padding-left: 15px;
	}

	ul {
		padding-left: 20px;
	}

	li + li {
		margin-top: 8px;
	}
</style>
