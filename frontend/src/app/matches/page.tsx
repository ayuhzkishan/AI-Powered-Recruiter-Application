"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";
import { MatchScoreRing } from "@/components/MatchScoreRing";

export default function MatchesPage() {
  const [matches, setMatches] = useState<any[]>([]);

  const fetchMatches = async () => {
    const { data } = await api.get("/api/matches");
    setMatches(data);
  };

  useEffect(() => { fetchMatches(); }, []);

  const updateStatus = async (id: string, status: string) => {
    await api.put(`/api/matches/${id}/review?status=${status}`);
    fetchMatches();
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header">
          <h1 className="page-title">Match Results</h1>
          <p className="page-subtitle">AI-driven candidate fit analysis</p>
        </div>

        <div className="flex-col gap-lg">
          {matches.map(m => (
            <div key={m.id} className="card">
              <div className="flex justify-between items-center mb-md">
                <div className="flex items-center gap-lg">
                  <MatchScoreRing score={m.match_score} />
                  <div>
                    <h2 className="detail-section-title mb-0">{m.candidate_name}</h2>
                    <div className="text-secondary" style={{fontSize: "0.9rem"}}>{m.job_title} • {m.department}</div>
                  </div>
                </div>
                <div className="flex gap-sm">
                  <button className="btn btn-secondary" onClick={() => updateStatus(m.id, "shortlisted")}>Shortlist</button>
                  <button className="btn btn-ghost" onClick={() => updateStatus(m.id, "rejected")}>Reject</button>
                  <span className={`badge badge-${m.review_status} ml-sm`}>{m.review_status}</span>
                </div>
              </div>

              {m.fit_analysis && (
                <div className="detail-grid mt-lg">
                  <div className="detail-item">
                    <div className="detail-item-label">Strengths</div>
                    {m.fit_analysis.strengths?.map((s: string, i: number) => (
                      <div key={i} className="fit-item strength">{s}</div>
                    ))}
                  </div>
                  <div className="detail-item">
                    <div className="detail-item-label">Gaps</div>
                    {m.fit_analysis.gaps?.map((s: string, i: number) => (
                      <div key={i} className="fit-item gap">{s}</div>
                    ))}
                  </div>
                </div>
              )}
              
              {m.fit_analysis?.reasoning && (
                <div className="mt-md p-md bg-glass rounded-md border border-border-color p-4" style={{borderRadius: 12, padding: 16, background: "var(--bg-glass)"}}>
                  <div className="detail-item-label">AI Reasoning</div>
                  <div className="text-secondary text-sm" style={{fontSize: "0.85rem"}}>{m.fit_analysis.reasoning}</div>
                </div>
              )}
            </div>
          ))}
          {matches.length === 0 && (
            <div className="empty-state card">
               <div className="empty-state-icon">⚖️</div>
               <div className="empty-state-title">No matches yet</div>
               <p className="empty-state-text">Go to a Job to trigger AI matching for candidates.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
