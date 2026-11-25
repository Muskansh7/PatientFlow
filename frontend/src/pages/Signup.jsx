import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Activity, User, Mail, Lock, ArrowRight } from "lucide-react";
import api from "../services/api";

export default function Signup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("/auth/signup", {
        name,
        email,
        password,
});

      navigate("/", {
        state: { message: "Account created successfully. Please sign in." },
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-brand">
        <div className="brand-icon">
          <Activity size={24} />
        </div>
        <span>PatientFlow</span>
      </div>

      <div className="auth-card">
        <div className="auth-heading">
          <span className="eyebrow">GET STARTED</span>
          <h1>Create your account</h1>
          <p>Set up your workspace for better patient management.</p>
        </div>

        <form onSubmit={handleSignup}>
          <div className="form-field">
            <label>Full name</label>
            <div className="input-wrapper">
              <User size={18} />
              <input
                type="text"
                placeholder="Your full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-field">
            <label>Email address</label>
            <div className="input-wrapper">
              <Mail size={18} />
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-field">
            <label>Password</label>
            <div className="input-wrapper">
              <Lock size={18} />
              <input
                type="password"
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                required
              />
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button className="auth-button" disabled={loading}>
            {loading ? "Creating account..." : "Create account"}
            {!loading && <ArrowRight size={18} />}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/">Sign in</Link>
        </div>
      </div>

      <div className="auth-bottom">
        PatientFlow · Patient Admission Management
      </div>
    </div>
  );
}