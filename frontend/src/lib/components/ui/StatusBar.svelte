<script lang="ts">
	interface Props {
		left: string;
		right: string;
	}

	let { left, right }: Props = $props();
</script>

<div class="status-bar" aria-label="Status">
	<div>{left}</div>
	<div>{right}</div>
</div>

<style>
	.status-bar {
		display: grid;
		gap: 4px;
		grid-template-columns: minmax(0, 220px) minmax(0, 1fr);
		padding: 2px 1px 1px;
	}

	.status-bar div {
		border: 1px solid;
		border-color: #888888 #dadada #dadada #888888;
		overflow: hidden;
		padding: 1px 4px;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	@media (max-width: 700px) {
		.status-bar {
			grid-template-columns: 1fr;
		}
	}
</style>
