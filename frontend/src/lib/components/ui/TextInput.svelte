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

<div class={['grid gap-2', className]}>
	{#if label}
		<label
			class="font-[Tahoma,Geneva,Verdana,sans-serif] text-xs font-bold tracking-[0.04em] uppercase"
			for={id}
		>
			{label}
		</label>
	{/if}

	<div
		class={[
			'relative bevel-sunken bg-white focus-within:bevel-sunken focus-within:bg-white',
			disabled && 'opacity-[0.72]'
		]}
	>
		{#if suggestionSuffix}
			{@const cleanedSuggestion = suggestionSuffix.trimStart()}
			<div
				class="pointer-events-none absolute inset-0 z-0 overflow-hidden px-3.5 py-3 font-[Tahoma,Geneva,Verdana,sans-serif] text-sm leading-[1.6] break-words whitespace-pre-wrap text-text"
				aria-hidden="true"
			>
				<div class="min-h-full" style:transform={`translate(${-overlayLeft}px, ${-overlayTop}px)`}>
					<span>{value}</span>
					<span class="text-muted-text">{cleanedSuggestion}</span>
				</div>
			</div>
		{/if}

		<textarea
			{...props}
			{id}
			{rows}
			{disabled}
			bind:value
			class="relative z-[1] min-h-44 w-full resize-y border-0 bg-transparent px-3.5 py-3 font-[Tahoma,Geneva,Verdana,sans-serif] text-sm leading-[1.6] text-text placeholder:text-muted-text placeholder:opacity-100 focus-visible:outline-none"
			onkeydown={handleKeydown}
			onscroll={handleScroll}
		></textarea>
	</div>

	{#if hintText}
		<p
			class="m-0 font-[Tahoma,Geneva,Verdana,sans-serif] text-xs leading-6 text-muted-text"
		>
			{hintText}
		</p>
	{/if}
</div>
