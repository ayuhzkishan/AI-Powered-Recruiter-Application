"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";
import { useParams } from "next/navigation";
import { MatchScoreRing } from "@/components/MatchScoreRing";
import Link from "next/link";

export default function JobDetailPage() {
  const params = useParams();
  const [job, setJob] = useState<any>(null);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [jobRes, candRes] = await Promise.all([
        api.get(`/api/jobs/${params.id}`),
        api.get("/api/candidates")
      ]);
      setJob(jobRes.data);
      // Only show fully analyzed candidates
      setCandidates(candRes.data.filter((c: any) => c.processing_status === "complete"));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [params.id]);

  const handleMatch = async () => {
    if (!selectedCandidateId) return;
    try {
      await api.post(`/api/matches/${selectedCandidateId}/match/${params.id}`);
      // Poll or just wait a bit and refresh
      setTimeout(fetchData, 4000);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) return <div className="app-layout"><Sidebar /><div className="main-content"><span className="loading-spinner"/></div></div>;
  if (!job) return <div className="app-layout"><Sidebar /><div className="main-content">Job not found or access denied.</div></div>;

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header">
          <h1 className="page-title">{job.title}</h1>
          <p className="page-subtitle">{job.department} • Min {job.minimum_experience_years} yrs exp</p>
        </div>

        <div className="card mb-lg">
          <h3 className="detail-section-title">Trigger AI Match</h3>
          <div className="flex gap-md items-center">
            <select 
              className="form-input flex-1" 
              value={selectedCandidateId} 
              onChange={e => setSelectedCandidateId(e.target.value)}
            >
              <option value="">Select a candidate to evaluate...</option>
              {candidates.map(c => (
                <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>
              ))}
            </select>
            <button className="btn btn-primary" onClick={handleMatch} disabled={!selectedCandidateId}>
              Generate Score
            </button>
          </div>
        </div>

        <h2 className="detail-section-title mt-lg">Matched Candidates</h2>
        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Score</th>
                <th>Candidate</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {job.matches?.map((m: any) => (
                <tr key={m.id}>
                  <td style={{width: 100}}><MatchScoreRing score={m.match_score} size={48} /></td>
                  <td className="name-cell">{m.candidate_name}</td>
                  <td><span className={`badge badge-${m.review_status}`}>{m.review_status}</span></td>
                  <td><Link href="/matches" className="btn btn-ghost btn-sm">View Analysis</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
