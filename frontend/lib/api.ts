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
  UserProfile,
  AnalysisResponse,
  StreamEvent,
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

export async function analyzeImage(file: File): Promise<AnalysisResponse> {
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
  if (body.status === "pending_confirmation") {
    return {
      status: "pending_confirmation",
      thread_id: body.data.thread_id,
      analysis: body.data.analysis,
    };
  }
  return {
    status: "success",
    analysis: body.data,
  };
}

/**
 * analyzeImageStream — streams SSE analysis progress events.
 *
 * Opens a fetch SSE connection to POST /analyze/image/stream and calls
 * onEvent for each parsed event line. The final event carries the full result.
 *
 * @param file     The image file to analyze.
 * @param onEvent  Callback called for every received SSE event object.
 */
export async function analyzeImageStream(
  file: File,
  onEvent: (event: StreamEvent) => void
): Promise<void> {
  const form = new FormData();
  form.append("file", file);

  const response = await fetch(`${BASE_URL}/analyze/image/stream`, {
    method: "POST",
    body: form,
  });

  if (!response.ok || !response.body) {
    throw new ApiError("Stream request failed", response.status);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE lines are separated by double newlines; parse complete events only
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? ""; // keep the incomplete last part

    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith("data:")) continue;
      const jsonStr = line.slice(5).trim();
      try {
        const event = JSON.parse(jsonStr) as StreamEvent;
        onEvent(event);
      } catch {
        // malformed line — skip
      }
    }
  }
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

export async function askCoach(question: string): Promise<{ answer: string }> {
  return request<{ answer: string }>("/coach/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });
}

export async function getProfile(): Promise<UserProfile> {
  return request<UserProfile>("/profile");
}

export async function updateProfile(
  dietary_goal: string,
  allergies: string[]
): Promise<UserProfile> {
  return request<UserProfile>("/profile", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ dietary_goal, allergies }),
  });
}

export async function confirmMeal(
  threadId: string,
  action: "approve" | "reject",
  edits?: Partial<MealResult>
): Promise<{ message: string }> {
  return request<{ message: string }>(`/coach/confirm/${threadId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ action, edits }),
  });
}

export async function getHistory(threadId: string): Promise<any[]> {
  return request<any[]>(`/coach/history/${threadId}`);
}
