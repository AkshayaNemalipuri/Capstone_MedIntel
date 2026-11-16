```jsx
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  // Demo login state
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  // Patient management state
  const [patientId, setPatientId] = useState("");
  const [patient, setPatient] = useState(null);
  const [history, setHistory] = useState([]);
  const [reports, setReports] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [activeTab, setActiveTab] = useState("patient");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Demo login only. Connect to a real authentication API before production.
  const handleLogin = (event) => {
    event.preventDefault();

    if (!email.trim() || !password) {
      setMessage("Please enter your email and password.");
      return;
    }

    setMessage("");
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setEmail("");
    setPassword("");
    setPatientId("");
    setPatient(null);
    setHistory([]);
    setReports([]);
    setTimeline([]);
    setMessage("");
  };

  // Fetch patient information
  const loadPatient = async () => {
    if (!patientId.trim()) {
      setMessage("Please enter a Patient ID.");
      return;
    }

    setLoading(true);
    setMessage("");
    setPatient(null);
    setHistory([]);
    setReports([]);
    setTimeline([]);

    try {
      const response = await fetch(
        `${API_URL}/patients/${encodeURIComponent(patientId)}`
      );

      if (!response.ok) {
        throw new Error(
          response.status === 404
            ? "Patient not found. Please check the Patient ID."
            : "Unable to load patient information."
        );
      }

      const data = await response.json();
      setPatient(data);

      // Load related patient data
      await Promise.all([
        loadHistory(patientId),
        loadReports(patientId),
        loadTimeline(patientId),
      ]);

      setMessage("Patient records loaded successfully.");
    } catch (error) {
      setPatient(null);
      setMessage(error.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  // Load medical history
  const loadHistory = async (id = patientId) => {
    try {
      const response = await fetch(
        `${API_URL}/patients/${encodeURIComponent(id)}/medical-history`
      );

      if (response.ok) {
        const data = await response.json();
        setHistory(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error("Unable to load medical history:", error);
    }
  };

  // Load medical reports
  const loadReports = async (id = patientId) => {
    try {
      const response = await fetch(
        `${API_URL}/patients/${encodeURIComponent(id)}/reports`
      );

      if (response.ok) {
        const data = await response.json();
        setReports(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error("Unable to load medical reports:", error);
    }
  };

  // Load health timeline
  const loadTimeline = async (id = patientId) => {
    try {
      const response = await fetch(
        `${API_URL}/patients/${encodeURIComponent(id)}/timeline`
      );

      if (response.ok) {
        const data = await response.json();
        setTimeline(Array.isArray(data.timeline) ? data.timeline : []);
      }
    } catch (error) {
      console.error("Unable to load health timeline:", error);
    }
  };

  // Upload medical report
  const uploadReport = async (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    if (!patient) {
      setMessage("Please load a patient before uploading a report.");
      event.target.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setMessage("Uploading medical report...");

      const response = await fetch(
        `${API_URL}/patients/${encodeURIComponent(patientId)}/reports`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Report upload failed.");
      }

      setMessage("Medical report uploaded successfully.");

      await Promise.all([
        loadReports(patientId),
        loadTimeline(patientId),
      ]);
    } catch (error) {
      setMessage(error.message || "Report upload failed.");
    } finally {
      event.target.value = "";
    }
  };

  // Download medical report
  const downloadReport = (reportId, reportName) => {
    const url = `${API_URL}/reports/${reportId}/download`;
    const link = document.createElement("a");

    link.href = url;
    link.download = reportName || "medical-report";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // LOGIN PAGE
  if (!isLoggedIn) {
    return (
      <main className="login-page">
        <div className="login-brand">
          <span className="brand-icon">✚</span>
          <h1>MedIntel</h1>
          <p>Intelligent Healthcare Records</p>
        </div>

        <section className="login-card">
          <h2>Welcome Back</h2>
          <p className="login-subtitle">
            Sign in to access patient health records.
          </p>

          <form onSubmit={handleLogin}>
            <label htmlFor="login-email">Email Address</label>
            <input
              id="login-email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="username"
              required
            />

            <label htmlFor="login-password">Password</label>
            <div className="password-field">
              <input
                id="login-password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
              />

              <button
                type="button"
                className="show-password"
                onClick={() => setShowPassword((value) => !value)}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>

            {message && <p className="login-message">{message}</p>}

            <button type="submit" className="login-button">
              Sign In
            </button>
          </form>

          <p className="login-footer">
            MedIntel · Intelligent Healthcare
          </p>
        </section>

        <p className="login-note">
          Authorized healthcare personnel only
        </p>
      </main>
    );
  }

  // PATIENT DASHBOARD
  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <span className="brand-icon">✚</span>
          <div>
            <h1>MedIntel</h1>
            <p>Patient Health Records</p>
          </div>
        </div>

        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </header>

      <main className="dashboard">
        <section className="search-section">
          <h2>Find Patient</h2>
          <p>Enter a patient ID to view their health records.</p>

          <form
            className="search-box"
            onSubmit={(event) => {
              event.preventDefault();
              loadPatient();
            }}
          >
            <input
              type="number"
              min="1"
              placeholder="Enter Patient ID"
              value={patientId}
              onChange={(event) => setPatientId(event.target.value)}
              aria-label="Patient ID"
              required
            />

            <button type="submit" disabled={loading}>
              {loading ? "Loading..." : "Load Patient"}
            </button>
          </form>

          {message && (
            <p className="message" role="status">
              {message}
            </p>
          )}
        </section>

        {patient && (
          <>
            <section className="patient-card">
              <h2>Patient Information</h2>

              <div className="patient-grid">
                <div>
                  <span>Name</span>
                  <strong>{patient.name || "Not provided"}</strong>
                </div>

                <div>
                  <span>Age</span>
                  <strong>{patient.age ?? "Not provided"}</strong>
                </div>

                <div>
                  <span>Gender</span>
                  <strong>{patient.gender || "Not provided"}</strong>
                </div>

                <div>
                  <span>Blood Group</span>
                  <strong>{patient.blood_group || "Not provided"}</strong>
                </div>

                <div>
                  <span>Phone</span>
                  <strong>{patient.phone || "Not provided"}</strong>
                </div>

                <div>
                  <span>Email</span>
                  <strong>{patient.email || "Not provided"}</strong>
                </div>
              </div>
            </section>

            <nav className="tabs" aria-label="Patient record sections">
              <button
                className={activeTab === "patient" ? "active" : ""}
                onClick={() => setActiveTab("patient")}
              >
                👤 Patient Details
              </button>

              <button
                className={activeTab === "history" ? "active" : ""}
                onClick={() => setActiveTab("history")}
              >
                🩺 Medical History
              </button>

              <button
                className={activeTab === "reports" ? "active" : ""}
                onClick={() => setActiveTab("reports")}
              >
                📄 Medical Reports
              </button>

              <button
                className={activeTab === "timeline" ? "active" : ""}
                onClick={() => setActiveTab("timeline")}
              >
                🕐 Health Timeline
              </button>
            </nav>

            {activeTab === "patient" && (
              <section className="content-card">
                <h2>Patient Details</h2>

                <p>
                  <strong>Allergies:</strong>{" "}
                  {patient.allergies || "None recorded"}
                </p>

                <p>
                  <strong>Medical History:</strong>{" "}
                  {patient.medical_history || "None recorded"}
                </p>
              </section>
            )}

            {activeTab === "history" && (
              <section className="content-card">
                <h2>Medical History</h2>

                {history.length === 0 ? (
                  <p>No medical history available.</p>
                ) : (
                  history.map((item) => (
                    <article className="history-item" key={item.id}>
                      <h3>{item.condition}</h3>

                      <p>
                        <strong>Diagnosis Date:</strong>{" "}
                        {item.diagnosis_date || "Not provided"}
                      </p>

                      <p>
                        <strong>Treatment:</strong>{" "}
                        {item.treatment || "Not provided"}
                      </p>

                      <p>
                        <strong>Medications:</strong>{" "}
                        {item.medications || "Not provided"}
                      </p>

                      <p>
                        <strong>Doctor:</strong>{" "}
                        {item.doctor_name || "Not provided"}
                      </p>

                      <p>
                        <strong>Notes:</strong> {item.notes || "None"}
                      </p>
                    </article>
                  ))
                )}
              </section>
            )}

            {activeTab === "reports" && (
              <section className="content-card">
                <div className="reports-header">
                  <h2>Medical Reports</h2>

                  <label className="upload-button">
                    📤 Upload Report
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={uploadReport}
                      hidden
                    />
                  </label>
                </div>

                {reports.length === 0 ? (
                  <p>No medical reports available.</p>
                ) : (
                  <div className="reports-list">
                    {reports.map((report) => (
                      <article className="report-item" key={report.id}>
                        <div>
                          <h3>📄 {report.report_name}</h3>
                          <p>Type: {report.file_type || "Unknown"}</p>
                          <p>
                            Uploaded: {report.upload_date || "Not available"}
                          </p>
                        </div>

                        <button
                          onClick={() =>
                            downloadReport(report.id, report.report_name)
                          }
                        >
                          📥 Download
                        </button>
                      </article>
                    ))}
                  </div>
                )}
              </section>
            )}

            {activeTab === "timeline" && (
              <section className="content-card">
                <h2>Health Timeline</h2>

                {timeline.length === 0 ? (
                  <p>No timeline events available.</p>
                ) : (
                  <div className="timeline">
                    {timeline.map((event, index) => (
                      <article
                        className="timeline-item"
                        key={`${event.type}-${event.date}-${index}`}
                      >
                        <div className="timeline-dot" />

                        <div className="timeline-content">
                          <span className="timeline-date">
                            {event.date || "Date unavailable"}
                          </span>

                          <h3>
                            {event.type === "medical_report"
                              ? "📄 Medical Report"
                              : "🩺 Medical History"}
                          </h3>

                          <h4>{event.title}</h4>

                          {event.type === "medical_history" && (
                            <>
                              <p>
                                <strong>Doctor:</strong>{" "}
                                {event.details?.doctor_name || "N/A"}
                              </p>

                              <p>
                                <strong>Treatment:</strong>{" "}
                                {event.details?.treatment || "N/A"}
                              </p>
                            </>
                          )}

                          {event.type === "medical_report" && (
                            <p>
                              File Type: {event.details?.file_type || "N/A"}
                            </p>
                          )}
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </section>
            )}
          </>
        )}
      </main>

      <footer className="app-footer">
        MedIntel · Intelligent Healthcare Records
      </footer>
    </div>
  );
}

export default App;
```