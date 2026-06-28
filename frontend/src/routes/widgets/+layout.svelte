<script lang="ts">
	import type { Snippet } from 'svelte';
	import { page } from '$app/state';
	import { setTitleContext } from '$lib/components/title/context.svelte';
	import ExplorerTree from '$lib/components/ui/ExplorerTree.svelte';
	import { explorerItems } from '$lib/data/arcade';
	import * as Frame from '$lib/components/ui/frame';
	import * as Dialog from '$lib/components/ui/dialog';
	import Button from '$lib/components/ui/Button.svelte';
	import myComputerIcon from '$lib/assets/images/mycomputer.png';
	import QRCode from 'qrcode';
	import ShareIcon from '$lib/components/ui/icons/ShareIcon.svelte';
	import { SparklesIcon } from '@lucide/svelte';

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
	function onCopy(content: string) {
		navigator.clipboard.writeText(content);
		copied = true;
		setTimeout(() => (copied = false), 2000);
	}

	// Generate a QR code for the embed URL
	const qrCodeDataUrl = $derived.by(async () => {
		try {
			return await QRCode.toDataURL(embedUrl, {
				color: {
					light: '#0000',
					dark: '#111827'
				},
				scale: 6
			});
		} catch (err) {
			console.error('Failed to generate QR code', err);
			return '';
		}
	});

	const BACKEND_STATUS: {
		[key: string]: 'AWS' | 'HuggingFace';
	} = {
		'LinkedIn Generator': 'AWS',
		'Next Token Predictor': 'AWS',
		'LLM Calculator': 'AWS'
	};
</script>

<svelte:head>
	<title>{title}</title>
</svelte:head>

{#snippet widgetHeader(title: string)}
	<Frame.Header {title} icon={myComputerIcon}>
		<div class="flex w-full items-center justify-between">
			<!-- Migration Status -->
			<div>
				{#if BACKEND_STATUS[title] === 'AWS'}
					<SparklesIcon class="size-3" />
				{/if}
			</div>
			<Dialog.Root
				onOpenChange={(open) => {
					console.log('Dialog open state changed:', open);
				}}
			>
				<Dialog.Trigger>
					<Button size="small" variant="secondary">
						<ShareIcon class="size-3" /> Share
					</Button>
				</Dialog.Trigger>
				<Dialog.Content position="center">
					<Dialog.Header title="Share this widget" icon={ShareIcon} />
					<div class="flex flex-col gap-3 p-3">
						<div class="flex flex-col gap-2">
							<p class="text-xs text-gray-700">
								Scan the QR code to use this widget on your mobile device.
							</p>
							<div class="mx-auto size-full bg-white bevel-sunken">
								{#await qrCodeDataUrl}
									<p class="mt-2">Generating QR code...</p>
								{:then url}
									<img src={url} alt="QR Code" class="size-full" />
								{:catch}
									<p class="mt-2 text-red-500">Failed to generate QR code.</p>
								{/await}
							</div>
						</div>
						<div class="flex flex-col gap-2">
							<p class="text-xs text-gray-700">
								Copy the link below to share this widget with others.
							</p>
							<div class="flex items-center gap-2">
								<input
									type="text"
									value={embedUrl}
									readonly
									class="w-full bg-white px-2 py-1 text-xs text-text bevel-sunken"
								/>
								<Button
									size="small"
									variant="secondary"
									onclick={() => onCopy(embedUrl)}
									class="px-2 py-1 whitespace-nowrap"
								>
									{#if copied}
										Copied!
									{:else}
										Copy Link
									{/if}
								</Button>
							</div>
						</div>
					</div>
				</Dialog.Content>
			</Dialog.Root>
		</div>
	</Frame.Header>
{/snippet}

{#if !isEmbedded}
	<div class="mx-auto mt-8 grid max-w-4xl grid-cols-[minmax(0,220px)_minmax(0,1fr)]">
		<Frame.Root class="size-full">
			<Frame.Header title="GenAI Arcade" />
			<Frame.Body>
				<ExplorerTree items={explorerItems} />
			</Frame.Body>
		</Frame.Root>
		<Frame.Root class="size-full">
			{@render widgetHeader(title)}
			<Frame.Body>
				<div class="bg-white bevel-sunken">
					{@render children()}
				</div>
			</Frame.Body>
		</Frame.Root>
	</div>
	<div>
		<Frame.Root class="mx-auto mt-8 max-w-4xl">
			<Frame.Header title="Embed This Widget" />
			<Frame.Body>
				<div class="bg-gray-100 p-2 text-sm text-gray-700">
					<div class="items-centre flex justify-between">
						<p>Copy and paste the following code to embed this widget on your site.</p>
						<Button variant="secondary" onclick={() => onCopy(embedCode)}>
							{#if copied}
								Copied!
							{:else}
								Copy Code
							{/if}
						</Button>
					</div>
					<pre class="mt-2 overflow-x-auto rounded bg-white p-2"><code>{embedCode}</code></pre>
				</div>
			</Frame.Body>
		</Frame.Root>
	</div>
{/if}

{#if isEmbedded}
	<Frame.Root class="size-full">
		{@render widgetHeader(title)}
		<Frame.Body>
			<div class="bg-white bevel-sunken">
				{@render children()}
			</div>
		</Frame.Body>
	</Frame.Root>
{/if}
