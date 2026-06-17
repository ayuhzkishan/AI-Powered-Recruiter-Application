"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";
import Link from "next/link";

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ title: "", department: "", raw_description: "", minimum_experience_years: 0 });

  const fetchJobs = async () => {
    const { data } = await api.get("/api/jobs");
    setJobs(data);
  };

  useEffect(() => { fetchJobs(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/api/jobs", formData);
    setShowModal(false);
    fetchJobs();
  };

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header flex justify-between items-center">
          <div>
            <h1 className="page-title">Job Postings</h1>
            <p className="page-subtitle">Manage open roles</p>
          </div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>Create Job</button>
        </div>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Department</th>
                <th>Status</th>
                <th>Min. Exp</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map(j => (
                <tr key={j.id}>
                  <td className="name-cell">{j.title}</td>
                  <td>{j.department}</td>
                  <td><span className={`badge badge-${j.status}`}>{j.status}</span></td>
                  <td>{j.minimum_experience_years} yrs</td>
                  <td><Link href={`/jobs/${j.id}`} className="btn btn-ghost btn-sm">Manage</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {showModal && (
          <div className="modal-overlay">
            <div className="modal-content">
              <h2 className="modal-title">Create Job Description</h2>
              <form onSubmit={handleCreate}>
                <div className="form-group">
                  <label className="form-label">Title</label>
                  <input type="text" className="form-input" required value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} />
                </div>
                <div className="form-group">
                  <label className="form-label">Department</label>
                  <input type="text" className="form-input" value={formData.department} onChange={e => setFormData({...formData, department: e.target.value})} />
                </div>
                <div className="form-group">
                  <label className="form-label">Min Experience (Years)</label>
                  <input type="number" className="form-input" min="0" value={formData.minimum_experience_years} onChange={e => setFormData({...formData, minimum_experience_years: parseInt(e.target.value)})} />
                </div>
                <div className="form-group">
                  <label className="form-label">Full Description (Paste JD here)</label>
                  <textarea className="form-input form-textarea" required minLength={50} value={formData.raw_description} onChange={e => setFormData({...formData, raw_description: e.target.value})} />
                </div>
                <div className="modal-actions">
                  <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary">Create Job</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
