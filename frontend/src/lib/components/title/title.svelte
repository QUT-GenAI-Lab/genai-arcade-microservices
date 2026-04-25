<script lang="ts">
	import { onMount } from 'svelte';
	import { getTitleContext } from './context.svelte';

	interface Props {
		value: string;
	}

	let { value }: Props = $props();

	const context = getTitleContext();
	onMount(() => {
		context.setTitle(value);
	});
</script>
