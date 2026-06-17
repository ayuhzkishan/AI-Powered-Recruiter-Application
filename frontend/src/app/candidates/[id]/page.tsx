"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";
import { useParams } from "next/navigation";

export default function CandidateDetailPage() {
  const params = useParams();
  const [candidate, setCandidate] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCandidate = async () => {
      try {
        const { data } = await api.get(`/api/candidates/${params.id}`);
        setCandidate(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchCandidate();
  }, [params.id]);

  if (loading) return <div className="app-layout"><Sidebar /><div className="main-content"><span className="loading-spinner"/></div></div>;
  if (!candidate) return <div className="app-layout"><Sidebar /><div className="main-content">Not found</div></div>;

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header">
          <h1 className="page-title">{candidate.first_name} {candidate.last_name}</h1>
          <p className="page-subtitle">{candidate.email} • {candidate.phone || "No phone"}</p>
        </div>

        <div className="detail-grid">
          <div className="card">
            <h3 className="detail-section-title">Profile Summary</h3>
            <p className="text-secondary mb-md" style={{fontSize: "0.95rem"}}>
              {candidate.ai_analysis?.summary || "No summary available."}
            </p>

            <div className="detail-item">
              <div className="detail-item-label">Experience</div>
              <div className="detail-item-value">{candidate.ai_analysis?.years_experience || 0} years</div>
            </div>
            
            <h3 className="detail-section-title mt-lg">Hard Skills</h3>
            <div className="skill-chips mb-md">
              {candidate.ai_analysis?.skills?.hard?.map((s: string) => (
                <span key={s} className="skill-chip">{s}</span>
              ))}
            </div>

            <h3 className="detail-section-title">Soft Skills</h3>
            <div className="skill-chips">
              {candidate.ai_analysis?.skills?.soft?.map((s: string) => (
                <span key={s} className="skill-chip soft">{s}</span>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="detail-section-title">Experience Timeline</h3>
            {candidate.ai_analysis?.experience?.map((exp: any, i: number) => (
              <div key={i} className="detail-item">
                <div className="detail-item-value">{exp.title}</div>
                <div className="detail-item-label">{exp.company} • {Math.round(exp.duration_months / 12)} yrs</div>
              </div>
            ))}

            <h3 className="detail-section-title mt-lg">Education</h3>
            {candidate.ai_analysis?.education?.map((edu: any, i: number) => (
              <div key={i} className="detail-item">
                <div className="detail-item-value">{edu.degree}</div>
                <div className="detail-item-label">{edu.institution} • {edu.year}</div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
