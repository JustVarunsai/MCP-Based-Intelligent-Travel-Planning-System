"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import ReactMarkdown from "react-markdown";
import {
  CheckCircle2, Loader2, AlertTriangle, Wrench, Sparkles, ArrowRight,
} from "lucide-react";
import {
  startPlan, pollPlanStatus, type AgentState, type AgentEvent, type PlanStatus,
} from "@/lib/api";
import { cn } from "@/lib/utils";

const AGENT_ORDER = [
  "Destination Researcher",
  "Accommodation Agent",
  "Route Optimizer",
  "Budget Optimizer",
  "Itinerary Compiler",
];

const TAGS = [
  "Beach", "Adventure", "Cultural", "Food & Dining", "Mountain", "Spiritual",
  "Nightlife", "Family-Friendly", "Budget-Friendly", "Luxury", "Heritage", "Nature",
];

export default function PlanPage() {
  return (
    <Suspense fallback={null}>
      <PlanForm />
    </Suspense>
  );
}

function PlanForm() {
  const search = useSearchParams();
  const initial = search.get("destination") || "";
  const [destination, setDestination] = useState(initial);
  const [days, setDays] = useState(5);
  const [budget, setBudget] = useState(1500);
  const [prefs, setPrefs] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [running, setRunning] = useState(false);
  const [status, setStatus] = useState<PlanStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const sinceRef = useRef(0);

  useEffect(() => {
    if (initial && !destination) setDestination(initial);
  }, [initial, destination]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setStatus(null);
    sinceRef.current = 0;

    const preferences = [prefs, ...tags].filter(Boolean).join(", ") || "General sightseeing";

    try {
      setRunning(true);
      const { run_id } = await startPlan({
        destination,
        num_days: days,
        budget_usd: budget,
        preferences,
      });
      pollLoop(run_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setRunning(false);
    }
  }

  async function pollLoop(runId: string) {
    while (true) {
      try {
        const snap = await pollPlanStatus(runId, sinceRef.current);
        sinceRef.current = snap.next_since;
        setStatus((prev) => mergeStatus(prev, snap));
        if (snap.status === "completed" || snap.status === "failed") {
          setRunning(false);
          return;
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        setRunning(false);
        return;
      }
      await sleep(1500);
    }
  }

  function toggleTag(t: string) {
    setTags((cur) => (cur.includes(t) ? cur.filter((x) => x !== t) : [...cur, t]));
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Plan a trip</h1>
        <p className="text-[color:var(--muted)] mt-1">
          Five agents will coordinate through the MCP server to build your itinerary.
        </p>
      </div>

      <form onSubmit={onSubmit} className="card space-y-5">
        <div className="grid sm:grid-cols-2 gap-5">
          <div>
            <label className="label">Destination</label>
            <input
              className="input"
              required
              placeholder="Goa, Tokyo, Bali, Paris..."
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              disabled={running}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Days</label>
              <input
                className="input"
                type="number" min={1} max={30}
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                disabled={running}
              />
            </div>
            <div>
              <label className="label">Budget (USD)</label>
              <input
                className="input"
                type="number" min={100} step={100}
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                disabled={running}
              />
            </div>
          </div>
        </div>

        <div>
          <label className="label">Preferences</label>
          <textarea
            className="textarea min-h-[60px]"
            placeholder="beaches, local food, heritage sites, nightlife..."
            value={prefs}
            onChange={(e) => setPrefs(e.target.value)}
            disabled={running}
          />
        </div>

        <div>
          <label className="label">Quick tags</label>
          <div className="flex flex-wrap gap-2">
            {TAGS.map((t) => (
              <button
                type="button"
                key={t}
                onClick={() => toggleTag(t)}
                disabled={running}
                className={cn(
                  "tag cursor-pointer",
                  tags.includes(t) && "ring-2 ring-[color:var(--accent)] bg-white"
                )}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-3 pt-1">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={running || !destination.trim()}
          >
            {running ? (
              <><Loader2 size={15} className="animate-spin" /> Planning...</>
            ) : (
              <><Sparkles size={15} /> Plan my trip</>
            )}
          </button>
          {status?.trip_id && (
            <Link href={`/trips/${status.trip_id}`} className="btn btn-secondary">
              Open trip <ArrowRight size={14} />
            </Link>
          )}
        </div>
      </form>

      {error && (
        <div
          className="card flex items-start gap-3"
          style={{ borderColor: "var(--error)" }}
        >
          <AlertTriangle size={18} className="text-[color:var(--error)] mt-0.5" />
          <div>
            <div className="font-semibold text-[color:var(--error)]">Run failed</div>
            <div className="text-sm text-[color:var(--muted)] mt-1">{error}</div>
          </div>
        </div>
      )}

      {status && <AgentPanel status={status} />}

      {status?.status === "completed" && status.content && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2 size={18} className="text-[color:var(--success)]" />
            <h2 className="text-xl font-semibold">Final itinerary</h2>
          </div>
          <article className="prose">
            <ReactMarkdown>{status.content}</ReactMarkdown>
          </article>
        </div>
      )}
    </div>
  );
}

function AgentPanel({ status }: { status: PlanStatus }) {
  const states = status.agent_states;
  const specialists = AGENT_ORDER.length;
  const specialistsDone = AGENT_ORDER.filter((n) => states[n]?.status === "done").length;
  const specialistsWorking = AGENT_ORDER.filter((n) => states[n]?.status === "working").length;

  const orchestratorState: AgentState = (() => {
    if (status.status === "completed") return { status: "done", tools: [] };
    if (status.status === "failed") return { status: "idle", tools: [] };
    if (specialistsDone === specialists) return { status: "working", tools: [] };
    return { status: "idle", tools: [] };
  })();

  const total = specialists + 1;
  const done = specialistsDone + (orchestratorState.status === "done" ? 1 : 0);
  const working = specialistsWorking + (orchestratorState.status === "working" ? 1 : 0);

  let phaseLabel = "queued";
  if (status.status === "completed") phaseLabel = "completed";
  else if (status.status === "failed") phaseLabel = "failed";
  else if (specialistsDone === specialists) phaseLabel = "compiling final response";
  else if (specialistsDone > 0 || specialistsWorking > 0) phaseLabel = "specialists running";
  else phaseLabel = "starting";

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-semibold">Agent activity</div>
          <div className="text-xs text-[color:var(--muted)]">
            {done}/{total} complete · {working} working ·{" "}
            <span className="kbd">{phaseLabel}</span>
          </div>
        </div>
        {status.status === "running" && (
          <div className="flex items-center gap-1 text-[color:var(--muted)]">
            <span className="dot-pulse">●</span>
            <span className="dot-pulse">●</span>
            <span className="dot-pulse">●</span>
          </div>
        )}
      </div>

      <div
        className="h-2 w-full rounded-full overflow-hidden"
        style={{ background: "var(--border)" }}
      >
        <div
          className="h-full transition-all duration-500"
          style={{ width: `${(done / total) * 100}%`, background: "var(--accent)" }}
        />
      </div>

      <div className="space-y-2">
        {AGENT_ORDER.map((name) => {
          const s: AgentState = states[name] || { status: "idle", tools: [] };
          return <AgentRow key={name} name={name} state={s} />;
        })}
        <AgentRow
          name="Orchestrator"
          state={orchestratorState}
          subtitle="Synthesises the 5 specialist outputs into the final answer"
        />
      </div>

      {(() => {
        const actions = status.events.filter(
          (e) => e.type === "agent_tool_start" || e.type === "agent_completed"
        );
        if (actions.length === 0) return null;
        return (
          <details className="text-xs text-[color:var(--muted)]" open>
            <summary className="cursor-pointer hover:text-[color:var(--text)]">
              Activity log ({actions.length})
            </summary>
            <div className="mt-2 max-h-64 overflow-auto space-y-1.5 font-mono">
              {actions.slice(-40).map((e: AgentEvent) => (
                <div key={e.i} className="flex gap-2 text-[11px]">
                  <span className="text-[color:var(--muted-2)] w-14 flex-shrink-0">
                    {e.ts.slice(11, 19)}
                  </span>
                  <span className="font-medium w-40 flex-shrink-0 truncate">
                    {e.agent}
                  </span>
                  {e.type === "agent_tool_start" ? (
                    <span className="text-[color:var(--text)] truncate">
                      <span className="text-[color:var(--accent)]">→ {e.tool}</span>
                      {e.args ? (
                        <span className="text-[color:var(--muted)]">({e.args})</span>
                      ) : null}
                    </span>
                  ) : (
                    <span className="text-[color:var(--success)]">finished</span>
                  )}
                </div>
              ))}
            </div>
          </details>
        );
      })()}
    </div>
  );
}

function AgentRow({
  name, state, subtitle,
}: {
  name: string;
  state: AgentState;
  subtitle?: string;
}) {
  const status = state.status;
  return (
    <div
      className={cn(
        "flex items-center justify-between gap-3 px-3 py-2 rounded-lg",
        status === "working" && "bg-[#fffbeb]",
        status === "done" && "bg-[#f0fdf4]"
      )}
    >
      <div className="flex items-center gap-3 min-w-0">
        <div className="w-5 flex-shrink-0">
          {status === "idle" && (
            <div className="h-2 w-2 rounded-full bg-[color:var(--border-strong)] mx-auto" />
          )}
          {status === "working" && (
            <Loader2 size={14} className="animate-spin text-[color:var(--warning)]" />
          )}
          {status === "done" && (
            <CheckCircle2 size={14} className="text-[color:var(--success)]" />
          )}
        </div>
        <div className="min-w-0">
          <div className="font-medium text-sm">{name}</div>
          {subtitle && (
            <div className="text-[11px] text-[color:var(--muted)] mt-0.5">{subtitle}</div>
          )}
          {state.tools.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {state.tools.slice(0, 5).map((t) => (
                <span
                  key={t}
                  className="tag !text-[10px] !px-1.5 !py-0.5 inline-flex items-center gap-1"
                >
                  <Wrench size={9} /> {t}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
      <span className="text-xs text-[color:var(--muted)] flex-shrink-0">
        {status === "idle" ? "waiting" : status === "working" ? "working..." : "done"}
      </span>
    </div>
  );
}

function mergeStatus(prev: PlanStatus | null, snap: PlanStatus): PlanStatus {
  if (!prev) return snap;
  return {
    ...snap,
    events: [...prev.events, ...snap.events],
    agent_states: snap.agent_states,
  };
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}
