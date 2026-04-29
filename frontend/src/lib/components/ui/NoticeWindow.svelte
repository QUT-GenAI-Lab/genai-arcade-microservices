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
	<div class="bg-white px-5.5 py-4.5 text-center bevel-sunken">
		<p class="m-0">{body}</p>
	</div>
</WindowFrame>
