<script lang="ts">
	import type { HTMLSelectAttributes } from 'svelte/elements';

	interface Option {
		value: string;
		label: string;
	}

	interface Props extends Omit<HTMLSelectAttributes, 'children' | 'value'> {
		value?: string;
		label?: string;
		hint?: string;
		options: Option[];
		className?: string;
	}

	let {
		value = $bindable(''),
		label = '',
		hint = '',
		options = [],
		className = '',
		id,
		disabled = false,
		...props
	}: Props = $props();
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

	<select
		{...props}
		{id}
		{disabled}
		bind:value
		class={[
			'w-full bevel-sunken bg-white px-3 py-2 font-[Tahoma,Geneva,Verdana,sans-serif] text-sm leading-[1.6] text-text',
			'disabled:opacity-[0.72] focus-visible:outline-none'
		]}
	>
		{#each options as option (option.value)}
			<option value={option.value}>{option.label}</option>
		{/each}
	</select>

	{#if hint}
		<p class="m-0 font-[Tahoma,Geneva,Verdana,sans-serif] text-xs leading-6 text-muted-text">
			{hint}
		</p>
	{/if}
</div>
