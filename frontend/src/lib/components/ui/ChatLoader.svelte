<script lang="ts">
	import { onMount } from 'svelte';

	const {
		length = 24,
		maxDots = 5,
		interval = 100
	}: {
		length?: number;
		maxDots?: number;
		interval?: number;
	} = $props();
	let currentDotIndex = $state(0);
	let direction = $state<'forward' | 'backward'>('forward');
	// const LENGTH = 24;
	// const MAX_DOTS = 5;

	onMount(() => {
		// Animate a moving "..." effect (e.g., "...  ", " ... ", "  ...", "...  ", etc.) to indicate the model is generating a response.
		const _interval = setInterval(() => {
			// Cycle the dot index forward and backward to create a "ping-pong" effect
			if (direction === 'forward') {
				currentDotIndex += 1;
			} else {
				currentDotIndex -= 1;
			}

			// Reverse direction at the ends
			if (currentDotIndex >= length - maxDots) {
				currentDotIndex = length - maxDots;
				direction = 'backward';
			} else if (currentDotIndex <= 0) {
				currentDotIndex = 0;
				direction = 'forward';
			}
		}, interval);

		return () => clearInterval(_interval);
	});
	const animatedDots = $derived.by(() => {
		return '.'
			.repeat(maxDots)
			.padStart(currentDotIndex + maxDots, ' ')
			.padEnd(length, ' ');
	});
</script>

{animatedDots}
