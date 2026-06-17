import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Recruiter — Intelligent Candidate Matching",
  description:
    "AI-powered recruiting platform. Upload resumes, match candidates to jobs with semantic AI scoring, and build your talent pipeline.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
