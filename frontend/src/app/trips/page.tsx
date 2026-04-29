"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Calendar, Trash2, Loader2, MapPin, ArrowRight } from "lucide-react";
import { listTrips, deleteTrip, type TripSummary } from "@/lib/api";

export default function TripsPage() {
  const [trips, setTrips] = useState<TripSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("");

  async function refresh() {
    try {
      const r = await listTrips();
      setTrips(r.trips);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleDelete(id: string) {
    if (!confirm("Delete this trip?")) return;
    try {
      await deleteTrip(id);
      await refresh();
    } catch (err) {
      alert(err instanceof Error ? err.message : String(err));
    }
  }

  const filtered = (trips || []).filter((t) =>
    t.destination.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My trips</h1>
          <p className="text-[color:var(--muted)] mt-1">
            Itineraries auto-saved when generation completes.
          </p>
        </div>
        <Link href="/plan" className="btn btn-primary">Plan another</Link>
      </div>

      {error && (
        <div className="card text-sm" style={{ borderColor: "var(--error)" }}>
          <div className="font-semibold text-[color:var(--error)]">Could not load trips</div>
          <div className="text-[color:var(--muted)] mt-1">{error}</div>
        </div>
      )}

      {trips === null && !error && (
        <div className="card flex items-center gap-2 text-sm text-[color:var(--muted)]">
          <Loader2 size={14} className="animate-spin" /> Loading...
        </div>
      )}

      {trips && (
        <>
          <input
            className="input max-w-sm"
            placeholder="Filter by destination..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />

          {filtered.length === 0 ? (
            <div className="card text-sm text-[color:var(--muted)]">
              No saved trips yet.{" "}
              <Link href="/plan" className="underline">Plan one</Link>.
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {filtered.map((t) => (
                <div key={t.id} className="card flex flex-col gap-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <MapPin size={16} className="text-[color:var(--muted)]" />
                      <h3 className="font-semibold">{t.destination}</h3>
                    </div>
                    <span className="tag">{t.status}</span>
                  </div>
                  <div className="text-sm text-[color:var(--muted)]">
                    {t.duration_days} days · ${t.budget_usd} budget
                  </div>
                  <div className="text-xs text-[color:var(--muted-2)] flex items-center gap-1">
                    <Calendar size={11} />
                    {t.created_at ? new Date(t.created_at).toLocaleDateString() : ""}
                  </div>
                  <div className="flex gap-2 mt-2">
                    <Link href={`/trips/${t.id}`} className="btn btn-primary flex-1">
                      View <ArrowRight size={14} />
                    </Link>
                    <button
                      onClick={() => handleDelete(t.id)}
                      className="btn btn-secondary"
                      aria-label="delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
