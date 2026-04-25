<script lang="ts">
	import type { HTMLTextareaAttributes } from 'svelte/elements';

	interface Props extends Omit<HTMLTextareaAttributes, 'children' | 'value'> {
		value?: string;
		prediction?: string | null;
		label?: string;
		hint?: string;
		className?: string;
	}

	let {
		value = $bindable(''),
		prediction = null,
		label = '',
		hint = '',
		className = '',
		id,
		rows = 8,
		disabled = false,
		...props
	}: Props = $props();

	let overlayTop = $state(0);
	let overlayLeft = $state(0);
	let suggestionCoolingDown = $state(false);
	let cooldownTimeout: ReturnType<typeof setTimeout> | null = null;

	let suggestionSuffix = $derived.by(() => {
		if (!prediction || prediction === value || suggestionCoolingDown) {
			return '';
		}

		return prediction.startsWith(value) ? prediction.slice(value.length) : prediction;
	});

	let hintText = $derived.by(() => {
		const hints = [hint];

		if (suggestionSuffix) {
			hints.push('Press Tab to accept suggestion.');
		}

		return hints.filter(Boolean).join(' ');
	});

	function handleScroll(event: Event) {
		const target = event.currentTarget as HTMLTextAreaElement;
		overlayTop = target.scrollTop;
		overlayLeft = target.scrollLeft;
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key !== 'Tab' || !prediction || !suggestionSuffix || disabled) {
			return;
		}

		event.preventDefault();
		const target = event.currentTarget as HTMLTextAreaElement;
		const nextValue = prediction.startsWith(value) ? prediction : `${value}${prediction}`;
		value = nextValue;
		suggestionCoolingDown = true;

		if (cooldownTimeout) {
			clearTimeout(cooldownTimeout);
		}

		cooldownTimeout = setTimeout(() => {
			suggestionCoolingDown = false;
		}, 450);

		requestAnimationFrame(() => {
			target.focus();
			target.setSelectionRange(nextValue.length, nextValue.length);
		});
	}
</script>

<div class={['text-input', className]}>
	{#if label}
		<label class="text-input__label" for={id}>{label}</label>
	{/if}

	<div class={['text-input__field', disabled && 'text-input__field--disabled']}>
		{#if suggestionSuffix}
			{@const cleanedSuggestion = suggestionSuffix.trimStart()}
			<div class="text-input__overlay" aria-hidden="true">
				<div
					class="text-input__overlay-copy"
					style:transform={`translate(${-overlayLeft}px, ${-overlayTop}px)`}
				>
					<span>{value}</span>
					<span class="text-input__suggestion">{cleanedSuggestion}</span>
				</div>
			</div>
		{/if}

		<textarea
			{...props}
			{id}
			{rows}
			{disabled}
			bind:value
			class="text-input__control"
			onkeydown={handleKeydown}
			onscroll={handleScroll}
		></textarea>
	</div>

	{#if hintText}
		<p class="text-input__hint">{hintText}</p>
	{/if}
</div>

<style>
	.text-input {
		display: grid;
		gap: 8px;
	}

	.text-input__label,
	.text-input__hint {
		font-family: Tahoma, Geneva, Verdana, sans-serif;
	}

	.text-input__label {
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.04em;
		text-transform: uppercase;
	}

	.text-input__field {
		background: var(--arcade-surface);
		border: 2px solid;
		border-color: var(--arcade-window-shadow) var(--arcade-outline-light)
			var(--arcade-outline-light) var(--arcade-window-shadow);
		position: relative;
	}

	.text-input__field:focus-within {
		border-color: var(--arcade-outline-dark) var(--arcade-outline-light) var(--arcade-outline-light)
			var(--arcade-outline-dark);
	}

	.text-input__field--disabled {
		opacity: 0.72;
	}

	.text-input__overlay,
	.text-input__control {
		font-family: Tahoma, Geneva, Verdana, sans-serif;
		font-size: 14px;
		line-height: 1.6;
		padding: 12px 14px;
	}

	.text-input__overlay {
		color: var(--arcade-text);
		inset: 0;
		overflow: hidden;
		pointer-events: none;
		position: absolute;
		white-space: pre-wrap;
		word-break: break-word;
		z-index: 0;
	}

	.text-input__overlay-copy {
		min-height: 100%;
	}

	.text-input__suggestion {
		color: var(--arcade-muted-text);
	}

	.text-input__control {
		background: transparent;
		border: 0;
		color: var(--arcade-text);
		min-height: 11rem;
		position: relative;
		resize: vertical;
		width: 100%;
		z-index: 1;
	}

	.text-input__control::placeholder {
		color: var(--arcade-muted-text);
		opacity: 1;
	}

	.text-input__control:focus-visible {
		outline: none;
	}

	.text-input__hint {
		color: var(--arcade-muted-text);
		font-size: 12px;
		line-height: 1.5;
		margin: 0;
	}
</style>
