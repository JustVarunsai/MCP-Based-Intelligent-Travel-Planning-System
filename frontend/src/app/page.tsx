import Link from "next/link";
import { ArrowRight, Compass, Search, Sparkles, Wrench, Crown } from "lucide-react";

const AGENTS = [
  {
    name: "Destination Researcher",
    role: "Pulls together weather, culture, attractions and country basics so you know what you are walking into.",
    tools: ["search_knowledge_base", "geocode", "get_weather", "country_info", "find_attractions", "search_destinations"],
  },
  {
    name: "Accommodation Agent",
    role: "Suggests where to stay across budget, mid-range and luxury tiers using Wikivoyage's Sleep guides and regional benchmarks.",
    tools: ["search_destinations"],
  },
  {
    name: "Route Optimizer",
    role: "Geocodes every stop and runs a TSP solver so each day flows in the shortest possible loop.",
    tools: ["geocode", "route", "optimize_day_route"],
  },
  {
    name: "Budget Optimizer",
    role: "Cross-checks the plan against regional cost benchmarks and converts the totals into the local currency.",
    tools: ["search_knowledge_base", "convert_currency"],
  },
  {
    name: "Itinerary Compiler",
    role: "Brings everything together into a clean day-by-day plan with a packing list and travel tips.",
    tools: ["score_itinerary"],
  },
];

export default function Home() {
  return (
    <div className="space-y-14">
      <section className="space-y-4">
        <div className="tag" style={{ background: "#fef3c7", color: "#92400e" }}>
          <Sparkles size={12} /> Multi-agent · MCP · RAG
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight">
          MCP Based Intelligent <br className="hidden sm:block" />
          Travel Planning System
        </h1>
        <p className="text-lg text-[color:var(--muted)] max-w-2xl">
          Runs on a multi-agent system where each agent has its own goal,
          researching the place, finding stays, ordering daily routes,
          balancing the budget, compiling the plan. They coordinate through
          a custom Model Context Protocol server.
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

      <section className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "Specialist agents", value: "5" },
          { label: "MCP tools", value: "9" },
          { label: "MCP resources + prompts", value: "4" },
          { label: "Curated destinations", value: "74" },
        ].map((m) => (
          <div key={m.label} className="card text-center">
            <div className="text-3xl font-bold">{m.value}</div>
            <div className="text-xs text-[color:var(--muted)] mt-1">{m.label}</div>
          </div>
        ))}
      </section>

      <section className="space-y-5">
        <div>
          <h2 className="text-2xl font-semibold">The agent team</h2>
          <p className="text-sm text-[color:var(--muted)] mt-1">
            One coordinator delegates to five specialists. Each specialist has
            a clear job and a small set of tools it knows how to use.
          </p>
        </div>

        <div className="card space-y-2" style={{ background: "#f5f5f4" }}>
          <div className="flex items-center gap-2">
            <Crown size={16} className="text-[color:var(--muted)]" />
            <span className="font-medium">Orchestrator</span>
          </div>
          <p className="text-sm text-[color:var(--muted)]">
            Reads your input, hands work to each of the five specialists in
            order, and stitches their outputs into the final reply.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 gap-3">
          {AGENTS.map((a, i) => (
            <div key={a.name} className="card flex flex-col gap-3">
              <div className="flex items-center gap-2">
                <div
                  className="inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold"
                  style={{ background: "var(--accent)", color: "var(--accent-fg)" }}
                >
                  {i + 1}
                </div>
                <div className="font-semibold">{a.name}</div>
              </div>
              <p className="text-sm text-[color:var(--muted)] leading-relaxed">
                {a.role}
              </p>
              <div className="flex flex-wrap gap-1 mt-auto pt-1">
                {a.tools.map((t) => (
                  <span
                    key={t}
                    className="tag !text-[10px] inline-flex items-center gap-1"
                  >
                    <Wrench size={9} /> {t}
                  </span>
                ))}
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
