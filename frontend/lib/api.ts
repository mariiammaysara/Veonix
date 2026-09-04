/**
 * Veonix — API Client
 * lib/api.ts
 *
 * All backend communication lives here.
 * Never call fetch() directly from components or pages.
 */

import type {
  MealResult,
  MealHistoryResponse,
  StatsResponse,
  ApiErrorResponse,
  BatchResult,
} from "./types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Error class ────────────────────────────────────────────

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(message: string, status: number, code: string = "UNKNOWN_ERROR") {
    super(message);
    this.status = status;
    this.code = code;
    this.name = "ApiError";
  }
}

// ── Helper ─────────────────────────────────────────────────

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, options);

  if (!response.ok) {
    let errorBody: ApiErrorResponse | null = null;
    try {
      errorBody = await response.json();
    } catch {
      // non-JSON error body
    }

    const message =
      errorBody?.error?.message ?? "An unexpected error occurred.";
    const code = errorBody?.error?.code ?? "UNKNOWN_ERROR";

    throw new ApiError(message, response.status, code);
  }

  const body = await response.json();
  // Backend wraps all responses in { status, data }
  return body.data as T;
}

// ── Endpoints ──────────────────────────────────────────────

export async function analyzeImage(file: File): Promise<MealResult> {
  const form = new FormData();
  form.append("file", file);

  const response = await fetch(`${BASE_URL}/analyze/image`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    let errorBody: ApiErrorResponse | null = null;
    try {
      errorBody = await response.json();
    } catch {
      // ignore
    }
    const message = errorBody?.error?.message ?? "An unexpected error occurred.";
    const code = errorBody?.error?.code ?? "UNKNOWN_ERROR";
    throw new ApiError(message, response.status, code);
  }

  const body = await response.json();
  return body.data as MealResult;
}

/**
 * analyzeBatch — uploads N images in parallel for batch analysis.
 *
 * POST /analyze/images/batch with all files as FormData entries.
 * Returns per-meal results and aggregated nutrition totals.
 */
export async function analyzeBatch(files: File[]): Promise<BatchResult> {
  const form = new FormData();
  for (const file of files) {
    form.append("files", file);
  }

  const response = await fetch(`${BASE_URL}/analyze/images/batch`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    let errorBody: ApiErrorResponse | null = null;
    try {
      errorBody = await response.json();
    } catch {
      // ignore
    }
    const message = errorBody?.error?.message ?? "Batch analysis failed.";
    const code = errorBody?.error?.code ?? "UNKNOWN_ERROR";
    throw new ApiError(message, response.status, code);
  }

  const body = await response.json();
  return body.data as BatchResult;
}

export async function getMealHistory(
  limit = 50,
  offset = 0
): Promise<MealHistoryResponse> {
  return request<MealHistoryResponse>(
    `/analyze/history?limit=${limit}&offset=${offset}`
  );
}

export async function deleteMeal(id: number): Promise<void> {
  await fetch(`${BASE_URL}/analyze/${id}`, { method: "DELETE" });
}

export async function getStats(): Promise<StatsResponse> {
  return request<StatsResponse>("/analyze/stats");
}

export async function checkHealth(): Promise<{ status: string }> {
  return request<{ status: string }>("/health");
}
