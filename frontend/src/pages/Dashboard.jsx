
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Activity, LogOut, Users, BedDouble, UserCheck, Clock,
  Plus, Search, Pencil, Trash2, CheckCircle, X,
  RefreshCw, History
} from "lucide-react";
import api from "../services/api";

const wards = [
  "General Ward", "ICU", "Emergency", "Pediatric Ward", "Private Ward"
];

const doctors = [
  { name: "Dr. Amit Verma", department: "Cardiology" },
  { name: "Dr. Priya Sharma", department: "Neurology" },
  { name: "Dr. Rajesh Gupta", department: "Orthopedics" },
  { name: "Dr. Neha Singh", department: "Pediatrics" },
  { name: "Dr. Karan Mehta", department: "General Medicine" }
];

const wardCapacity = {
  "General Ward": 10,
  ICU: 5,
  Emergency: 8,
  "Pediatric Ward": 6,
  "Private Ward": 4
};

const genders = [
  "Male", "Female", "Transgender", "Non-binary",
  "Gender Fluid", "Agender", "Other", "Prefer not to say"
];

const initialForm = {
  name: "",
  age: "",
  gender: "",
  ward: "",
  department: "",
  doctor: "",
  admission_date: "",
  status: "Admitted"
};

export default function Dashboard() {
  const navigate = useNavigate();

  const [activeSection, setActiveSection] = useState("patients");
  const [patients, setPatients] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [wardFilter, setWardFilter] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [editingPatient, setEditingPatient] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyData, setHistoryData] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [historyPatient, setHistoryPatient] = useState("");

  const fetchPatients = useCallback(async () => {
    try {
      setLoading(true);

      const params = {};
      if (search.trim()) params.search = search.trim();
      if (statusFilter) params.status = statusFilter;
      if (wardFilter) params.ward = wardFilter;

      const res = await api.get("/patients/", { params });
      setPatients(res.data.items || []);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load patients.");
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, wardFilter]);

  const fetchStats = async () => {
    try {
      const res = await api.get("/analytics/");
      setStats(res.data);
    } catch {
      console.error("Unable to load analytics.");
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  useEffect(() => {
    fetchStats();
  }, []);

  const refreshData = async () => {
    await Promise.all([fetchPatients(), fetchStats()]);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/", { replace: true });
  };

  const openAddModal = () => {
    setEditingPatient(null);
    setForm({ ...initialForm });
    setFormError("");
    setModalOpen(true);
  };

  const openEditModal = (patient) => {
    setEditingPatient(patient);
    setForm({
      name: patient.name,
      age: patient.age,
      gender: patient.gender,
      ward: patient.ward,
      department: patient.department,
      doctor: patient.doctor,
      admission_date: patient.admission_date,
      status: patient.status
    });
    setFormError("");
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditingPatient(null);
    setForm({ ...initialForm });
    setFormError("");
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => {
      const updated = { ...prev, [name]: value };

      if (name === "doctor") {
        const selected = doctors.find((d) => d.name === value);
        updated.department = selected?.department || "";
      }

      return updated;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");

    if (!form.name.trim()) {
      setFormError("Patient name is required.");
      return;
    }

    if (!/^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$/.test(form.name.trim())) {
      setFormError("Name can contain letters, spaces, hyphens and apostrophes only.");
      return;
    }

    if (Number(form.age) < 0 || Number(form.age) > 120) {
      setFormError("Age must be between 0 and 120.");
      return;
    }

    if (!form.gender || !form.ward || !form.department || !form.doctor) {
      setFormError("Please complete all fields.");
      return;
    }

    if (!form.admission_date) {
      setFormError("Admission date is required.");
      return;
    }

    if (form.admission_date > new Date().toISOString().split("T")[0]) {
      setFormError("Admission date cannot be in the future.");
      return;
    }

    const payload = {
      ...form,
      name: form.name.trim(),
      age: Number(form.age)
    };

    try {
      setSaving(true);

      if (editingPatient) {
        await api.put(`/patients/${editingPatient.id}`, payload);
      } else {
        await api.post("/patients/", payload);
      }

      closeModal();
      await refreshData();
    } catch (err) {
      setFormError(err.response?.data?.detail || "Unable to save patient.");
    } finally {
      setSaving(false);
    }
  };

  const handleHistory = async (patientId) => {
    const patient = patients.find((p) => p.id === patientId);

    setHistoryPatient(patient?.name || "Patient");
    setHistoryOpen(true);
    setHistoryLoading(true);
    setHistoryError("");
    setHistoryData([]);

    try {
      const res = await api.get(`/patients/${patientId}/history`);
      setHistoryData(res.data);
    } catch (err) {
      setHistoryError(
        err.response?.data?.detail || "Unable to load patient history."
      );
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleDischarge = async (patient) => {
    if (patient.status === "Discharged") return;
    if (!window.confirm(`Discharge ${patient.name}?`)) return;

    try {
      await api.patch(`/patients/${patient.id}/discharge`);
      await refreshData();
    } catch (err) {
      alert(err.response?.data?.detail || "Unable to discharge patient.");
    }
  };

  const handleDelete = async (patient) => {
    if (!window.confirm(`Delete ${patient.name}? This action cannot be undone.`)) {
      return;
    }

    try {
      await api.delete(`/patients/${patient.id}`);
      await refreshData();
    } catch (err) {
      alert(err.response?.data?.detail || "Unable to delete patient.");
    }
  };

  const admittedPatients = patients.filter((p) => p.status === "Admitted");

  const getWardStats = (ward) => {
    const occupied = patients.filter(
      (p) => p.ward === ward && p.status === "Admitted"
    ).length;

    return {
      occupied,
      capacity: wardCapacity[ward],
      available: Math.max(wardCapacity[ward] - occupied, 0)
    };
  };

  const renderPatients = () => (
    <section className="dashboard-content">
      <div className="dashboard-panel">
        <div className="panel-heading patient-panel-heading">
          <div>
            <h2>Patient Records</h2>
            <p>View and manage patient admissions.</p>
          </div>

          <button className="add-patient-button" onClick={openAddModal}>
            <Plus size={18} />
            Add Patient
          </button>
        </div>

        <div className="patient-toolbar">
          <div className="patient-search">
            <Search size={18} />
            <input
              placeholder="Search patients..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All statuses</option>
            <option value="Admitted">Admitted</option>
            <option value="Discharged">Discharged</option>
          </select>

          <select value={wardFilter} onChange={(e) => setWardFilter(e.target.value)}>
            <option value="">All wards</option>
            {wards.map((ward) => (
              <option key={ward} value={ward}>{ward}</option>
            ))}
          </select>

          <button className="refresh-button" onClick={refreshData} title="Refresh">
            <RefreshCw size={17} />
          </button>
        </div>

        {error && <div className="dashboard-error">{error}</div>}

        {loading ? (
          <div className="table-loading">Loading patient records...</div>
        ) : patients.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon"><Users size={28} /></div>
            <h3>No patients found</h3>
            <p>Add a patient or adjust your search filters.</p>
          </div>
        ) : (
          <div className="patient-table-wrapper">
            <table className="patient-table">
              <thead>
                <tr>
                  <th>Patient</th>
                  <th>Age</th>
                  <th>Gender</th>
                  <th>Ward</th>
                  <th>Department</th>
                  <th>Doctor</th>
                  <th>Admission</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {patients.map((patient) => (
                  <tr key={patient.id}>
                    <td>
                      <div className="patient-name-cell">
                        <div className="patient-avatar">
                          {patient.name.charAt(0).toUpperCase()}
                        </div>
                        <strong>{patient.name}</strong>
                      </div>
                    </td>
                    <td>{patient.age}</td>
                    <td>{patient.gender}</td>
                    <td>{patient.ward}</td>
                    <td>{patient.department}</td>
                    <td>{patient.doctor}</td>
                    <td>{patient.admission_date}</td>
                    <td>
                      <span className={`status-badge ${patient.status.toLowerCase()}`}>
                        {patient.status}
                      </span>
                    </td>
                    <td>
                      <div className="patient-actions">
                        <button
                          title="Edit"
                          className="action-button edit"
                          onClick={() => openEditModal(patient)}
                        >
                          <Pencil size={16} />
                        </button>

                        <button
                          title="History"
                          className="action-button history"
                          onClick={() => handleHistory(patient.id)}
                        >
                          <History size={16} />
                        </button>

                        {patient.status === "Admitted" && (
                          <button
                            title="Discharge"
                            className="action-button discharge"
                            onClick={() => handleDischarge(patient)}
                          >
                            <CheckCircle size={16} />
                          </button>
                        )}

                        <button
                          title="Delete"
                          className="action-button delete"
                          onClick={() => handleDelete(patient)}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );

  const renderWards = () => (
    <section className="dashboard-content">
      <div className="panel-heading">
        <h2>Ward Management</h2>
        <p>Monitor ward occupancy and available beds.</p>
      </div>

      <div className="ward-grid">
        {wards.map((ward) => {
          const { occupied, capacity, available } = getWardStats(ward);
          const percentage = capacity ? (occupied / capacity) * 100 : 0;

          return (
            <div className="ward-card" key={ward}>
              <div className="ward-card-header">
                <BedDouble size={22} />
                <h3>{ward}</h3>
              </div>

              <div className="ward-counts">
                <div>
                  <span>Occupied</span>
                  <strong>{occupied}</strong>
                </div>
                <div>
                  <span>Available</span>
                  <strong>{available}</strong>
                </div>
                <div>
                  <span>Capacity</span>
                  <strong>{capacity}</strong>
                </div>
              </div>

              <div className="ward-progress">
                <div
                  className="ward-progress-fill"
                  style={{ width: `${Math.min(percentage, 100)}%` }}
                />
              </div>

              <span className="ward-percentage">
                {Math.round(percentage)}% occupied
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );

  const renderDoctors = () => (
    <section className="dashboard-content">
      <div className="panel-heading">
        <h2>Doctors Directory</h2>
        <p>Doctors and their departments.</p>
      </div>

      <div className="doctor-grid">
        {doctors.map((doctor) => {
          const assigned = patients.filter(
            (p) => p.doctor === doctor.name && p.status === "Admitted"
          );

          return (
            <div className="doctor-card" key={doctor.name}>
              <div className="doctor-avatar">
                <UserCheck size={24} />
              </div>
              <h3>{doctor.name}</h3>
              <p>{doctor.department}</p>
              <div className="doctor-patient-count">
                <Users size={16} />
                <span>{assigned.length} active patient(s)</span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );

  return (
    <div className="dashboard-page">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon"><Activity size={22} /></div>
          <span>PatientFlow</span>
        </div>

        <div className="sidebar-label">MENU</div>

        <div
          className={`sidebar-item ${activeSection === "patients" ? "active" : ""}`}
          onClick={() => setActiveSection("patients")}
        >
          <Users size={18} />
          <span>Patients</span>
        </div>

        <div
          className={`sidebar-item ${activeSection === "wards" ? "active" : ""}`}
          onClick={() => setActiveSection("wards")}
        >
          <BedDouble size={18} />
          <span>Wards</span>
        </div>

        <div
          className={`sidebar-item ${activeSection === "doctors" ? "active" : ""}`}
          onClick={() => setActiveSection("doctors")}
        >
          <UserCheck size={18} />
          <span>Doctors</span>
        </div>

        <div className="sidebar-bottom">
          <button className="logout-button" onClick={handleLogout}>
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <h1>
              {activeSection === "patients"
                ? "Patient Overview"
                : activeSection === "wards"
                ? "Ward Overview"
                : "Doctor Overview"}
            </h1>
            <p>
              {activeSection === "patients"
                ? "Manage hospital admissions and patient records."
                : activeSection === "wards"
                ? "Monitor hospital beds and ward capacity."
                : "View doctors and their assigned patients."}
            </p>
          </div>

          <div className="dashboard-date">
            <Clock size={17} />
            PatientFlow Management
          </div>
        </header>

        {activeSection === "patients" && (
          <>
            <section className="dashboard-stats">
              <div className="stat-card">
                <div className="stat-icon blue"><Users size={22} /></div>
                <div>
                  <p>Total Patients</p>
                  <h2>{stats?.total_patients ?? patients.length}</h2>
                  <span>All patient records</span>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon green"><UserCheck size={22} /></div>
                <div>
                  <p>Currently Admitted</p>
                  <h2>{stats?.admitted_patients ?? admittedPatients.length}</h2>
                  <span>Active admissions</span>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon orange"><BedDouble size={22} /></div>
                <div>
                  <p>Ward Occupancy</p>
                  <h2>{admittedPatients.length}</h2>
                  <span>Occupied beds</span>
                </div>
              </div>
            </section>

            {renderPatients()}
          </>
        )}

        {activeSection === "wards" && renderWards()}
        {activeSection === "doctors" && renderDoctors()}
      </main>

      {modalOpen && (
        <div className="patient-modal-overlay" onClick={closeModal}>
          <div className="patient-modal" onClick={(e) => e.stopPropagation()}>
            <div className="patient-modal-header">
              <div>
                <h2>{editingPatient ? "Edit Patient" : "Add New Patient"}</h2>
                <p>
                  {editingPatient
                    ? "Update patient information."
                    : "Enter patient admission details."}
                </p>
              </div>

              <button className="modal-close-button" onClick={closeModal}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="patient-form-grid">
                <div className="patient-form-field full">
                  <label>Full Name</label>
                  <input
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    placeholder="Patient name"
                    required
                  />
                </div>

                <div className="patient-form-field">
                  <label>Age</label>
                  <input
                    name="age"
                    type="number"
                    min="0"
                    max="120"
                    value={form.age}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="patient-form-field">
                  <label>Gender</label>
                  <select
                    name="gender"
                    value={form.gender}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select gender</option>
                    {genders.map((gender) => (
                      <option key={gender} value={gender}>{gender}</option>
                    ))}
                  </select>
                </div>

                <div className="patient-form-field">
                  <label>Ward</label>
                  <select
                    name="ward"
                    value={form.ward}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select ward</option>
                    {wards.map((ward) => (
                      <option key={ward} value={ward}>{ward}</option>
                    ))}
                  </select>
                </div>

                <div className="patient-form-field">
                  <label>Doctor</label>
                  <select
                    name="doctor"
                    value={form.doctor}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select doctor</option>
                    {doctors.map((doctor) => (
                      <option key={doctor.name} value={doctor.name}>
                        {doctor.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="patient-form-field">
                  <label>Department</label>
                  <input
                    name="department"
                    value={form.department}
                    readOnly
                    placeholder="Automatically selected"
                  />
                </div>

                <div className="patient-form-field">
                  <label>Admission Date</label>
                  <input
                    name="admission_date"
                    type="date"
                    max={new Date().toISOString().split("T")[0]}
                    value={form.admission_date}
                    onChange={handleChange}
                    required
                  />
                </div>

                {editingPatient && (
                  <div className="patient-form-field">
                    <label>Status</label>
                    <select
                      name="status"
                      value={form.status}
                      onChange={handleChange}
                    >
                      <option value="Admitted">Admitted</option>
                      <option value="Discharged">Discharged</option>
                    </select>
                  </div>
                )}
              </div>

              {formError && <div className="patient-form-error">{formError}</div>}

              <div className="patient-modal-footer">
                <button type="button" className="cancel-button" onClick={closeModal}>
                  Cancel
                </button>

                <button className="add-patient-button" disabled={saving}>
                  {saving
                    ? "Saving..."
                    : editingPatient
                    ? "Save Changes"
                    : "Add Patient"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {historyOpen && (
        <div
          className="patient-modal-overlay"
          onClick={() => setHistoryOpen(false)}
        >
          <div className="patient-modal" onClick={(e) => e.stopPropagation()}>
            <div className="patient-modal-header">
              <div>
                <h2>Patient History</h2>
                <p>{historyPatient}</p>
              </div>

              <button
                className="modal-close-button"
                onClick={() => setHistoryOpen(false)}
              >
                <X size={20} />
              </button>
            </div>

            <div className="history-content">
              {historyLoading ? (
                <p>Loading history...</p>
              ) : historyError ? (
                <p className="error-message">{historyError}</p>
              ) : !Array.isArray(historyData) || historyData.length === 0 ? (
                <p>No history available for this patient.</p>
              ) : (
                <div className="history-list">
                  {historyData.map((item, index) => (
                    <div className="history-item" key={index}>
                      <div className="history-marker" />
                      <div className="history-details">
                        <h4>{item.action || item.event || "Activity"}</h4>
                        <p>{item.details || item.description || ""}</p>
                        <span>
                          {item.timestamp || item.date || item.created_at || ""}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
