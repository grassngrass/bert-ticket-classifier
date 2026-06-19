import type { PredictResponse } from "../types";
import { CheckCircleIcon } from "./icons";

// Per-department accent colors. Unknown departments fall back to slate.
const DEPARTMENT_STYLES: Record<string, string> = {
  IT: "bg-blue-50 text-blue-700 ring-blue-200",
  HR: "bg-violet-50 text-violet-700 ring-violet-200",
  SAP: "bg-amber-50 text-amber-700 ring-amber-200",
};

function departmentClasses(dep: string): string {
  return (
    DEPARTMENT_STYLES[dep.toUpperCase()] ??
    "bg-slate-100 text-slate-700 ring-slate-200"
  );
}

function confidenceTone(confidence: number): string {
  if (confidence >= 80) return "text-emerald-600";
  if (confidence >= 60) return "text-amber-600";
  return "text-rose-600";
}

export function ResultCard({ result }: { result: PredictResponse }) {
  const confidence = Math.round(result.confidence * 10) / 10;

  return (
    <section
      className="animate-fade-in-up mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
      aria-live="polite"
    >
      <div className="flex items-center gap-3 border-b border-slate-100 bg-emerald-50/60 px-6 py-4">
        <CheckCircleIcon className="h-6 w-6 text-emerald-500" />
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
            Predicted Department
          </h2>
          <p className="text-xs text-slate-500">
            Routed automatically by the classification model
          </p>
        </div>
      </div>

      <div className="flex flex-col items-center gap-5 px-6 py-8 sm:flex-row sm:justify-between">
        <div className="flex flex-col items-center sm:items-start">
          <span
            className={`animate-scale-in inline-flex items-center rounded-xl px-6 py-3 text-3xl font-extrabold uppercase tracking-tight ring-1 ${departmentClasses(
              result.predicted_department
            )}`}
          >
            {result.predicted_department}
          </span>
          <span className="mt-2 text-xs text-slate-400">
            Ticket #{result.id}
          </span>
        </div>

        <div className="flex flex-col items-center sm:items-end">
          <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Confidence
          </span>
          <span
            className={`text-4xl font-bold tabular-nums ${confidenceTone(
              confidence
            )}`}
          >
            {confidence}%
          </span>
          <div className="mt-3 h-2 w-40 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-blue-600 transition-[width] duration-700 ease-out"
              style={{ width: `${Math.min(confidence, 100)}%` }}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
