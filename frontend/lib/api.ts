const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://veonix-api.onrender.com";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function analyzeImage(file: File) {
  const form = new FormData();
  form.append("file", file);

  const resp = await fetch(`${BASE_URL}/analyze/image`, {
    method: "POST",
    body: form,
  });

  if (!resp.ok) {
    const text = await resp.text();
    let message = "Analysis failed";
    try {
      const j = JSON.parse(text);
      message = j.detail || message;
    } catch {
      message = text || message;
    }
    throw new ApiError(message, resp.status);
  }

  return await resp.json();
}

