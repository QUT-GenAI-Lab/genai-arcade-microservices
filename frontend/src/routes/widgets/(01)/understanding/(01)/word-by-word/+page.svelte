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

	const panelMetaClass = 'text-xs font-bold text-muted-text';
	const noticeClass =
		'bevel-raised-thin bg-surface px-2.5 py-2 text-xs leading-6';
	const chipButtonClass = 'min-h-7.5 px-2.5 py-1.25 text-[11px]';
	const predictionButtonClass =
		'grid min-h-7.5 gap-2 px-2.5 py-1.25 text-left text-[11px] [grid-template-columns:auto_1fr_auto]';

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

<div
	class="grid gap-3 bg-surface-variant p-3 font-[Tahoma,Geneva,Verdana,sans-serif] text-text"
>
	<section class="grid gap-2.5">
		<div class="flex items-start justify-between max-[760px]:block">
			<div>
				<div class="flex flex-wrap items-baseline gap-x-3 gap-y-2">
					<h2 class="m-0 text-base leading-[1.2]">Prompt</h2>
					<p class={['m-0', panelMetaClass]}>Model: {modelStatus}</p>
				</div>
				<p class="mt-1 max-w-[68ch] leading-6">
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

		<div class="flex flex-wrap gap-2">
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

	<section class="grid gap-2.5">
		<div class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1.5">
			<div>
				<h2 class="m-0 text-base leading-[1.2]">Example prompts</h2>
			</div>
		</div>

		<div class="flex flex-wrap gap-2">
			{#each EXAMPLES as example (example)}
				<Button
					variant="secondary"
					className={chipButtonClass}
					onclick={() => applyExample(example)}
				>
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
				{:else if predictions?.data.length}
					{predictionSummary}. Top guess: {topPrediction?.word ?? '--'}.
				{:else}
					{predictionSummary}.
				{/if}
			</p>
		</div>

		{#if loading}
			<p class={[noticeClass, 'm-0']}>Connecting model...</p>
		{:else if error}
			<p class={[noticeClass, 'm-0 text-[#7f0000]']}>{error}</p>
		{:else if predicting}
			<p class={[noticeClass, 'm-0']}>Updating predictions...</p>
		{:else if predictions?.data.length}
			<ol class="m-0 flex list-none flex-wrap gap-2 p-0">
				{#each predictions.data as prediction, index (`${prediction.word}-${prediction.probability}`)}
					<li>
						<Button
							variant="secondary"
							className={predictionButtonClass}
							onclick={() => applyPrediction(prediction.word)}
						>
							<span class="min-w-3.5 text-[11px] text-muted-text">{index + 1}.</span>
							<span class="text-xs">{prediction.word}</span>
							<span class="text-[11px] whitespace-nowrap"
								>{(prediction.probability * 100).toFixed(2)}%</span
							>
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
