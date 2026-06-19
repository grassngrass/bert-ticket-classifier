// Mirrors the FastAPI schemas in app/schemas.py.

export interface PredictRequest {
  ticket_text: string;
}

export interface PredictResponse {
  id: number;
  ticket_text: string;
  predicted_department: string;
  /** Confidence as a percentage (0–100). */
  confidence: number;
}
