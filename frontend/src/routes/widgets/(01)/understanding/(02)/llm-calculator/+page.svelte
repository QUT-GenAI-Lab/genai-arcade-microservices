<script module>
	export const title = 'LLM Calculator';
	export const hfSpace = 'QUT-GenAILab/server-llm-calculator';
</script>

<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
	import Title from '$lib/components/title/title.svelte';
	import { Client } from '@gradio/client';
	import { onMount } from 'svelte';

	type Operation = '+' | '-' | '*' | '/';

	interface GradioPredictionResult {
		data?: unknown;
	}

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

	function extractMainResult(result: unknown): string {
		const payload = result as GradioPredictionResult | string | string[] | undefined;

		if (typeof payload === 'string') {
			return payload;
		}

		if (Array.isArray(payload)) {
			const first = payload[0];
			return typeof first === 'string' ? first : JSON.stringify(first);
		}

		if (payload && typeof payload === 'object' && 'data' in payload) {
			const data = payload.data;

			if (Array.isArray(data)) {
				const first = data[0];

				if (typeof first === 'string') {
					return first;
				}

				if (first && typeof first === 'object' && 'value' in first) {
					const nested = (first as { value?: unknown }).value;
					return typeof nested === 'string' ? nested : JSON.stringify(nested);
				}
			}

			if (typeof data === 'string') {
				return data;
			}
		}

		return JSON.stringify(result);
	}

	let loading = $state(false);
	let computing = $state(false);
	let app = $state.raw<Client | null>(null);
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
		if (loading) {
			return 'Connecting';
		}

		if (computing) {
			return 'Calculating';
		}

		return app ? 'Ready' : 'Offline';
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

	async function connectModel() {
		loading = true;
		error = null;

		try {
			app = await Client.connect(hfSpace);
		} catch (errorValue) {
			app = null;
			error = `Could not load model: ${getErrorMessage(errorValue)}`;
		} finally {
			loading = false;
		}
	}

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

		if (!app) {
			error = 'Model not connected yet.';
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
			const result = await app.predict('/calculate', {
				left_num: left,
				operation: activeOperation,
				right_num: right
			});

			if (activeRequestId !== requestId) {
				return;
			}

			const llmResult = extractMainResult(result);
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
		calculate();
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

	onMount(async () => {
		await connectModel();
	});
</script>

<svelte:window onkeydown={handleKeydown} />

<Title value="LLM Calculator" />

<div class="calculator-window__body" aria-live="polite">
	<div class="grid gap-6 sm:grid-cols-1 md:grid-cols-2">
		<div class="calc-section">
			<p class="section-header__meta mb-2">
				Type or use the keypad to enter an equation. Press '=' to see the correct result and the
				model's answer.
			</p>
			<div>
				<div class="display-label">{secondaryLabel}</div>
				<div class="display display--secondary">{secondaryDisplay}</div>
			</div>

			<div class="mt-2">
				<div class="display-label flex items-center justify-between">
					LLM output
					<span class="panel-header__meta">Model: {modelStatus}</span>
				</div>
				<div class={['display', 'display--main', computing && 'display--computing']}>
					{mainDisplay}
				</div>
			</div>

			<div class="keypad mt-3">
				<button class="calc-key calc-key--operator" type="button" onclick={clearAll}>C</button>
				<button class="calc-key calc-key--operator" type="button" onclick={backspace}>
					Back
				</button>
				<button
					class="calc-key calc-key--operator"
					type="button"
					onclick={() => handleOperation('/')}
				>
					/
				</button>
				<button
					class="calc-key calc-key--operator"
					type="button"
					onclick={() => handleOperation('*')}
				>
					*
				</button>
				{#each ['7', '8', '9'] as digit (digit)}
					<button class="calc-key" type="button" onclick={() => handleNum(digit)}>{digit}</button>
				{/each}
				<button
					class="calc-key calc-key--operator"
					type="button"
					onclick={() => handleOperation('-')}
				>
					-
				</button>
				{#each ['4', '5', '6'] as digit (digit)}
					<button class="calc-key" type="button" onclick={() => handleNum(digit)}>{digit}</button>
				{/each}
				<button
					class="calc-key calc-key--operator"
					type="button"
					onclick={() => handleOperation('+')}
				>
					+
				</button>
				{#each ['1', '2', '3'] as digit (digit)}
					<button class="calc-key" type="button" onclick={() => handleNum(digit)}>{digit}</button>
				{/each}
				<button class="calc-key calc-key--equals" type="button" onclick={() => void calculate()}>
					=
				</button>
				<button class="calc-key calc-key--wide" type="button" onclick={() => handleNum('0')}
					>0</button
				>
				<button class="calc-key" type="button" onclick={() => handleNum('.')}>.</button>
			</div>
		</div>

		<div class="sidebar-section">
			<Button
				variant="secondary"
				className="w-full mb-4"
				onclick={() => void connectModel()}
				disabled={loading || computing}
			>
				Reconnect model
			</Button>

			{#if error}
				<p class={['notice', 'notice--error', 'mb-4']}>{error}</p>
			{/if}

			<div class="info-panel">
				<div class="display-label">Difference</div>
				<p class="section-header__meta mb-2">
					{#if lastEquation && !computing && lastEquation.correct !== mainDisplay}
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
					{:else if lastEquation && lastEquation.correct === mainDisplay}
						The model's answer is correct!
					{:else}
						After you calculate an equation, this will show how far off the model's answer is.
					{/if}
				</p>
				<div
					class={[
						'display',
						'display--secondary',
						lastEquation && lastEquation.correct !== mainDisplay && 'display--computing'
					]}
				>
					{lastEquation && !computing
						? formatNumber(Number.parseFloat(lastEquation.correct) - Number.parseFloat(mainDisplay))
						: '0'}
				</div>

				<div class="mt-4">
					<div class="display-label">Sample equations</div>
					<p class="section-header__meta mb-2">
						Load a preset, then press equals to compare the model against the exact result.
					</p>
					<div class="example-grid">
						{#each EXAMPLES as example (example.label)}
							<Button
								variant="secondary"
								className="example-grid__button"
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

<style>
	h2,
	p {
		margin: 0;
	}

	.calculator-window__body {
		background: var(--arcade-surface-variant);
		padding: 12px;
	}

	.section-header__meta {
		font-size: 12px;
		color: var(--arcade-muted-text);
	}

	.info-panel {
		background: var(--arcade-surface-variant);
		padding: 10px;
		flex-grow: 1;
		border: 1px solid;
		border-color: var(--arcade-outline-light) var(--arcade-outline-dark) var(--arcade-outline-dark)
			var(--arcade-outline-light);
	}

	.display-label {
		font-size: 12px;
		font-weight: 700;
		margin-bottom: 4px;
	}

	.display {
		background: var(--arcade-surface);
		border: 1px solid;
		border-color: var(--arcade-muted-text) var(--arcade-outline-light) var(--arcade-outline-light)
			var(--arcade-muted-text);
		font-family: 'Courier New', Courier, monospace;
		overflow: hidden;
		padding: 6px 8px;
		text-align: right;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.display--secondary {
		font-size: 12px;
		min-height: 20px;
	}

	.display--main {
		font-size: 24px;
		font-weight: 700;
		min-height: 42px;
	}

	.display--computing {
		color: var(--arcade-muted-text);
	}

	.keypad {
		display: grid;
		gap: 6px;
		grid-template-columns: repeat(4, minmax(0, 1fr));
	}

	.calc-key {
		background: var(--arcade-surface-variant);
		border: 2px solid;
		border-color: var(--arcade-outline-light) var(--arcade-outline-dark) var(--arcade-outline-dark)
			var(--arcade-outline-light);
		color: var(--arcade-text);
		cursor: pointer;
		font-family: Tahoma, Geneva, Verdana, sans-serif;
		font-size: 13px;
		font-weight: 700;
		min-height: 36px;
	}

	.calc-key:hover,
	.calc-key:focus-visible {
		border-color: var(--arcade-outline-dark) var(--arcade-outline-light) var(--arcade-outline-light)
			var(--arcade-outline-dark);
		outline: none;
	}

	.calc-key:disabled {
		color: var(--arcade-muted-text);
		cursor: default;
	}

	.calc-key--operator {
		color: #7f0000;
	}

	.calc-key--equals {
		color: var(--arcade-primary);
		grid-column: 4;
		grid-row: 4 / span 2;
	}

	.calc-key--wide {
		grid-column: span 2;
	}

	.example-grid {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	:global(.example-grid__button) {
		font-size: 11px;
		min-height: 30px;
		padding: 5px 10px;
	}

	.notice {
		background: var(--arcade-surface-variant);
		border: 1px solid;
		border-color: var(--arcade-outline-light) var(--arcade-outline-dark) var(--arcade-outline-dark)
			var(--arcade-outline-light);
		font-size: 12px;
		line-height: 1.5;
		padding: 8px 10px;
	}

	.notice--error {
		color: #7f0000;
	}
</style>
