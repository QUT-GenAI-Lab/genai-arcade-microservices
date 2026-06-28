import { createContext } from 'svelte';

class DialogState {
	#open = $state(false);
	#title = $state<string | null>(null);
	#triggerRect = $state<DOMRect | null>(null);

	get open() {
		return this.#open;
	}

	get title() {
		return this.#title;
	}

	get triggerRect() {
		return this.#triggerRect;
	}

	setOpen(value: boolean) {
		this.#open = value;
	}

	setTitle(value: string) {
		this.#title = value;
	}

	setTriggerRect(rect: DOMRect | null) {
		this.#triggerRect = rect;
	}
}

const [getDialogContextFn, setDialogContextFn] = createContext<DialogState>();

export function getDialogContext() {
	return getDialogContextFn();
}

export function setDialogContext() {
	const context = new DialogState();
	setDialogContextFn(context);
	return context;
}
