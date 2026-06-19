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

export function ResultCard({ result }: { result: PredictResponse }) {
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
        </div>
      </div>

      <div className="flex flex-col items-center px-6 py-8">
        <span
          className={`animate-scale-in inline-flex items-center rounded-xl px-6 py-3 text-3xl font-extrabold uppercase tracking-tight ring-1 ${departmentClasses(
            result.predicted_department
          )}`}
        >
          {result.predicted_department}
        </span>
      </div>
    </section>
  );
}
