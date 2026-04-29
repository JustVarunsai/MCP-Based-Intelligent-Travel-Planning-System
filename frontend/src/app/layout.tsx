import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Nav from "@/components/Nav";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MCP Travel Planner",
  description:
    "Multi-agent AI travel planner powered by a custom Model Context Protocol server",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <Nav />
        <main className="flex-1 mx-auto w-full max-w-6xl px-4 py-8">
          {children}
        </main>
        <footer className="border-t" style={{ borderColor: "var(--border)" }}>
          <div className="mx-auto max-w-6xl px-4 py-4 text-xs text-[color:var(--muted)] flex items-center justify-between">
            <span>MCP Based Intelligent Travel Planning System</span>
            <span>5 agents · 9 tools · 2 resources · 2 prompts</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
