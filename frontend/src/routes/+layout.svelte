<script lang="ts">
	import type { Snippet } from 'svelte';
	import './layout.css';
	import favicon from '$lib/assets/images/favicon.ico';

	interface Props {
		children: Snippet;
	}

	let { children }: Props = $props();
</script>

<svelte:head>
	<title>GenAI Arcade</title>
	<meta
		name="description"
		content="Retro GenAI Arcade shell rebuilt in Svelte from the original Jekyll version."
	/>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
