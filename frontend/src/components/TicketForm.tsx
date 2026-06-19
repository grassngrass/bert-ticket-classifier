import { useState } from "react";
import { SparklesIcon, SpinnerIcon } from "./icons";

interface TicketFormProps {
  loading: boolean;
  onSubmit: (text: string) => void;
}

const MAX_LENGTH = 2000;

export function TicketForm({ loading, onSubmit }: TicketFormProps) {
  const [text, setText] = useState("");
  const trimmed = text.trim();
  const canSubmit = trimmed.length > 0 && !loading;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    onSubmit(trimmed);
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-2 flex items-baseline justify-between">
        <label
          htmlFor="ticket-text"
          className="text-sm font-semibold text-slate-800"
        >
          Describe Your Issue
        </label>
        <span className="text-xs tabular-nums text-slate-400">
          {text.length}/{MAX_LENGTH}
        </span>
      </div>

      <textarea
        id="ticket-text"
        value={text}
        onChange={(e) => setText(e.target.value.slice(0, MAX_LENGTH))}
        placeholder="e.g. I can't log in to my account and my password reset email never arrived…"
        rows={6}
        disabled={loading}
        className="w-full resize-y rounded-xl border border-slate-200 bg-slate-50/50 px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 shadow-inner outline-none transition focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-100 disabled:opacity-60"
      />

      <button
        type="submit"
        disabled={!canSubmit}
        className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-200 active:scale-[0.99] disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
      >
        {loading ? (
          <>
            <SpinnerIcon className="h-5 w-5 animate-spin" />
            Analyzing…
          </>
        ) : (
          <>
            <SparklesIcon className="h-5 w-5" />
            Analyze Ticket
          </>
        )}
      </button>
    </form>
  );
}
