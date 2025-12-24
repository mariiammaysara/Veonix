const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeImage(file: File) {
  const form = new FormData();
  form.append("file", file);

  const resp = await fetch(`${BASE_URL}/analyze/image`, {
    method: "POST",
    body: form,
  });

  if (!resp.ok) {
    const text = await resp.text();
    try {
      const j = JSON.parse(text);
      throw new Error(j.detail || "Analysis failed");
    } catch {
      throw new Error(text || "Network error");
    }
  }

  return await resp.json();
}

export async function getMealHistory(limit: number = 10) {
  const resp = await fetch(`${BASE_URL}/analyze/history?limit=${limit}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(text || "Could not fetch history");
  }

  return await resp.json();
}

export async function deleteMeal(id: number) {
  const resp = await fetch(`${BASE_URL}/analyze/${id}`, {
    method: "DELETE",
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(text || "Failed to delete meal");
  }

  return true;
}