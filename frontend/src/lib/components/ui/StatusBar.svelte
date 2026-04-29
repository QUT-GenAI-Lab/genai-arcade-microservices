<script lang="ts">
	interface Props {
		left: string;
		right: string;
	}

	let { left, right }: Props = $props();
</script>

<div
	class="grid [grid-template-columns:minmax(0,220px)_minmax(0,1fr)] gap-1 px-px pt-0.5 pb-px max-[700px]:grid-cols-1"
	aria-label="Status"
>
	<div
		class="overflow-hidden border border-t-[#888888] border-r-[#dadada] border-b-[#dadada] border-l-[#888888] px-1 py-px text-ellipsis whitespace-nowrap"
	>
		{left}
	</div>
	<div
		class="overflow-hidden border border-t-[#888888] border-r-[#dadada] border-b-[#dadada] border-l-[#888888] px-1 py-px text-ellipsis whitespace-nowrap"
	>
		{right}
	</div>
</div>
