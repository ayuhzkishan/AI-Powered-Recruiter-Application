"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import api from "@/lib/api";
import { ResumeUploader } from "@/components/ResumeUploader";

type Job = {
  id: string;
  title: string;
  department: string;
  raw_description: string;
};

export default function CandidateApplyPage() {
  const { jobId } = useParams();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [applied, setApplied] = useState(false);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const { data } = await api.get(`/api/jobs/${jobId}`);
        setJob(data);
      } catch (err) {
        console.error(err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    if (jobId) fetchJob();
  }, [jobId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center" style={{ minHeight: "100vh" }}>
        <div className="loading-spinner" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="flex justify-center items-center" style={{ minHeight: "100vh" }}>
        <div className="empty-state">
          <h2>Job Not Found</h2>
          <p className="text-muted">This job post may have expired or does not exist.</p>
        </div>
      </div>
    );
  }

  if (applied) {
    return (
      <div className="flex justify-center items-center" style={{ minHeight: "100vh", padding: 20 }}>
        <div className="card" style={{ maxWidth: 600, width: "100%", textAlign: "center" }}>
          <div className="empty-state-icon" style={{color: "var(--accent-emerald)", opacity: 1}}>✅</div>
          <h2 className="mb-sm">Application Submitted!</h2>
          <p className="text-muted mb-lg">Thank you for applying for the <strong>{job.title}</strong> role. Our recruitment team will review your application shortly.</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "40px 20px" }}>
      <div className="mb-xl">
        <h1 className="page-title">{job.title}</h1>
        <div className="badge badge-draft mt-sm">{job.department}</div>
      </div>
      
      <div className="card mb-xl">
        <h3 className="detail-section-title">Job Description</h3>
        <div style={{ whiteSpace: "pre-wrap", color: "var(--text-secondary)", lineHeight: 1.6 }}>
          {job.raw_description}
        </div>
      </div>

      <div id="apply-section">
        <ResumeUploader 
          title="Submit Your Application" 
          onComplete={() => setApplied(true)}
        />
      </div>
    </div>
  );
}
