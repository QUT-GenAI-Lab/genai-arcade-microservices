<script lang="ts">
	import WindowFrame from './WindowFrame.svelte';

	interface Props {
		title: string;
		body: string;
		icon: string;
	}

	let { title, body, icon }: Props = $props();
</script>

<WindowFrame {title} {icon}>
	<div class="notice">
		<p>{body}</p>
	</div>
</WindowFrame>

<style>
	.notice {
		background: var(--arcade-surface);
		border: 2px solid;
		border-color: var(--arcade-window-shadow) var(--arcade-outline-light)
			var(--arcade-outline-light) var(--arcade-window-shadow);
		padding: 18px 22px;
		text-align: center;
	}

	p {
		margin: 0;
	}
</style>
