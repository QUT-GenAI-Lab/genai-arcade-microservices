<script lang="ts">
	import type { Snippet } from 'svelte';
	import { page } from '$app/state';
	import { setTitleContext } from '$lib/components/title/context.svelte';
	import Widget from '$lib/widgets/widget.svelte';
	import ExplorerTree from '$lib/components/ui/ExplorerTree.svelte';
	import { explorerItems } from '$lib/data/arcade';
	import WindowFrame from '$lib/components/ui/WindowFrame.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		children: Snippet;
	}

	let { children }: Props = $props();

	// Get the embed=true query parameter to determine if the page is being embedded in an iframe
	const urlParams = page.url.searchParams;
	const isEmbedded = $derived(urlParams.get('embed') === 'true');
	const context = setTitleContext();
	const title = $derived(context.title ?? 'GenAI Arcade');

	const embedUrl = $derived.by(() => {
		const url = new URL(page.url);
		url.searchParams.set('embed', 'true');
		return url.toString();
	});
	const embedCode = $derived(
		`<iframe 
	src="${embedUrl}" 
	title="${title}" 
	style="border:0;width:100%;height:400px;"
></iframe>`.trim()
	);

	let copied = $state(false);
	function onCopy() {
		navigator.clipboard.writeText(embedCode);
		copied = true;
		setTimeout(() => (copied = false), 2000);
	}
</script>

<svelte:head>
	<title>{title}</title>
</svelte:head>

{#if !isEmbedded}
	<div class="mx-auto mt-8 grid max-w-4xl grid-cols-[minmax(0,220px)_minmax(0,1fr)]">
		<WindowFrame title="GenAI Arcade" class="size-full">
			<ExplorerTree items={explorerItems} />
		</WindowFrame>
		<Widget {title}>
			{@render children()}
		</Widget>
	</div>
	<div>
		<WindowFrame title="Embed This Widget" class="mx-auto mt-8 max-w-4xl">
			<div class="bg-gray-100 p-2 text-sm text-gray-700">
				<div class="items-centre flex justify-between">
					<p>Copy and paste the following code to embed this widget on your site.</p>
					<Button variant="secondary" onclick={onCopy}>
						{#if copied}
							Copied!
						{:else}
							Copy Code
						{/if}
					</Button>
				</div>
				<pre class="mt-2 overflow-x-auto rounded bg-white p-2"><code>{embedCode}</code></pre>
			</div>
		</WindowFrame>
	</div>
{/if}

{#if isEmbedded}
	<Widget {title}>
		{@render children()}
	</Widget>
{/if}
