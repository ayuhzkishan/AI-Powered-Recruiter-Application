"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function Dashboard() {
  const [stats, setStats] = useState({
    candidates: 0,
    jobs: 0,
    matches: 0,
  });

  useEffect(() => {
    // Quick and dirty stats via existing endpoints
    const fetchStats = async () => {
      try {
        const [cRes, jRes, mRes] = await Promise.all([
          api.get("/api/candidates"),
          api.get("/api/jobs"),
          api.get("/api/matches"),
        ]);
        setStats({
          candidates: cRes.data.length,
          jobs: jRes.data.length,
          matches: mRes.data.length,
        });
      } catch (err) {
        console.error(err);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header">
          <h1 className="page-title">Overview</h1>
          <p className="page-subtitle">Your recruitment pipeline at a glance</p>
        </div>

        <div className="stats-grid">
          <div className="stat-card emerald">
            <div className="stat-card-label">Total Candidates</div>
            <div className="stat-card-value">{stats.candidates}</div>
            <div className="stat-card-sub">Analyzed by AI</div>
            <div className="stat-card-icon">👥</div>
          </div>
          <div className="stat-card purple">
            <div className="stat-card-label">Active Jobs</div>
            <div className="stat-card-value">{stats.jobs}</div>
            <div className="stat-card-sub">Ready for matching</div>
            <div className="stat-card-icon">📋</div>
          </div>
          <div className="stat-card blue">
            <div className="stat-card-label">Matches Generated</div>
            <div className="stat-card-value">{stats.matches}</div>
            <div className="stat-card-sub">Across all roles</div>
            <div className="stat-card-icon">✨</div>
          </div>
        </div>
      </main>
    </div>
  );
}
