import { z } from 'zod';
export const WIDGETS_BACKEND_URL =
	'https://jw0ikxn9w2.execute-api.ap-southeast-2.amazonaws.com/prod';

const HealthCheckPayloadSchema = z.object({
	status: z.enum(['pending', 'success', 'error']),
	message: z.string(),
	metadata: z
		.object({
			checked_at: z.string().optional(),
			gateway_url: z.string().nullable().optional(),
			endpoint: z.string().optional(),
			model_count: z.number().optional(),
			models: z.array(z.string()).optional(),
			error: z.string().nullable().optional()
		})
		.optional()
});

type Status = 'Not Checked' | 'Unknown' | 'Ready' | 'Pending' | 'Error';
type Message = {
	content: string;
	type: 'info' | 'error' | 'success';
};

export class WidgetBackend {
	_status: Status = $state<Status>('Not Checked');
	message: Message | null = $state<Message | null>(null);

	constructor(private readonly widgetUrl: string) {}

	async get<T extends z.ZodTypeAny>(
		path: string,
		options?: RequestInit & {
			schema: T;
		}
	): Promise<
		| {
				data: z.infer<T>;
				error: null;
		  }
		| {
				data: null;
				error: unknown;
		  }
	> {
		const url = `${WIDGETS_BACKEND_URL}${this.widgetUrl}${path}`;
		try {
			const response = await fetch(url, options);
			const data = await response.json();
			console.log('Response data:', data); // Log the response data for debugging
			const parsedData = options?.schema.parse(data);
			if (parsedData) {
				return { data: parsedData, error: null };
			}
			return { data: null, error: new Error('Failed to parse response data') };
		} catch (error) {
			return { data: null, error };
		}
	}

	async post<T extends z.ZodTypeAny>(
		path: string,
		body: unknown,
		options?: RequestInit & {
			schema: T;
		}
	): Promise<
		| {
				data: z.infer<T>;
				error: null;
		  }
		| {
				data: null;
				error: unknown;
		  }
	> {
		const url = `${WIDGETS_BACKEND_URL}${this.widgetUrl}${path}`;
		console.log('POST request to:', url, 'with body:', body); // Log the request details for debugging
		try {
			const headers = new Headers(
				options?.headers || {
					'Content-Type': 'application/json'
				}
			);
			const response = await fetch(url, {
				...options,
				method: 'POST',
				headers,
				body: JSON.stringify(body)
			});
			const data = await response.json();
			const parsedData = options?.schema.parse(data);
			if (parsedData) {
				return { data: parsedData, error: null };
			}
			return { data: null, error: new Error('Failed to parse response data') };
		} catch (error) {
			return { data: null, error };
		}
	}

	async healthCheck(): Promise<void> {
		// Perform a health check by sending a request to the widget backend, then update the status based on the response.
		const { data, error } = await this.get('/health', {
			schema: HealthCheckPayloadSchema
		});

		if (error) {
			this._status = 'Error';
			this.message = {
				content: 'Failed to check widget health.',
				type: 'error'
			};
			console.error('Health check error:', error);
			return;
		}

		if (data) {
			if (data.status === 'success') {
				this._status = 'Ready';
			} else if (data.status === 'pending') {
				this._status = 'Pending';
			} else {
				this._status = 'Error';
				this.message = {
					content: `Widget health check failed: ${data.message}`,
					type: 'error'
				};
			}
		} else {
			this._status = 'Unknown';
			this.message = {
				content: 'Widget health check returned unknown status.',
				type: 'info'
			};
		}
	}

	get status(): Status {
		return this._status;
	}
}
