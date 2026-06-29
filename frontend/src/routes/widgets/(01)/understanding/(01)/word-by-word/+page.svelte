<script module>
	export const title = 'Next Token Predictor';
	export const widgetUrl = '/next-token-predictor';
</script>

<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
	import TextInput from '$lib/components/ui/TextInput.svelte';
	import Title from '$lib/components/title/title.svelte';
	import { WidgetBackend } from '$lib/widgets/widget-backend.svelte';
	import { NextTokenPredictResponseSchema, type TokenPrediction } from '$lib/widgets/schemas';
	import { debounce } from '$lib/utils';
	import { onMount } from 'svelte';

	const EXAMPLES = [
		'The weather today is',
		'I love to eat',
		'Machine learning is',
		'The quick brown fox',
		'In the future, we will'
	];
	const TOP_K = 10;
	const TEMPERATURE_PRESETS = [
		{ label: 'None', value: 0, description: 'Always pick top choice' },
		{ label: 'Low', value: 0.5, description: 'Prefer top choices' },
		{ label: 'Standard', value: 1, description: 'Use shown probabilities' },
		{ label: 'High', value: 2, description: 'More likely to pick unlikely choices' },
		{ label: 'Max', value: 99, description: 'All choices are equal' }
	];

	const backend = new WidgetBackend(`${widgetUrl}`);

	function buildCompletion(text: string, nextToken: string): string {
		return `${text}${nextToken}`;
	}

	function getErrorMessage(error: unknown): string {
		return error instanceof Error ? error.message : 'Unknown error';
	}

	function applyTemperature(probs: number[], temp: number): number[] {
		const logits = probs.map((p) => Math.log(p) / temp);
		const weights = logits.map((l) => Math.exp(l));
		const sum = weights.reduce((acc, w) => acc + w, 0);
		return weights.map((w) => w / sum);
	}

	function sampleIndex(weights: number[]): number {
		const r = Math.random();
		let cumulative = 0;
		for (let i = 0; i < weights.length; i++) {
			cumulative += weights[i];
			if (r < cumulative) return i;
		}
		return weights.length - 1;
	}

	function pickSuggestion(preds: TokenPrediction[] | null): TokenPrediction | null {
		if (!preds?.length) return null;
		if (temperature === 0) return preds[0];
		const probs = preds.map((p) => p.probability);
		const adjusted = applyTemperature(probs, temperature);
		return preds[sampleIndex(adjusted)];
	}

	let predicting = $state(false);
	let connecting = $state(false);
	let inputText = $state('');
	let predictions = $state<TokenPrediction[] | null>(null);
	let error = $state<string | null>(null);
	let predictionRequestId = $state(0);
	let temperatureIndex = $state(2);
	let suggestedToken = $state<TokenPrediction | null>(null);

	let topPrediction = $derived(predictions?.[0] ?? null);
	let temperature = $derived(TEMPERATURE_PRESETS[temperatureIndex].value);
	let temperatureLabel = $derived(TEMPERATURE_PRESETS[temperatureIndex].label);
	let temperatureDescription = $derived(TEMPERATURE_PRESETS[temperatureIndex].description);
	let suggestion = $derived(
		suggestedToken && inputText.trim() ? buildCompletion(inputText, suggestedToken.token) : null
	);
	let modelStatus = $derived.by(() => {
		if (connecting) return 'Checking';
		if (backend.status === 'Ready' && predicting) return 'Refreshing';
		if (backend.status === 'Ready') return 'Ready';
		if (backend.status === 'Pending') return 'Pending';
		if (backend.status === 'Error') return 'Error';
		return 'Unknown';
	});
	let predictionSummary = $derived.by(() => {
		if (predicting) {
			return 'Refreshing results...';
		}

		if (!predictions?.length) {
			return 'No predictions yet';
		}

		return `${predictions.length} candidates loaded`;
	});

	const panelMetaClass = 'text-xs text-muted-text';
	const noticeClass = 'bevel-raised-thin bg-surface px-2.5 py-2 text-xs leading-6';
	const chipButtonClass = 'min-h-7.5 px-2.5 py-1.25 text-[11px]';
	const predictionButtonClass =
		'grid min-h-7.5 gap-2 px-2.5 py-1.25 text-left text-[11px] [grid-template-columns:auto_1fr_auto]';

	async function fetchPredictions(text: string): Promise<TokenPrediction[] | null> {
		if (!text.trim()) {
			return null;
		}

		const { data, error: parseError } = await backend.post(
			'/predict',
			{
				text,
				top_k: TOP_K
			},
			{ schema: NextTokenPredictResponseSchema }
		);

		if (parseError || !data) {
			throw parseError ?? new Error('Failed to parse predictions');
		}

		return data.tokens;
	}

	async function runPrediction(text: string, requestId: number) {
		if (requestId !== predictionRequestId) {
			return;
		}

		predicting = true;

		if (requestId === predictionRequestId) {
			error = null;
		}

		try {
			const nextPredictions = await fetchPredictions(text);

			if (requestId !== predictionRequestId) {
				return;
			}

			predictions = nextPredictions;
			suggestedToken = pickSuggestion(nextPredictions);
		} catch (errorValue) {
			if (requestId !== predictionRequestId) {
				return;
			}

			predictions = null;
			suggestedToken = null;
			error = `Prediction failed: ${getErrorMessage(errorValue)}`;
		} finally {
			if (requestId === predictionRequestId) {
				predicting = false;
			}
		}
	}

	const debouncedPredict = debounce((text: string, requestId: number) => {
		void runPrediction(text, requestId);
	}, 450);

	async function refreshPredictions(text: string) {
		const requestId = ++predictionRequestId;
		await runPrediction(text, requestId);
	}

	async function reconnectModel() {
		connecting = true;
		await backend.healthCheck();
		connecting = false;
	}

	function setPrompt(value: string) {
		inputText = value;
		error = null;

		if (!value.trim()) {
			predictionRequestId += 1;
			predictions = null;
			suggestedToken = null;
			predicting = false;
			return;
		}

		const requestId = ++predictionRequestId;
		debouncedPredict(value, requestId);
	}

	function applyExample(example: string) {
		inputText = example;
		void refreshPredictions(example);
	}

	function applyPrediction(token: string) {
		const nextValue = buildCompletion(inputText, token);
		inputText = nextValue;
		void refreshPredictions(nextValue);
	}

	function setTemperature(index: number) {
		temperatureIndex = index;
		suggestedToken = pickSuggestion(predictions);
	}

	function retrySuggestion() {
		suggestedToken = pickSuggestion(predictions);
	}

	function clearPrompt() {
		predictionRequestId += 1;
		inputText = '';
		predictions = null;
		suggestedToken = null;
		error = null;
		predicting = false;
	}

	onMount(() => {
		void backend.healthCheck();
	});
</script>

<Title value="Next Token Predictor" />

<div class="grid gap-3 bg-surface-variant p-3 font-[Tahoma,Geneva,Verdana,sans-serif] text-text">
	<section class="grid gap-2.5">
		<div class="flex items-start justify-between max-[760px]:block">
			<div>
				<div class="flex flex-wrap items-baseline gap-x-3 gap-y-2">
					<h2 class="m-0 text-base leading-[1.2]">Prompt</h2>
					<p class={['m-0', panelMetaClass]}>Model: {modelStatus}</p>
				</div>
				<p class="mt-1 max-w-[68ch] text-xs leading-6 text-muted-text">
					Type a sentence and see the top 10 most likely next tokens with their probabilities! Click
					on any prediction to add that token to your text.
				</p>
			</div>
		</div>
		<TextInput
			id="prompt"
			rows={6}
			placeholder="Start typing story, sentence, or phrase..."
			prediction={predicting ? null : suggestion}
			bind:value={() => inputText, (value) => setPrompt(value)}
		/>

		<div class="flex flex-wrap gap-2">
			<Button
				onclick={() => {
					if (suggestion) {
						applyPrediction(suggestedToken?.token ?? '');
					} else {
						refreshPredictions(inputText);
					}
				}}
				disabled={predicting || !inputText.trim()}
			>
				{#if predicting}
					Refreshing...
				{:else if suggestion}
					Accept suggestion
				{:else}
					Refresh predictions
				{/if}
			</Button>
			<Button
				variant="secondary"
				onclick={retrySuggestion}
				disabled={predicting || !predictions?.length || temperature === 0}
			>
				Retry
			</Button>
			<Button variant="secondary" onclick={clearPrompt} disabled={!inputText}>Clear prompt</Button>
			<Button variant="secondary" onclick={reconnectModel} disabled={connecting}>
				{connecting ? 'Checking...' : 'Reconnect model'}
			</Button>
		</div>
	</section>

	<section class="grid gap-2.5">
		<div class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1.5">
			<div>
				<h2 class="m-0 text-base leading-[1.2]">Temperature (Creativity)</h2>
			</div>
			<p class={['m-0', panelMetaClass]}>
				{temperatureLabel}{temperature !== 1 ? ` (${temperature})` : ''}
			</p>
		</div>

		<input
			type="range"
			min="0"
			max="4"
			step="1"
			value={temperatureIndex}
			oninput={(e) => setTemperature(Number((e.currentTarget as HTMLInputElement).value))}
			class="w-full accent-[var(--color-primary)]"
			aria-label="Temperature"
		/>
		<div class="flex justify-between text-[11px] text-muted-text">
			{#each TEMPERATURE_PRESETS as preset (preset.label)}
				<span>{preset.label}</span>
			{/each}
		</div>
		{#if temperatureDescription}
			<p class={['m-0', panelMetaClass]}>{temperatureDescription}</p>
		{/if}
	</section>

	<section class="grid gap-2.5">
		<div class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1.5">
			<div>
				<h2 class="m-0 text-base leading-[1.2]">Example prompts</h2>
			</div>
		</div>

		<div class="flex flex-wrap gap-2">
			{#each EXAMPLES as example (example)}
				<Button variant="secondary" class={chipButtonClass} onclick={() => applyExample(example)}>
					{example}...
				</Button>
			{/each}
		</div>
	</section>

	<section class="grid gap-2.5">
		<div class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1.5">
			<div>
				<h2 class="m-0 text-base leading-[1.2]">Top predictions</h2>
			</div>
			<p class={['m-0', panelMetaClass]}>
				{#if predicting}
					Refreshing results...
				{:else if predictions?.length}
					{predictionSummary}. Top guess: {topPrediction?.display ?? '--'}
				{:else}
					{predictionSummary}.
				{/if}
			</p>
		</div>

		{#if error}
			<p class={[noticeClass, 'm-0 text-[#7f0000]']}>{error}</p>
		{:else if predicting}
			<p class={[noticeClass, 'm-0']}>Updating predictions...</p>
		{:else if predictions?.length}
			<ol class="m-0 flex list-none flex-wrap gap-2 p-0">
				{#each predictions as prediction (`${prediction.rank}-${prediction.token_id}-${prediction.token}`)}
					<li>
						<Button
							variant="secondary"
							class={predictionButtonClass}
							pressed={prediction.token_id === suggestedToken?.token_id}
							onclick={() => applyPrediction(prediction.token)}
						>
							<span class="min-w-3.5 text-[11px] text-muted-text">{prediction.rank}.</span>
							<span class="text-xs">{prediction.display}</span>
							<span class="text-[11px] whitespace-nowrap">{prediction.percentage.toFixed(2)}%</span>
						</Button>
					</li>
				{/each}
			</ol>
		{:else}
			<p class={[noticeClass, 'm-0']}>
				Start with few words. Arcade will surface strongest next-token guesses here.
			</p>
		{/if}
	</section>
</div>
