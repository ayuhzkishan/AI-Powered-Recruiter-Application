"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { setToken, enterDemoMode } from "@/lib/auth";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const { data } = await api.post("/api/auth/login", { email, password });
      setToken(data.access_token);
      router.push("/dashboard");
    } catch {
      setError("Invalid email or password. Try the demo shortcut below.");
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    enterDemoMode();
    router.push("/dashboard");
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Logo mark */}
        <div style={{ textAlign: "center", marginBottom: 8 }}>
          <div
            style={{
              width: 52,
              height: 52,
              borderRadius: 12,
              background: "#2B2B2B",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 26,
              marginBottom: 16,
            }}
          >
            🧠
          </div>
        </div>

        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-subtitle">Sign in to your recruiter dashboard</p>

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="login-email" className="form-label">
              Email
            </label>
            <input
              id="login-email"
              type="email"
              className="form-input"
              placeholder="recruiter@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="login-password" className="form-label">
              Password
            </label>
            <input
              id="login-password"
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <p className="form-error">{error}</p>}

          <button
            type="submit"
            id="login-submit"
            className="btn btn-primary btn-lg w-full"
            disabled={loading}
            style={{ marginTop: 8 }}
          >
            {loading ? (
              <>
                <span className="loading-spinner" /> Signing in...
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        {/* Divider */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            margin: "20px 0",
          }}
        >
          <div style={{ flex: 1, height: 1, background: "var(--border-color)" }} />
          <span style={{ fontSize: "0.78rem", color: "var(--text-muted)", whiteSpace: "nowrap" }}>
            or for demo
          </span>
          <div style={{ flex: 1, height: 1, background: "var(--border-color)" }} />
        </div>

        {/* Skip button */}
        <button
          id="demo-skip"
          type="button"
          className="btn btn-secondary btn-lg w-full"
          onClick={handleSkip}
          style={{
            borderStyle: "dashed",
            color: "var(--text-secondary)",
          }}
        >
          ⚡ Skip — Enter as Demo Recruiter
        </button>

        <p className="auth-footer" style={{ marginTop: 20 }}>
          Don&apos;t have an account?{" "}
          <Link href="/signup">Create one</Link>
        </p>
      </div>
    </div>
  );
}
