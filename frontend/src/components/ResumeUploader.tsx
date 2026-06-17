"use client";
import { useState, useCallback } from "react";
import api from "@/lib/api";

type UploadStatus = "idle" | "uploading" | "processing" | "complete" | "error";

export function ResumeUploader({ onComplete, title = "Upload New Candidate" }: { onComplete?: () => void, title?: string }) {
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");

  const pollStatus = useCallback(async (candidateId: string) => {
    const interval = setInterval(async () => {
      try {
        const { data } = await api.get(`/api/candidates/${candidateId}/status`);
        if (data.status === "complete") {
          clearInterval(interval);
          setStatus("complete");
          if (onComplete) onComplete();
        } else if (data.status === "failed") {
          clearInterval(interval);
          setStatus("error");
          setError("Analysis failed. Please check the file and try again.");
        }
      } catch {
        clearInterval(interval);
        setStatus("error");
        setError("Error checking status.");
      }
    }, 3000); // Poll every 3 seconds
  }, [onComplete]);

  const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const fileInput = form.elements.namedItem("file") as HTMLInputElement;
    const file = fileInput.files?.[0];

    if (!file) {
      setError("Please select a file");
      return;
    }

    // Client-side pre-validation
    if (file.size > 5 * 1024 * 1024) {
      setError("File must be under 5MB");
      return;
    }
    if (
      ![
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      ].includes(file.type) &&
      !file.name.endsWith(".pdf") &&
      !file.name.endsWith(".docx")
    ) {
      setError("Only PDF and DOCX files are accepted");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("first_name", firstName);
    formData.append("last_name", lastName);
    formData.append("email", email);
    if (phone) formData.append("phone", phone);

    try {
      setStatus("uploading");
      setError(null);
      const { data } = await api.post("/api/candidates/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus("processing");
      await pollStatus(data.candidate_id);
    } catch (err: any) {
      setStatus("error");
      setError(
        err.response?.data?.detail || "Upload failed. Please try again."
      );
    }
  };

  return (
    <div className="card">
      <h3 className="detail-section-title">{title}</h3>

      {status === "idle" || status === "error" ? (
        <form onSubmit={handleUpload}>
          <div className="detail-grid">
            <div className="form-group">
              <label className="form-label">First Name *</label>
              <input
                type="text"
                className="form-input"
                required
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Last Name *</label>
              <input
                type="text"
                className="form-input"
                required
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Email *</label>
              <input
                type="email"
                className="form-input"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Phone</label>
              <input
                type="text"
                className="form-input"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
          </div>
          
          <div className="form-group">
             <label className="form-label">Resume (PDF/DOCX) *</label>
             <input type="file" name="file" accept=".pdf,.docx" required className="form-input" />
          </div>

          {error && <p className="form-error">{error}</p>}
          
          <button type="submit" className="btn btn-primary mt-md">Upload & Analyze</button>
        </form>
      ) : status === "uploading" ? (
        <div className="empty-state">
           <div className="loading-spinner mb-md" />
           <div className="empty-state-title">Uploading...</div>
        </div>
      ) : status === "processing" ? (
        <div className="empty-state">
           <div className="loading-spinner mb-md" />
           <div className="empty-state-title">AI is analyzing resume...</div>
           <p className="empty-state-text">Extracting skills, education, and experience. This may take 10-20 seconds.</p>
        </div>
      ) : (
         <div className="empty-state">
           <div className="empty-state-icon" style={{color: "var(--accent-emerald)", opacity: 1}}>✅</div>
           <div className="empty-state-title">Analysis Complete!</div>
           <button className="btn btn-secondary mt-md" onClick={() => {
              setStatus("idle");
              setFirstName("");
              setLastName("");
              setEmail("");
              setPhone("");
           }}>Upload Another</button>
        </div>
      )}
    </div>
  );
}
