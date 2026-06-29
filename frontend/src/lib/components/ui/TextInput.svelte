<script lang="ts">
	import type { HTMLTextareaAttributes } from 'svelte/elements';
	import { twMerge } from 'tailwind-merge';

	interface Props extends Omit<HTMLTextareaAttributes, 'children' | 'value'> {
		value?: string;
		prediction?: string | null;
		label?: string;
		hint?: string;
		class?: string;
		ref?: HTMLTextAreaElement;
		onEnter?: (event: KeyboardEvent) => void;
	}

	let {
		value = $bindable(''),
		ref = $bindable<HTMLTextAreaElement>(),
		prediction = null,
		label = '',
		hint = '',
		class: className = '',
		id,
		rows = 8,
		disabled = false,
		onEnter,
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
			hints.push(`Press Tab to accept suggestion: "${suggestionSuffix.trimStart()}"`);
		}

		return hints.filter(Boolean).join(' ');
	});

	function handleScroll(event: Event) {
		const target = event.currentTarget as HTMLTextAreaElement;
		overlayTop = target.scrollTop;
		overlayLeft = target.scrollLeft;
	}

	function acceptSuggestion() {
		if (!suggestionSuffix || suggestionCoolingDown) {
			return;
		}

		value = `${value}${suggestionSuffix}`;
		suggestionCoolingDown = true;

		if (cooldownTimeout) {
			clearTimeout(cooldownTimeout);
		}

		cooldownTimeout = setTimeout(() => {
			suggestionCoolingDown = false;
		}, 450);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Tab' && suggestionSuffix && !disabled) {
			event.preventDefault();
			acceptSuggestion();
		}
		if (event.key === 'Enter' && onEnter) {
			event.preventDefault();
			onEnter(event);
		}
	}
</script>

<div class="grid flex-1 gap-2">
	{#if label}
		<label
			class="font-[Tahoma,Geneva,Verdana,sans-serif] text-xs font-bold tracking-[0.04em] uppercase"
			for={id}
		>
			{label}
		</label>
	{/if}

	<div class="relative">
		{#if suggestionSuffix}
			{@const cleanedSuggestion = suggestionSuffix}
			<div
				class="pointer-events-none absolute inset-0 z-20 overflow-hidden px-3.5 py-3 font-[Tahoma,Geneva,Verdana,sans-serif] text-sm leading-[1.6] break-words whitespace-pre-wrap text-transparent"
				aria-hidden="true"
			>
				<div class="min-h-full" style:transform={`translate(${-overlayLeft}px, ${-overlayTop}px)`}>
					<span>{value}</span><button
						class="pointer-events-auto cursor-pointer text-muted-text"
						onclick={acceptSuggestion}>{cleanedSuggestion}</button
					>
				</div>
			</div>
		{/if}

		<textarea
			{...props}
			{id}
			{rows}
			{disabled}
			bind:value
			bind:this={ref}
			class={twMerge(
				'relative z-10 block w-full resize-y border-0 bg-white px-3.5 py-3 font-[Tahoma,Geneva,Verdana,sans-serif] text-sm leading-[1.6] text-text bevel-sunken placeholder:text-muted-text placeholder:opacity-100 focus-within:bg-white focus-within:bevel-sunken focus-visible:outline-none',
				disabled && 'opacity-[0.72]',
				className
			)}
			onkeydown={handleKeydown}
			onscroll={handleScroll}
		></textarea>
	</div>

	{#if hintText}
		<p class="z-10 m-0 font-[Tahoma,Geneva,Verdana,sans-serif] text-xs leading-6 text-muted-text">
			{hintText}
		</p>
	{/if}
</div>
