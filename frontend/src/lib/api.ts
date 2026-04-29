const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} - ${text || path}`);
  }
  return res.json() as Promise<T>;
}

export type AgentEvent = {
  i: number;
  ts: string;
  type: string;
  agent?: string;
  tool?: string;
  args?: string;
  content?: string;
};

export type AgentState = {
  status: "idle" | "working" | "done";
  tools: string[];
};

export type PlanStatus = {
  run_id: string;
  status: "queued" | "running" | "completed" | "failed";
  agent_states: Record<string, AgentState>;
  events: AgentEvent[];
  next_since: number;
  content: string | null;
  trip_id: string | null;
  error: string | null;
};

export type PlanResponse = { run_id: string; status: string; poll_url: string };

export function startPlan(body: {
  destination: string;
  num_days: number;
  budget_usd: number;
  preferences: string;
  user_email?: string;
}): Promise<PlanResponse> {
  return jsonFetch<PlanResponse>("/api/plan", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function pollPlanStatus(runId: string, since: number): Promise<PlanStatus> {
  return jsonFetch<PlanStatus>(`/api/plan/${runId}/status?since=${since}`);
}

export type TripSummary = {
  id: string;
  destination: string;
  duration_days: number;
  budget_usd: number;
  status: string;
  created_at: string | null;
  preferences?: string;
};

export type Trip = TripSummary & {
  itinerary_markdown: string;
  itinerary_json: unknown;
};

export type TripLog = {
  id: string;
  trip_id: string;
  agent_name: string;
  event_type: string;
  tool_name: string | null;
  content: string | null;
  duration_ms: number | null;
  created_at: string;
};

export function listTrips(userEmail = "default@travel.app"):
  Promise<{ count: number; trips: TripSummary[] }> {
  return jsonFetch(`/api/trips?user_email=${encodeURIComponent(userEmail)}`);
}

export function getTrip(id: string): Promise<Trip> {
  return jsonFetch(`/api/trips/${id}`);
}

export function deleteTrip(id: string): Promise<{ ok: boolean }> {
  return jsonFetch(`/api/trips/${id}`, { method: "DELETE" });
}

export function getTripLogs(id: string):
  Promise<{ trip_id: string; count: number; logs: TripLog[] }> {
  return jsonFetch(`/api/trips/${id}/logs`);
}

export type ExploreHit = {
  score: number;
  name: string;
  country: string;
  region: string;
  primary_type: string;
  tags: string[];
  trending_2026: boolean;
  latitude: number | null;
  longitude: number | null;
  doc: {
    description?: string;
    best_months?: string;
    top_attractions?: string[];
    budget_per_day_usd?: { budget?: number; mid?: number; luxury?: number };
  };
};

export function exploreSearch(q: string, topK = 8):
  Promise<{ query: string; count: number; results: ExploreHit[] }> {
  return jsonFetch(`/api/explore?q=${encodeURIComponent(q)}&top_k=${topK}`);
}

export function getHealth(): Promise<{
  ok: boolean;
  service: string;
  version: string;
  mcp_transport: string;
  mcp_url: string | null;
  pinecone_configured: boolean;
  supabase_configured: boolean;
}> {
  return jsonFetch("/health");
}
