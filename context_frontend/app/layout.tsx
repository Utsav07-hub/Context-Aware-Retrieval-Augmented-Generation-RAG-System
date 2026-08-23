import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Context — AI Knowledge Workspace",
  description:
    "Add your knowledge. Ask questions. Get grounded answers backed by retrieval.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-bg text-ink antialiased">{children}</body>
    </html>
  );
}
