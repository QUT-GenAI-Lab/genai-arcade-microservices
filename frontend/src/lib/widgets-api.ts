const WIDGETS_BACKEND_URL = 'https://jw0ikxn9w2.execute-api.ap-southeast-2.amazonaws.com/prod';

async function parseWidgetError(response: Response): Promise<Error> {
	const text = await response.text().catch(() => '');
	const detail = text ? ` ${text}` : '';
	return new Error(`Widget request failed: ${response.status} ${response.statusText}${detail}`);
}

export async function postWidget<T = unknown>(
	path: string,
	body: Record<string, unknown>
): Promise<T> {
	const response = await fetch(`${WIDGETS_BACKEND_URL}${path}`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	});

	if (!response.ok) {
		throw await parseWidgetError(response);
	}

	return (await response.json()) as T;
}

export async function getWidget<T = unknown>(path: string): Promise<T> {
	const response = await fetch(`${WIDGETS_BACKEND_URL}${path}`);

	if (!response.ok) {
		throw await parseWidgetError(response);
	}

	return (await response.json()) as T;
}
