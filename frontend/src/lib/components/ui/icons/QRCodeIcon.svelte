<script lang="ts">
	const { size = 16, class: className = '' } = $props();
</script>

<svg
	width={size}
	height={size}
	viewBox="0 0 24 24"
	fill="none"
	stroke="currentColor"
	stroke-width="2"
	class={className}
	aria-hidden="true"
	role="img"
>
	<rect width="8" height="8" x="3" y="3" />
	<rect width="8" height="8" x="16" y="3" />
	<rect width="8" height="8" x="3" y="16" />
	<path d="M16 16h2v2h-2z" />
	<path d="M20 16h2v2h-2z" />
	<path d="M16 20h2v2h-2z" />
	<path d="M20 20h2v2h-2z" />
</svg>
