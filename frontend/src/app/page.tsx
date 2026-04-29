import Link from "next/link";
import { ArrowRight, Compass, Search, Sparkles, Layers, Boxes, Zap } from "lucide-react";

export default function Home() {
  return (
    <div className="space-y-12">
      {/* hero */}
      <section className="space-y-4">
        <div className="tag" style={{ background: "#fef3c7", color: "#92400e" }}>
          <Sparkles size={12} /> Multi-agent · MCP · RAG
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight">
          MCP Based Intelligent <br className="hidden sm:block" />
          Travel Planning System
        </h1>
        <p className="text-lg text-[color:var(--muted)] max-w-2xl">
          Five specialist AI agents coordinate through a custom Model Context
          Protocol server we authored — using free public APIs, RAG-grounded
          knowledge, and a deterministic itinerary scorer.
        </p>
        <div className="flex flex-wrap gap-3 pt-2">
          <Link href="/plan" className="btn btn-primary">
            Plan a Trip <ArrowRight size={15} />
          </Link>
          <Link href="/explore" className="btn btn-secondary">
            <Search size={15} /> Explore Destinations
          </Link>
        </div>
      </section>

      {/* numbers */}
      <section className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "Specialist agents", value: "5" },
          { label: "MCP tools", value: "9" },
          { label: "Curated destinations", value: "74" },
          { label: "Free public APIs", value: "7" },
        ].map((m) => (
          <div key={m.label} className="card text-center">
            <div className="text-3xl font-bold">{m.value}</div>
            <div className="text-xs text-[color:var(--muted)] mt-1">{m.label}</div>
          </div>
        ))}
      </section>

      {/* what's special */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">What makes this different</h2>
        <div className="grid sm:grid-cols-3 gap-3">
          {[
            {
              Icon: Layers,
              title: "All 3 MCP primitives",
              body: "Tools, Resources and Prompts — most public servers only do tools.",
            },
            {
              Icon: Boxes,
              title: "Composite + domain tools",
              body: "Beyond API wrappers — TSP route ordering and a deterministic 6-criterion itinerary scorer.",
            },
            {
              Icon: Zap,
              title: "Local ↔ cloud transports",
              body: "Same server, stdio for development or SSE in cloud — flipped by one env variable.",
            },
          ].map(({ Icon, title, body }) => (
            <div key={title} className="card space-y-2">
              <Icon size={20} className="text-[color:var(--muted)]" />
              <div className="font-semibold">{title}</div>
              <p className="text-sm text-[color:var(--muted)]">{body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* agents */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">The agent team</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {[
            { name: "Destination Researcher", role: "Weather, culture, attractions, country info" },
            { name: "Accommodation Agent", role: "Stays across budget tiers from Wikivoyage + benchmarks" },
            { name: "Route Optimizer", role: "Geocoding + OSRM routing + TSP daily ordering" },
            { name: "Budget Optimizer", role: "Regional benchmarks via RAG + live currency conversion" },
            { name: "Itinerary Compiler", role: "Synthesises into a structured plan + self-scores" },
            { name: "Orchestrator", role: "Delegates to all 5 specialists and composes the answer" },
          ].map((a) => (
            <div key={a.name} className="card">
              <div className="font-medium">{a.name}</div>
              <div className="text-sm text-[color:var(--muted)] mt-1">
                {a.role}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <Link href="/plan" className="btn btn-primary text-base px-6 py-3">
          Plan a trip now <ArrowRight size={16} />
        </Link>
      </section>
    </div>
  );
}
