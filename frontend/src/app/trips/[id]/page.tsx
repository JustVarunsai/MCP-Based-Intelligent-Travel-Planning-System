"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import {
  ArrowLeft, Calendar, DollarSign, Clock, ListChecks, Wrench, Loader2, MessageSquare,
} from "lucide-react";
import { getTrip, getTripLogs, type Trip, type TripLog } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function TripDashboard({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [trip, setTrip] = useState<Trip | null>(null);
  const [logs, setLogs] = useState<TripLog[] | null>(null);
  const [tab, setTab] = useState<"itinerary" | "audit">("itinerary");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancel = false;
    (async () => {
      try {
        const [t, l] = await Promise.all([getTrip(id), getTripLogs(id).catch(() => null)]);
        if (cancel) return;
        setTrip(t);
        setLogs(l ? l.logs : []);
      } catch (err) {
        if (!cancel) setError(err instanceof Error ? err.message : String(err));
      }
    })();
    return () => { cancel = true; };
  }, [id]);

  if (error) {
    return (
      <div className="space-y-4">
        <BackLink />
        <div className="card text-sm" style={{ borderColor: "var(--error)" }}>
          <div className="font-semibold text-[color:var(--error)]">Could not load trip</div>
          <div className="text-[color:var(--muted)] mt-1">{error}</div>
        </div>
      </div>
    );
  }

  if (!trip) {
    return (
      <div className="space-y-4">
        <BackLink />
        <div className="card flex items-center gap-2 text-sm text-[color:var(--muted)]">
          <Loader2 size={14} className="animate-spin" /> Loading trip...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <BackLink />

      <div>
        <h1 className="text-3xl font-bold tracking-tight">{trip.destination}</h1>
        <div className="flex flex-wrap gap-4 mt-2 text-sm text-[color:var(--muted)]">
          <span className="flex items-center gap-1.5"><Clock size={14} /> {trip.duration_days} days</span>
          <span className="flex items-center gap-1.5"><DollarSign size={14} /> ${trip.budget_usd} budget</span>
          {trip.created_at && (
            <span className="flex items-center gap-1.5">
              <Calendar size={14} /> {new Date(trip.created_at).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>

      {/* tabs */}
      <div className="border-b" style={{ borderColor: "var(--border)" }}>
        <div className="flex gap-1 -mb-px">
          <TabButton active={tab === "itinerary"} onClick={() => setTab("itinerary")}>
            <ListChecks size={14} /> Itinerary
          </TabButton>
          <TabButton active={tab === "audit"} onClick={() => setTab("audit")}>
            <Wrench size={14} /> Audit Trail
            {logs && logs.length > 0 && (
              <span className="tag !text-[10px] !px-1.5">{logs.length}</span>
            )}
          </TabButton>
        </div>
      </div>

      {tab === "itinerary" && (
        <div className="card">
          {trip.itinerary_markdown ? (
            <article className="prose">
              <ReactMarkdown>{trip.itinerary_markdown}</ReactMarkdown>
            </article>
          ) : (
            <div className="text-sm text-[color:var(--muted)]">No itinerary text saved.</div>
          )}
        </div>
      )}

      {tab === "audit" && (
        <AuditTrail logs={logs} />
      )}
    </div>
  );
}

function TabButton({ children, active, onClick }: {
  children: React.ReactNode; active: boolean; onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors",
        active
          ? "border-[color:var(--accent)] text-[color:var(--text)]"
          : "border-transparent text-[color:var(--muted)] hover:text-[color:var(--text)]"
      )}
    >
      {children}
    </button>
  );
}

function AuditTrail({ logs }: { logs: TripLog[] | null }) {
  if (logs === null) {
    return (
      <div className="card flex items-center gap-2 text-sm text-[color:var(--muted)]">
        <Loader2 size={14} className="animate-spin" /> Loading audit trail...
      </div>
    );
  }
  if (logs.length === 0) {
    return (
      <div className="card text-sm text-[color:var(--muted)]">
        No agent reasoning logs were captured for this trip.
      </div>
    );
  }

  // group by agent for the summary
  const byAgent: Record<string, TripLog[]> = {};
  for (const l of logs) {
    byAgent[l.agent_name] = byAgent[l.agent_name] || [];
    byAgent[l.agent_name].push(l);
  }

  return (
    <div className="space-y-4">
      <div className="card">
        <div className="font-semibold mb-2">Agent reasoning summary</div>
        <div className="text-sm text-[color:var(--muted)] mb-3">
          Every tool call across all agents during this trip's generation.
          This is observability for multi-agent systems — full transparency of decision-making.
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {Object.entries(byAgent).map(([agent, entries]) => {
            const tools = new Set(entries.map((e) => e.tool_name).filter(Boolean));
            return (
              <div key={agent} className="border rounded-lg p-3" style={{ borderColor: "var(--border)" }}>
                <div className="font-medium text-sm">{agent}</div>
                <div className="text-xs text-[color:var(--muted)] mt-1">
                  {entries.length} events · {tools.size} unique tools
                </div>
                {tools.size > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {[...tools].slice(0, 6).map((t) => (
                      <span key={t} className="tag !text-[10px]">{t}</span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="card">
        <div className="font-semibold mb-3">Full event timeline</div>
        <div className="space-y-1.5 max-h-[500px] overflow-auto pr-2">
          {logs.map((l) => <LogRow key={l.id} log={l} />)}
        </div>
      </div>
    </div>
  );
}

function LogRow({ log }: { log: TripLog }) {
  const isToolCall = log.tool_name && log.event_type.startsWith("agent_tool");
  return (
    <div className="flex gap-3 text-xs py-1.5 border-b last:border-0" style={{ borderColor: "var(--border)" }}>
      <span className="text-[color:var(--muted-2)] font-mono w-16 flex-shrink-0">
        {log.created_at ? new Date(log.created_at).toLocaleTimeString().slice(0, 8) : ""}
      </span>
      <span className="font-medium w-44 flex-shrink-0 truncate">{log.agent_name}</span>
      <span className="text-[color:var(--muted)] w-32 flex-shrink-0">{log.event_type}</span>
      {isToolCall && log.tool_name && (
        <span className="tag inline-flex items-center gap-1">
          <Wrench size={9} /> {log.tool_name}
        </span>
      )}
      {log.content && !isToolCall && (
        <span className="text-[color:var(--muted)] truncate">{log.content.slice(0, 80)}</span>
      )}
    </div>
  );
}

function BackLink() {
  return (
    <Link href="/trips" className="btn btn-ghost -ml-3">
      <ArrowLeft size={15} /> Back to my trips
    </Link>
  );
}
