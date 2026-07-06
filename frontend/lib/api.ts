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
  return request<MealResult>("/analyze/image", { method: "POST", body: form });
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
