import type { PredictRequest, PredictResponse } from "../types";

/** Raised for any non-2xx response, carrying a user-friendly message. */
export class ApiError extends Error {
  readonly status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

// Requests go to /api/* and are proxied to the FastAPI backend by Vite
// (see vite.config.ts). Override with VITE_API_BASE for other environments.
const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export async function predictTicket(
  ticketText: string,
  signal?: AbortSignal
): Promise<PredictResponse> {
  const body: PredictRequest = { ticket_text: ticketText };

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal,
    });
  } catch {
    throw new ApiError(
      0,
      "Could not reach the server. Make sure the backend is running."
    );
  }

  if (!res.ok) {
    throw new ApiError(res.status, await extractErrorMessage(res));
  }

  return (await res.json()) as PredictResponse;
}

async function extractErrorMessage(res: Response): Promise<string> {
  if (res.status === 409) {
    return "The model has not been trained yet. Train the model before analyzing tickets.";
  }
  try {
    const data = await res.json();
    // FastAPI puts errors under `detail` (string or validation array).
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail) && data.detail[0]?.msg) {
      return data.detail[0].msg;
    }
  } catch {
    /* fall through to generic message */
  }
  return `Request failed (${res.status}). Please try again.`;
}
