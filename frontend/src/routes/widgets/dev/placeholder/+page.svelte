<script module>
	export const title = 'Unavailable';
</script>

<script lang="ts">
	import Title from '$lib/components/title/title.svelte';
	import { ConstructionIcon, ClockIcon } from '@lucide/svelte';
</script>

<Title value="Unavailable" />

<div
	class="flex flex-col items-center justify-center gap-5 bg-surface-variant p-6 text-center font-[Tahoma,Geneva,Verdana,sans-serif] text-text"
>
	<div class="flex size-16 items-center justify-center bg-surface bevel-raised-thin">
		<ConstructionIcon class="size-8 text-primary" />
	</div>

	<div class="flex flex-col items-center gap-2">
		<h2 class="m-0 text-base font-bold">Widget Unavailable</h2>
		<p class="m-0 max-w-[42ch] text-sm leading-6">
			This widget is unavailable at the moment for development. Please visit later.
		</p>
	</div>

	<div class="flex items-center gap-1.5 text-xs text-muted-text">
		<ClockIcon class="size-3.5" />
		<span>Check back soon</span>
	</div>
</div>
