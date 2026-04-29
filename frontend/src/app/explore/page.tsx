"use client";

import { useState } from "react";
import Link from "next/link";
import { Search, Loader2, Sparkles, MapPin, Sun, ArrowRight } from "lucide-react";
import { exploreSearch, type ExploreHit } from "@/lib/api";

const QUICK = [
  "beaches in India",
  "high-altitude monastery",
  "tropical island honeymoon",
  "heritage UNESCO Rajasthan",
  "cheap backpacker yoga",
  "trending 2026 mountains",
];

export default function ExplorePage() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<ExploreHit[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runSearch(query: string) {
    if (!query.trim()) return;
    setQ(query);
    setLoading(true);
    setError(null);
    try {
      const r = await exploreSearch(query, 12);
      setResults(r.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Destination Explorer</h1>
        <p className="text-[color:var(--muted)] mt-1">
          Semantic search over our 90-document curated knowledge base, embedded with
          location and category awareness.
        </p>
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); runSearch(q); }}
        className="card flex gap-2"
      >
        <input
          className="input flex-1"
          placeholder='Try "beaches in India" or "high-altitude monastery"...'
          value={q}
          onChange={(e) => setQ(e.target.value)}
          autoFocus
        />
        <button type="submit" disabled={loading || !q.trim()} className="btn btn-primary">
          {loading ? <Loader2 size={15} className="animate-spin" /> : <Search size={15} />}
          Search
        </button>
      </form>

      <div className="flex flex-wrap gap-2">
        {QUICK.map((qq) => (
          <button
            key={qq}
            type="button"
            onClick={() => runSearch(qq)}
            className="tag cursor-pointer hover:bg-white"
          >
            {qq}
          </button>
        ))}
      </div>

      {error && (
        <div className="card text-sm" style={{ borderColor: "var(--error)" }}>
          <div className="font-semibold text-[color:var(--error)]">Search failed</div>
          <div className="text-[color:var(--muted)] mt-1">{error}</div>
        </div>
      )}

      {results && (
        <div className="space-y-3">
          <div className="text-sm text-[color:var(--muted)]">
            {results.length} result{results.length === 1 ? "" : "s"} for{" "}
            <span className="kbd">{q}</span>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {results.map((r, i) => <ResultCard key={i} hit={r} q={q} />)}
          </div>
        </div>
      )}

      {!results && !loading && (
        <div className="card text-sm text-[color:var(--muted)]">
          Enter a query above or click one of the chips to start exploring.
        </div>
      )}
    </div>
  );
}

function ResultCard({ hit, q }: { hit: ExploreHit; q: string }) {
  const budget = hit.doc.budget_per_day_usd;
  return (
    <div className="card flex flex-col gap-2">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-semibold leading-tight">{hit.name}</h3>
          <div className="text-xs text-[color:var(--muted)] flex items-center gap-1 mt-0.5">
            <MapPin size={11} /> {hit.country}
            {hit.region && <span>· {hit.region}</span>}
          </div>
        </div>
        <span className="tag" title="cosine similarity">
          {(hit.score * 100).toFixed(0)}%
        </span>
      </div>

      <div className="flex flex-wrap gap-1">
        <span className="tag !bg-stone-100">{hit.primary_type}</span>
        {hit.trending_2026 && (
          <span
            className="tag inline-flex items-center gap-1"
            style={{ background: "#fef3c7", color: "#92400e" }}
          >
            <Sparkles size={10} /> trending 2026
          </span>
        )}
      </div>

      {hit.doc.description && (
        <p className="text-sm text-[color:var(--muted)] line-clamp-3">
          {hit.doc.description}
        </p>
      )}

      <div className="text-xs text-[color:var(--muted-2)] space-y-1">
        {hit.doc.best_months && (
          <div className="flex items-center gap-1">
            <Sun size={11} /> Best: {hit.doc.best_months}
          </div>
        )}
        {budget && (
          <div>
            ~${budget.budget}-${budget.luxury}/day
          </div>
        )}
      </div>

      <Link
        href={{ pathname: "/plan", query: { destination: hit.name } }}
        className="btn btn-secondary mt-1 text-xs !py-1.5"
      >
        Plan a trip <ArrowRight size={12} />
      </Link>
    </div>
  );
}
