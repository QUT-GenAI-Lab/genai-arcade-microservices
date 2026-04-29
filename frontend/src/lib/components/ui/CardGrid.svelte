<script lang="ts">
	import type { CardItem } from '$lib/data/arcade';
	import { jumpToFragment } from '$lib/navigation';

	interface Props {
		items: CardItem[];
	}

	let { items }: Props = $props();
</script>

<div class="grid [grid-template-columns:repeat(auto-fit,minmax(220px,1fr))] gap-3">
	{#each items as item (item.title)}
		{#if item.external}
			<a
				class="flex min-h-37.5 flex-col gap-2.5 bg-white p-3.5 text-left text-text no-underline bevel-sunken hover:bg-[#f5f1ff] hover:outline-2 hover:outline-offset-2 hover:outline-primary focus-visible:bg-[#f5f1ff] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
				href={item.href}
				target="_blank"
				rel="external noreferrer"
			>
				<div class="flex items-start gap-2.5">
					<img class="mt-0.75 h-4.5 w-4.5" src={item.icon} alt="" />
					<div>
						{#if item.eyebrow}
							<p class="m-0 text-[11px] font-bold text-muted-text uppercase">
								{item.eyebrow}
							</p>
						{/if}
						<h3 class="m-0 text-base">{item.title}</h3>
					</div>
				</div>

				<p class="m-0 text-[13px] leading-6">{item.description}</p>

				{#if item.meta}
					<p class="mt-auto text-[11px] font-bold text-muted-text uppercase">
						{item.meta}
					</p>
				{/if}
			</a>
		{:else}
			<button
				class="flex min-h-37.5 cursor-pointer flex-col gap-2.5 bg-white p-3.5 text-left text-text bevel-sunken hover:bg-[#f5f1ff] hover:outline-2 hover:outline-offset-2 hover:outline-primary focus-visible:bg-[#f5f1ff] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
				type="button"
				onclick={() => jumpToFragment(item.href)}
			>
				<div class="flex items-start gap-2.5">
					<img class="mt-0.75 h-4.5 w-4.5" src={item.icon} alt="" />
					<div>
						{#if item.eyebrow}
							<p class="m-0 text-[11px] font-bold text-muted-text uppercase">
								{item.eyebrow}
							</p>
						{/if}
						<h3 class="m-0 text-base">{item.title}</h3>
					</div>
				</div>

				<p class="m-0 text-[13px] leading-6">{item.description}</p>

				{#if item.meta}
					<p class="mt-auto text-[11px] font-bold text-muted-text uppercase">
						{item.meta}
					</p>
				{/if}
			</button>
		{/if}
	{/each}
</div>
