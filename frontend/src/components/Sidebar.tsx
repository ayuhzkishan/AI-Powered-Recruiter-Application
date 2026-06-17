"use client";

import Link from "next/link";
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { clearToken, isAuthenticated } from "@/lib/auth";

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  // Auth guard — runs on every protected page that uses this Sidebar
  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    }
  }, [router]);

  const handleLogout = () => {
    clearToken();
    router.push("/login");
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🧠</div>
        <div>
          <div className="sidebar-logo-text">AI Recruiter</div>
          <div className="sidebar-logo-sub">Talent Pipeline</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <Link
          href="/dashboard"
          className={`nav-link ${pathname === "/dashboard" ? "active" : ""}`}
        >
          <span className="nav-icon">📊</span>
          <span>Dashboard</span>
        </Link>
        <Link
          href="/candidates"
          className={`nav-link ${
            pathname.startsWith("/candidates") ? "active" : ""
          }`}
        >
          <span className="nav-icon">👥</span>
          <span>Candidates</span>
        </Link>
        <Link
          href="/jobs"
          className={`nav-link ${pathname.startsWith("/jobs") ? "active" : ""}`}
        >
          <span className="nav-icon">📋</span>
          <span>Jobs</span>
        </Link>
        <Link
          href="/matches"
          className={`nav-link ${
            pathname.startsWith("/matches") ? "active" : ""
          }`}
        >
          <span className="nav-icon">✨</span>
          <span>Matches</span>
        </Link>
      </nav>

      <div className="sidebar-footer">
        <button className="nav-link" onClick={handleLogout}>
          <span className="nav-icon">🚪</span>
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
