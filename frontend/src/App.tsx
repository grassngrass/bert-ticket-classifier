import { useState } from "react";
import { TicketForm } from "./components/TicketForm";
import { ResultCard } from "./components/ResultCard";
import { AlertIcon } from "./components/icons";
import { predictTicket, ApiError } from "./api/client";
import type { PredictResponse } from "./types";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze(text: string) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await predictTicket(text);
      setResult(response);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-full flex-col bg-gradient-to-b from-slate-100 to-slate-200">
      <main className="flex flex-1 items-center justify-center px-4 py-10 sm:py-16">
        <div className="w-full max-w-xl">
          {/* Header */}
          <header className="mb-8 text-center">
            <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/20">
              <span className="text-lg font-bold">AI</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              AI Ticket Routing Portal
            </h1>
            <p className="mt-2 text-sm text-slate-500">
              Describe your issue and our model instantly routes it to the right
              department.
            </p>
          </header>

          {/* Form card */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <TicketForm loading={loading} onSubmit={handleAnalyze} />

            {error && (
              <div
                className="animate-fade-in-up mt-4 flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
                role="alert"
              >
                <AlertIcon className="mt-0.5 h-5 w-5 flex-shrink-0 text-rose-500" />
                <span>{error}</span>
              </div>
            )}
          </div>

          {/* Result card */}
          {result && <ResultCard result={result} />}

          <footer className="mt-10 text-center text-xs text-slate-400">
            Internal tool · Predictions are routed automatically and may be
            reviewed.
          </footer>
        </div>
      </main>
    </div>
  );
}
