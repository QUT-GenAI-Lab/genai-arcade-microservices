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

		<article class="bg-white px-6 py-4.5 bevel-sunken">
			{#each sections as section, index (section.title)}
				<section class={[index > 0 && 'mt-7', 'space-y-3.5']} id={section.id}>
					<h3 class="m-0 text-xl">{section.title}</h3>

					{#if section.quote}
						<blockquote class="ml-0 border-l-8 border-l-outline-dark pl-3.75 text-sm leading-[1.6]">
							{section.quote}
						</blockquote>
					{/if}

					{#each section.paragraphs as paragraph, index (`${section.title}-${index}`)}
						<p class="text-sm leading-[1.6]">{paragraph}</p>
					{/each}

					{#if section.bullets?.length}
						<ul class="list-disc space-y-2 pl-5 text-sm leading-[1.6]">
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
