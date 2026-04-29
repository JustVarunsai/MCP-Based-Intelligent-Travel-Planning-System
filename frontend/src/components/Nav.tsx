"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, Map, Search, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Home", Icon: Sparkles },
  { href: "/plan", label: "Plan a Trip", Icon: Compass },
  { href: "/trips", label: "My Trips", Icon: Map },
  { href: "/explore", label: "Explore", Icon: Search },
];

export default function Nav() {
  const pathname = usePathname();

  return (
    <header
      className="sticky top-0 z-30 border-b backdrop-blur bg-[color:var(--bg)]/80"
      style={{ borderColor: "var(--border)" }}
    >
      <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <span
            className="inline-flex h-7 w-7 items-center justify-center rounded-md text-white font-bold text-sm"
            style={{ background: "var(--accent)" }}
          >
            T
          </span>
          <span className="hidden sm:inline">Travel MCP</span>
        </Link>

        <nav className="flex items-center gap-1">
          {links.map(({ href, label, Icon }) => {
            const active =
              href === "/"
                ? pathname === "/"
                : pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "btn btn-ghost text-sm",
                  active && "text-[color:var(--text)] bg-[#f5f5f4]"
                )}
              >
                <Icon size={15} className="hidden sm:inline" />
                <span>{label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
