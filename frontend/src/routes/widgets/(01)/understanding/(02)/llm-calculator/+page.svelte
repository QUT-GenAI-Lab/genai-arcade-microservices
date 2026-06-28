<script module>
	export const title = 'LLM Calculator';
	export const widgetUrl = '/llm-calculator';
</script>

<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
	import Title from '$lib/components/title/title.svelte';
	import { WidgetBackend } from '$lib/widgets/widget-backend.svelte';
	import { CalculateResponseSchema } from '$lib/widgets/schemas';
	import { onMount } from 'svelte';

	type Operation = '+' | '-' | '*' | '/';

	const backend = new WidgetBackend(`${widgetUrl}`);

	const EXAMPLES = [
		{
			label: 'Addition',
			left: '42917',
			operation: '+',
			right: '83056'
		},
		{
			label: 'Subtraction',
			left: '904215',
			operation: '-',
			right: '276384'
		},
		{
			label: 'Multiplication',
			left: '5821',
			operation: '*',
			right: '7493'
		},
		{
			label: 'Division',
			left: '84726315',
			operation: '/',
			right: '3192'
		},
		{
			label: 'Decimal operation',
			left: '419.72',
			operation: '*',
			right: '8.36'
		}
	] satisfies Array<{ label: string; left: string; operation: Operation; right: string }>;

	function getErrorMessage(error: unknown): string {
		return error instanceof Error ? error.message : 'Unknown error';
	}

	function formatNumber(value: number): string {
		if (!Number.isFinite(value)) {
			return 'Error';
		}

		const normalized = Object.is(value, -0) ? 0 : value;
		return Number.isInteger(normalized)
			? normalized.toString()
			: normalized.toLocaleString('en-US', {
					maximumFractionDigits: 12,
					useGrouping: false
				});
	}

	function sanitizeNumericInput(value: string): string {
		return value.replace(/[^0-9.-]/g, '');
	}

	function normalizeOperand(value: string): string {
		if (!value || value === '-' || value === '.' || value === '-.') {
			return '0';
		}

		return value;
	}

	function appendDigit(value: string, digit: string): string {
		if (digit === '.') {
			if (value.includes('.')) {
				return value;
			}

			if (!value || value === '-') {
				return `${value}0.`;
			}
		}

		if (digit === '-' && value) {
			return value;
		}

		if (value === '0' && digit !== '.') {
			return digit;
		}

		if (value === '-0' && digit !== '.') {
			return `-${digit}`;
		}

		return `${value}${digit}`;
	}

	function computeCorrectResult(left: number, operation: Operation, right: number): number {
		switch (operation) {
			case '+':
				return left + right;
			case '-':
				return left - right;
			case '*':
				return left * right;
			case '/':
				return left / right;
		}
	}

	let computing = $state(false);
	let connecting = $state(false);
	let leftOperand = $state('');
	let rightOperand = $state('');
	let operation = $state<Operation | null>(null);
	let mainDisplay = $state('0');
	let error = $state<string | null>(null);
	let lastEquation = $state<{
		left: string;
		operation: Operation;
		right: string;
		correct: string;
	} | null>(null);
	let requestId = $state(0);

	let modelStatus = $derived.by(() => {
		if (connecting) return 'Checking';
		if (computing) return 'Calculating';
		if (backend.status === 'Ready') return 'Ready';
		if (backend.status === 'Pending') return 'Pending';
		if (backend.status === 'Error') return 'Error';
		return 'Unknown';
	});

	let currentExpression = $derived.by(() => {
		if (operation) {
			return `${leftOperand || '0'} ${operation} ${rightOperand || ''}`.trim();
		}

		return leftOperand || '0';
	});

	let secondaryLabel = $derived(lastEquation ? 'Correct value' : 'Preview');
	let secondaryDisplay = $derived.by(() => {
		if (lastEquation) {
			return `${lastEquation.left} ${lastEquation.operation} ${lastEquation.right} = ${lastEquation.correct}`;
		}

		return currentExpression;
	});

	const sectionMetaClass = 'text-xs text-muted-text';
	const displayLabelClass = 'mb-1 text-xs font-bold';
	const displayBaseClass =
		'overflow-hidden bevel-sunken-thin bg-white px-2 py-1.5 text-right font-[Courier_New,Courier,monospace] text-ellipsis whitespace-nowrap';
	const keypadButtonClass =
		'min-h-9 cursor-pointer bevel-raised bg-surface-variant font-[Tahoma,Geneva,Verdana,sans-serif] text-[13px] font-bold text-text hover:bevel-sunken focus-visible:bevel-sunken focus-visible:outline-none disabled:cursor-default disabled:text-muted-text disabled:hover:bevel-raised disabled:focus-visible:bevel-raised';
	const noticeClass = 'bevel-raised-thin bg-surface-variant px-2.5 py-2 text-xs leading-6';
	const exampleButtonClass = 'min-h-7.5 px-2.5 py-1.25 text-[11px]';

	function clearAll() {
		requestId += 1;
		leftOperand = '';
		rightOperand = '';
		operation = null;
		mainDisplay = '0';
		error = null;
		computing = false;
	}

	function backspace() {
		if (computing) {
			return;
		}

		error = null;

		if (operation === null) {
			leftOperand = leftOperand.slice(0, -1);
			mainDisplay = leftOperand || '0';
			return;
		}

		if (rightOperand) {
			rightOperand = rightOperand.slice(0, -1);
			mainDisplay = rightOperand
				? `${leftOperand || '0'} ${operation} ${rightOperand}`
				: `${leftOperand || '0'} ${operation}`;
			return;
		}

		operation = null;
		mainDisplay = leftOperand || '0';
	}

	function handleNum(digit: string) {
		if (computing) {
			return;
		}

		error = null;

		if (operation === null) {
			leftOperand = appendDigit(leftOperand, digit);
			mainDisplay = leftOperand;
			return;
		}

		rightOperand = appendDigit(rightOperand, digit);
		mainDisplay = `${leftOperand || '0'} ${operation} ${rightOperand}`;
	}

	function handleOperation(nextOperation: Operation) {
		if (computing) {
			return;
		}

		error = null;

		if (!leftOperand) {
			leftOperand = '0';
		}

		if (operation && rightOperand) {
			void calculate(nextOperation);
			return;
		}

		operation = nextOperation;
		mainDisplay = `${leftOperand} ${operation}`;
	}

	async function calculate(nextOperation: Operation | null = null) {
		if (computing) {
			return;
		}

		if (!operation) {
			mainDisplay = leftOperand || '0';
			return;
		}

		const normalizedLeft = normalizeOperand(leftOperand);
		const normalizedRight = normalizeOperand(rightOperand);
		const left = Number.parseFloat(normalizedLeft);
		const right = Number.parseFloat(normalizedRight);

		if (Number.isNaN(left) || Number.isNaN(right)) {
			error = 'Enter valid numbers before calculating.';
			return;
		}

		if (operation === '/' && right === 0) {
			error = 'Division by zero is not allowed.';
			return;
		}

		const activeOperation = operation;
		const activeRequestId = ++requestId;
		computing = true;
		error = null;
		mainDisplay = 'Calculating...';

		try {
			const { data, error: parseError } = await backend.post(
				'/calculate',
				{
					left_num: left,
					operation: activeOperation,
					right_num: right
				},
				{ schema: CalculateResponseSchema }
			);

			if (activeRequestId !== requestId) {
				return;
			}

			if (parseError || data === undefined || data === null) {
				throw parseError ?? new Error('Failed to parse calculation result');
			}

			const llmResult = data;
			const correctResult = formatNumber(computeCorrectResult(left, activeOperation, right));

			mainDisplay = llmResult;
			lastEquation = {
				left: normalizedLeft,
				operation: activeOperation,
				right: normalizedRight,
				correct: correctResult
			};
			leftOperand = sanitizeNumericInput(llmResult);
			rightOperand = '';
			operation = nextOperation;

			if (operation) {
				mainDisplay = `${leftOperand || llmResult} ${operation}`;
			}
		} catch (errorValue) {
			if (activeRequestId !== requestId) {
				return;
			}

			mainDisplay = `${normalizedLeft} ${activeOperation} ${normalizedRight}`;
			error = `Calculation failed: ${getErrorMessage(errorValue)}`;
		} finally {
			if (activeRequestId === requestId) {
				computing = false;
			}
		}
	}

	function loadExample(example: { left: string; operation: Operation; right: string }) {
		leftOperand = example.left;
		operation = example.operation;
		rightOperand = example.right;
		void calculate();
	}

	async function reconnectModel() {
		connecting = true;
		await backend.healthCheck();
		connecting = false;
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) {
			return;
		}

		const key = event.key;

		if (/^[0-9]$/.test(key) || key === '.') {
			event.preventDefault();
			handleNum(key);
			return;
		}

		if (key === '+' || key === '-' || key === '*' || key === '/') {
			event.preventDefault();
			handleOperation(key);
			return;
		}

		if (key === 'Enter' || key === '=') {
			event.preventDefault();
			void calculate();
			return;
		}

		if (key === 'Escape' || key.toLowerCase() === 'c') {
			event.preventDefault();
			clearAll();
			return;
		}

		if (key === 'Backspace') {
			event.preventDefault();
			backspace();
		}
	}

	onMount(() => {
		void backend.healthCheck();
	});
</script>

<svelte:window onkeydown={handleKeydown} />

<Title value="LLM Calculator" />

<div class="bg-surface-variant p-3" aria-live="polite">
	<div class="grid gap-6 md:grid-cols-2">
		<div>
			<p class={['mb-2', sectionMetaClass]}>
				Type or use the keypad to enter an equation. Press '=' to see the correct result and the
				model's answer.
			</p>
			<div>
				<div class={displayLabelClass}>{secondaryLabel}</div>
				<div class={[displayBaseClass, 'min-h-5 text-xs']}>{secondaryDisplay}</div>
			</div>

			<div class="mt-2">
				<div class={[displayLabelClass, 'flex items-center justify-between']}>
					LLM output
					<span class={sectionMetaClass}>Model: {modelStatus}</span>
				</div>
				<div
					class={[
						displayBaseClass,
						'min-h-10.5 text-2xl font-bold',
						computing && 'text-muted-text'
					]}
				>
					{mainDisplay}
				</div>
			</div>

			<div class="mt-3 flex flex-wrap gap-2">
				<Button variant="secondary" onclick={reconnectModel} disabled={connecting}>
					{connecting ? 'Checking...' : 'Reconnect model'}
				</Button>
			</div>

			<div class="mt-3 grid grid-cols-4 gap-1.5">
				<button class={[keypadButtonClass, 'text-[#7f0000]']} type="button" onclick={clearAll}
					>C</button
				>
				<button class={[keypadButtonClass, 'text-[#7f0000]']} type="button" onclick={backspace}>
					Back
				</button>
				<button
					class={[keypadButtonClass, 'text-[#7f0000]']}
					type="button"
					onclick={() => handleOperation('/')}
				>
					/
				</button>
				<button
					class={[keypadButtonClass, 'text-[#7f0000]']}
					type="button"
					onclick={() => handleOperation('*')}
				>
					*
				</button>
				{#each ['7', '8', '9'] as digit (digit)}
					<button class={keypadButtonClass} type="button" onclick={() => handleNum(digit)}
						>{digit}</button
					>
				{/each}
				<button
					class={[keypadButtonClass, 'text-[#7f0000]']}
					type="button"
					onclick={() => handleOperation('-')}
				>
					-
				</button>
				{#each ['4', '5', '6'] as digit (digit)}
					<button class={keypadButtonClass} type="button" onclick={() => handleNum(digit)}
						>{digit}</button
					>
				{/each}
				<button
					class={[keypadButtonClass, 'text-[#7f0000]']}
					type="button"
					onclick={() => handleOperation('+')}
				>
					+
				</button>
				{#each ['1', '2', '3'] as digit (digit)}
					<button class={keypadButtonClass} type="button" onclick={() => handleNum(digit)}
						>{digit}</button
					>
				{/each}
				<button
					class={[keypadButtonClass, 'col-4 row-[4/span_2] text-primary']}
					type="button"
					onclick={() => void calculate()}
				>
					=
				</button>
				<button
					class={[keypadButtonClass, 'col-[span_2]']}
					type="button"
					onclick={() => handleNum('0')}>0</button
				>
				<button class={keypadButtonClass} type="button" onclick={() => handleNum('.')}>.</button>
			</div>
		</div>

		<div class="flex flex-col">
			{#if error}
				<p class={[noticeClass, 'mb-4 text-[#7f0000]']}>{error}</p>
			{/if}

			<div class="grow bg-surface-variant p-2.5 bevel-raised-thin">
				<div class={displayLabelClass}>Difference</div>
				<p class={['mb-2', sectionMetaClass]}>
					{#if lastEquation && !computing && Number.parseFloat(lastEquation.correct) !== Number.parseFloat(mainDisplay)}
						{@const diff = Number.parseFloat(lastEquation.correct) - Number.parseFloat(mainDisplay)}
						{@const isHigher = diff > 0}
						{@const isLower = diff < 0}
						{@const formattedDiff = formatNumber(Math.abs(diff))}
						{@const percentageOff =
							(Math.abs(diff) / Math.max(Math.abs(Number.parseFloat(lastEquation.correct)), 1)) *
							100}
						The model's answer is {formattedDiff} units (or {percentageOff.toFixed(2)}%) {isHigher
							? 'higher'
							: isLower
								? 'lower'
								: 'equal'} than the correct result.
					{:else if lastEquation && Number.parseFloat(lastEquation.correct) === Number.parseFloat(mainDisplay)}
						The model's answer is correct!
					{:else}
						After you calculate an equation, this will show how far off the model's answer is.
					{/if}
				</p>
				<div
					class={[
						displayBaseClass,
						'min-h-5 text-xs',
						lastEquation && lastEquation.correct !== mainDisplay && 'text-muted-text'
					]}
				>
					{lastEquation && !computing
						? formatNumber(Number.parseFloat(lastEquation.correct) - Number.parseFloat(mainDisplay))
						: '0'}
				</div>

				<div class="mt-4">
					<div class={displayLabelClass}>Sample equations</div>
					<p class={['mb-2', sectionMetaClass]}>
						Load a preset, then press equals to compare the model against the exact result.
					</p>
					<div class="flex flex-wrap gap-2">
						{#each EXAMPLES as example (example.label)}
							<Button
								variant="secondary"
								class={exampleButtonClass}
								onclick={() => loadExample(example)}
							>
								{example.left}
								{example.operation}
								{example.right}
							</Button>
						{/each}
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
