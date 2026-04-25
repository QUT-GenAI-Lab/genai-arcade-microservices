import { createContext } from 'svelte';

class TitleContext {
	#title = $state<string | null>(null);

	setTitle(title: string | null) {
		this.#title = title;
	}

	get title() {
		return this.#title;
	}
}

const [_getTitleContext, _setTitleContext] = createContext<TitleContext>();

export function getTitleContext() {
	return _getTitleContext();
}

export function setTitleContext() {
	const context = new TitleContext();
	_setTitleContext(context);
	return context;
}
