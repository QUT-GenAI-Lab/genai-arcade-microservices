export function jumpToFragment(target: string) {
	if (typeof window === 'undefined') {
		return;
	}

	if (!target.startsWith('#')) {
		window.location.assign(target);
		return;
	}

	const element = document.getElementById(target.slice(1));

	if (element) {
		window.history.replaceState({}, '', target);
		element.scrollIntoView({ behavior: 'smooth', block: 'start' });
		return;
	}

	window.location.hash = target;
}
