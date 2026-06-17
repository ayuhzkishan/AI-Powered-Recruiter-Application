"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";
import { ResumeUploader } from "@/components/ResumeUploader";
import Link from "next/link";

type Candidate = {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  processing_status: string;
  years_experience: number;
};

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [showUpload, setShowUpload] = useState(false);

  const fetchCandidates = async () => {
    try {
      const { data } = await api.get("/api/candidates");
      setCandidates(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, []);

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header flex justify-between items-center">
          <div>
            <h1 className="page-title">Candidates</h1>
            <p className="page-subtitle">Manage and upload resumes</p>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => setShowUpload(!showUpload)}
          >
            {showUpload ? "Cancel" : "Upload Resume"}
          </button>
        </div>

        {showUpload && (
          <div className="mb-md">
            <ResumeUploader
              onComplete={() => {
                fetchCandidates();
              }}
            />
          </div>
        )}

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Status</th>
                <th>Experience</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <tr key={c.id}>
                  <td className="name-cell">
                    {c.first_name} {c.last_name}
                  </td>
                  <td>{c.email}</td>
                  <td>
                    <span className={`badge badge-${c.processing_status}`}>
                      {c.processing_status}
                    </span>
                  </td>
                  <td>{c.years_experience ?? "-"} yrs</td>
                  <td>
                    <Link
                      href={`/candidates/${c.id}`}
                      className="btn btn-ghost btn-sm"
                    >
                      View Profile
                    </Link>
                  </td>
                </tr>
              ))}
              {candidates.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center" style={{ padding: 40 }}>
                    No candidates found. Upload a resume to get started.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
