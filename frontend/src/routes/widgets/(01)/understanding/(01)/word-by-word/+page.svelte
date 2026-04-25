<script module>
	export const title = 'Next Word Predictor';
	export const hfSpace = 'qut-genailab/next-word-predictor';
</script>

<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
	import TextInput from '$lib/components/ui/TextInput.svelte';
	import Title from '$lib/components/title/title.svelte';
	import { debounce } from '$lib/utils';
	import { Client } from '@gradio/client';
	import { onMount } from 'svelte';

	const EXAMPLES = [
		'The weather today is',
		'I love to eat',
		'Machine learning is',
		'The quick brown fox',
		'In the future, we will'
	];

	interface RawPredictionResult {
		type: string;
		time: Date;
		data: {
			visible: boolean;
			value: string;
			__type__: string;
		}[];
		endpoint: string;
		fn_index: number;
	}

	interface PredictionResult {
		type: string;
		time: Date;
		data: {
			visible: boolean;
			word: string;
			probability: number;
		}[];
		endpoint: string;
		fn_index: number;
	}

	function parsePredictionResult(raw: RawPredictionResult): PredictionResult {
		const data = raw.data.map((item) => {
			const [word, probStr] = item.value.split('|').map((s) => s.trim());
			const probability = Number.parseFloat(probStr.split(' ')[0] ?? '0');
			return {
				visible: item.visible,
				word,
				probability
			};
		});

		return {
			...raw,
			data: data.filter((item) => item.visible)
		};
	}

	function buildCompletion(text: string, nextWord: string): string {
		if (!text) {
			return nextWord;
		}
		const separator = text.endsWith(' ') ? '' : ' ';
		return `${text}${separator}${nextWord}`;
	}

	function getErrorMessage(error: unknown): string {
		return error instanceof Error ? error.message : 'Unknown error';
	}

	let loading = $state(false);
	let predicting = $state(false);
	let inputText = $state('');
	let app = $state.raw<Client | null>(null);
	let predictions = $state.raw<PredictionResult | null>(null);
	let error = $state<string | null>(null);
	let predictionRequestId = $state(0);

	let topPrediction = $derived(predictions?.data[0] ?? null);
	let suggestion = $derived(
		topPrediction && inputText.trim() ? buildCompletion(inputText, topPrediction.word) : null
	);
	let modelStatus = $derived.by(() => {
		if (loading) {
			return 'Connecting';
		}

		return app ? 'Ready' : 'Offline';
	});
	let predictionSummary = $derived.by(() => {
		if (predicting) {
			return 'Refreshing results...';
		}

		if (!predictions?.data.length) {
			return 'No predictions yet';
		}

		return `${predictions.data.length} candidates loaded`;
	});

	async function fetchPredictions(text: string): Promise<PredictionResult | null> {
		const prompt = text.trim();
		if (!prompt) {
			return null;
		}

		if (!app) {
			if (loading) {
				return null;
			}

			throw new Error('Model not connected yet.');
		}

		const result = (await app.predict('/update_predictions', {
			text: prompt
		})) as RawPredictionResult;
		return parsePredictionResult(result);
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
		} catch (errorValue) {
			if (requestId !== predictionRequestId) {
				return;
			}

			predictions = null;
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

	async function connectModel() {
		loading = true;
		error = null;

		try {
			app = await Client.connect(hfSpace);

			if (inputText.trim()) {
				await refreshPredictions(inputText);
			}
		} catch (errorValue) {
			app = null;
			error = `Could not load model: ${getErrorMessage(errorValue)}`;
		} finally {
			loading = false;
		}
	}

	async function refreshPredictions(text: string) {
		const requestId = ++predictionRequestId;
		await runPrediction(text, requestId);
	}

	function setPrompt(value: string) {
		inputText = value;
		error = null;

		if (!value.trim()) {
			predictionRequestId += 1;
			predictions = null;
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

	function applyPrediction(word: string) {
		const nextValue = buildCompletion(inputText, word);
		inputText = nextValue;
		void refreshPredictions(nextValue);
	}

	function clearPrompt() {
		predictionRequestId += 1;
		inputText = '';
		predictions = null;
		error = null;
		predicting = false;
	}

	onMount(async () => {
		await connectModel();
	});
</script>

<Title value="Next Word Predictor" />

<div class="widget-shell">
	<section class="widget-panel">
		<div class="prompt-header">
			<div>
				<div class="prompt-header__title-row">
					<h2>Prompt</h2>
					<p class="model-status">Model: {modelStatus}</p>
				</div>
				<p class="prompt-header__copy">
					Type a sentence and see the top 10 most likely next words with their probabilities! Click
					on any prediction to add that word to your text.
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

		<div class="widget-panel__actions">
			<Button
				onclick={() => void refreshPredictions(inputText)}
				disabled={loading || predicting || !inputText.trim()}
			>
				{predicting ? 'Predicting...' : 'Predict next word'}
			</Button>
			<Button variant="secondary" onclick={clearPrompt} disabled={!inputText}>Clear prompt</Button>
			<Button variant="secondary" onclick={() => void connectModel()} disabled={loading}>
				Reconnect model
			</Button>
		</div>
	</section>

	<section class="widget-panel">
		<div class="section-header">
			<div>
				<h2>Example prompts</h2>
			</div>
		</div>

		<div class="example-grid">
			{#each EXAMPLES as example (example)}
				<Button
					variant="secondary"
					className="example-grid__button"
					onclick={() => applyExample(example)}
				>
					{example}...
				</Button>
			{/each}
		</div>
	</section>

	<section class="widget-panel">
		<div class="section-header">
			<div>
				<h2>Top predictions</h2>
			</div>
			<p class="section-header__meta">
				{#if predicting}
					Refreshing results...
				{:else if predictions?.data.length}
					{predictionSummary}. Top guess: {topPrediction?.word ?? '--'}.
				{:else}
					{predictionSummary}.
				{/if}
			</p>
		</div>

		{#if loading}
			<p class="notice">Connecting model...</p>
		{:else if error}
			<p class={['notice', 'notice--error']}>{error}</p>
		{:else if predicting}
			<p class="notice">Updating predictions...</p>
		{:else if predictions?.data.length}
			<ol class="prediction-list">
				{#each predictions.data as prediction, index (`${prediction.word}-${prediction.probability}`)}
					<li>
						<Button
							variant="secondary"
							className="prediction-list__button"
							onclick={() => applyPrediction(prediction.word)}
						>
							<span class="prediction-list__rank">{index + 1}.</span>
							<span class="prediction-list__word">{prediction.word}</span>
							<span class="prediction-list__probability"
								>{(prediction.probability * 100).toFixed(2)}%</span
							>
						</Button>
					</li>
				{/each}
			</ol>
		{:else}
			<p class="notice">
				Start with few words. Arcade will surface strongest next-token guesses here.
			</p>
		{/if}
	</section>
</div>

<style>
	.widget-shell {
		color: var(--arcade-text);
		display: grid;
		font-family: Tahoma, Geneva, Verdana, sans-serif;
		gap: 12px;
		padding: 6px 8px 8px;
	}

	.widget-panel {
		display: grid;
		gap: 10px;
	}

	.prompt-header {
		align-items: start;
		display: flex;
		justify-content: space-between;
	}

	.prompt-header__title-row {
		align-items: baseline;
		display: flex;
		flex-wrap: wrap;
		gap: 8px 12px;
	}

	.prompt-header__copy {
		line-height: 1.5;
		margin-top: 4px;
		max-width: 68ch;
	}

	.model-status,
	.section-header__meta {
		color: var(--arcade-muted-text);
		font-size: 12px;
		font-weight: 700;
	}

	h2,
	p,
	ol {
		margin: 0;
	}

	h2 {
		font-size: 16px;
		line-height: 1.2;
	}

	.widget-panel__actions {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.section-header {
		align-items: baseline;
		display: flex;
		flex-wrap: wrap;
		gap: 6px 12px;
		justify-content: space-between;
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

	.prediction-list {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		list-style: none;
		padding: 0;
	}

	:global(.prediction-list__button) {
		display: grid;
		font-size: 11px;
		gap: 8px;
		grid-template-columns: auto 1fr auto;
		min-height: 30px;
		padding: 5px 10px;
		text-align: left;
	}

	.prediction-list__rank {
		color: var(--arcade-muted-text);
		font-size: 11px;
		min-width: 14px;
	}

	.prediction-list__word {
		font-size: 12px;
	}

	.prediction-list__probability {
		font-size: 11px;
		white-space: nowrap;
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

	@media (max-width: 760px) {
		.prompt-header {
			display: block;
		}
	}
</style>
