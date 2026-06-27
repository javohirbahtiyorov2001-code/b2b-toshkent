import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "B2B CRM — Toshkent",
  description: "Lead generation and client management for Uzbekistan B2B",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="uz">
      <body>{children}</body>
    </html>
  );
}
