import { z } from 'zod';

export const TokenPredictionSchema = z.object({
	rank: z.number(),
	token_id: z.number(),
	token: z.string(),
	display: z.string(),
	probability: z.number(),
	percentage: z.number(),
	logprob: z.number()
});

export const NextTokenPredictRequestSchema = z.object({
	text: z.string(),
	top_k: z.number().int().min(1).max(50).default(10)
});

export const NextTokenPredictResponseSchema = z.object({
	tokens: z.array(TokenPredictionSchema)
});

export const CalculateRequestSchema = z.object({
	left_num: z.number(),
	operation: z.enum(['+', '-', '*', '/']),
	right_num: z.number()
});

export const CalculateResponseSchema = z.string();

export const GenerateRequestSchema = z.object({
	input_text: z.string().min(1)
});

export const GenerateResponseSchema = z.object({
	content: z.string(),
	source_text: z.string().optional(),
	model: z.string().optional(),
	usage: z
		.object({
			prompt_tokens: z.number().optional(),
			completion_tokens: z.number().optional(),
			total_tokens: z.number().optional()
		})
		.optional()
});

export type TokenPrediction = z.infer<typeof TokenPredictionSchema>;
export type NextTokenPredictRequest = z.infer<typeof NextTokenPredictRequestSchema>;
export type NextTokenPredictResponse = z.infer<typeof NextTokenPredictResponseSchema>;
export type CalculateRequest = z.infer<typeof CalculateRequestSchema>;
export type CalculateResponse = z.infer<typeof CalculateResponseSchema>;
export type GenerateRequest = z.infer<typeof GenerateRequestSchema>;
export type GenerateResponse = z.infer<typeof GenerateResponseSchema>;
