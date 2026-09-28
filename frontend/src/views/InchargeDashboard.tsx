import React, { useState, useEffect } from 'react';
import { api } from '../api';
import type { User, StudentEnrollment, Section, Subject } from '../types';
import { EmptyState } from '../components/EmptyState';
import {
  Users,
  UserCheck,
  Layers,
  BookOpen,
  PlusCircle,
  ShieldCheck,
} from 'lucide-react';

interface InchargeDashboardProps {
  initialTab?: 'dashboard' | 'approvals' | 'sections';
}

export const InchargeDashboard: React.FC<InchargeDashboardProps> = ({ initialTab = 'dashboard' }) => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'approvals' | 'sections'>(initialTab);
  const [stats, setStats] = useState<Record<string, number>>({});
  const [teachers, setTeachers] = useState<User[]>([]);
  const [enrollments, setEnrollments] = useState<StudentEnrollment[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [feedback, setFeedback] = useState<string | null>(null);

  // New section modal state
  const [showSecModal, setShowSecModal] = useState(false);
  const [newClassLevel, setNewClassLevel] = useState(10);
  const [newSectionName, setNewSectionName] = useState('');

  // New subject modal state
  const [showSubModal, setShowSubModal] = useState(false);
  const [newSubName, setNewSubName] = useState('');
  const [newSubCode, setNewSubCode] = useState('');

  // Assign teacher modal state
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [assignTeacherId, setAssignTeacherId] = useState('');
  const [assignSectionId, setAssignSectionId] = useState('');
  const [assignSubjectId, setAssignSubjectId] = useState('');

  const loadData = async () => {
    try {
      const [dashRes, teachRes, enrRes, secRes, subRes] = await Promise.all([
        api.getInchargeDashboard().catch(() => ({ stats: {} })),
        api.getInchargeTeachers().catch(() => []),
        api.getInchargeEnrollments().catch(() => []),
        api.getSections().catch(() => []),
        api.getSubjects().catch(() => []),
      ]);

      setStats(dashRes.stats || {});
      setTeachers(teachRes || []);
      setEnrollments(enrRes || []);
      setSections(secRes || []);
      setSubjects(subRes || []);
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApproveTeacher = async (teacherId: string, role: string) => {
    try {
      await api.approveTeacher(teacherId, role);
      setFeedback('Teacher approved successfully');
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleRejectTeacher = async (teacherId: string) => {
    try {
      await api.rejectTeacher(teacherId);
      setFeedback('Teacher rejected');
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleApproveEnrollment = async (enrollmentId: string) => {
    try {
      await api.approveInchargeEnrollment(enrollmentId);
      setFeedback('Student section enrollment approved');
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleRejectEnrollment = async (enrollmentId: string) => {
    try {
      await api.rejectInchargeEnrollment(enrollmentId);
      setFeedback('Student section enrollment rejected');
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleCreateSection = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createSection({
        class_level: Number(newClassLevel),
        section_name: newSectionName.trim(),
      });
      setShowSecModal(false);
      setNewSectionName('');
      setFeedback('Section created successfully');
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleCreateSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createSubject({
        name: newSubName.trim(),
        code: newSubCode.trim().toUpperCase(),
      });
      setShowSubModal(false);
      setNewSubName('');
      setNewSubCode('');
      setFeedback('Subject created successfully');
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleAssignTeacher = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.assignTeacherToSection({
        teacher_id: assignTeacherId,
        section_id: assignSectionId,
        subject_id: assignSubjectId,
      });
      setShowAssignModal(false);
      setFeedback('Teacher assigned to section and subject successfully');
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const pendingTeachers = teachers.filter((t) => t.status === 'PENDING_APPROVAL');
  const pendingEnrollments = enrollments.filter((e) => e.status === 'PENDING_APPROVAL');

  return (
    <div className="page-body">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1>School Incharge Workspace</h1>
          <p className="lead">Manage teacher onboarding, student section approvals, and academic structure.</p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`btn btn-sm ${activeTab === 'dashboard' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Overview
          </button>
          <button
            className={`btn btn-sm ${activeTab === 'approvals' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('approvals')}
          >
            Approvals Queue ({pendingTeachers.length + pendingEnrollments.length})
          </button>
          <button
            className={`btn btn-sm ${activeTab === 'sections' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('sections')}
          >
            Classes & Subjects
          </button>
        </div>
      </div>

      {feedback && (
        <div style={{
          background: 'var(--ok-bg)',
          color: 'var(--ok)',
          border: '1px solid rgba(47, 158, 68, 0.2)',
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          marginBottom: '20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>{feedback}</span>
          <button onClick={() => setFeedback(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}>✕</button>
        </div>
      )}

      {/* Overview Tab */}
      {activeTab === 'dashboard' && (
        <>
          <div className="stat-grid">
            <div className="stat-card">
              <span className="stat-label">Pending Teacher Approvals</span>
              <span className="stat-value" style={{ color: pendingTeachers.length > 0 ? 'var(--warn)' : 'var(--ink)' }}>
                {stats.pending_teacher_approvals ?? pendingTeachers.length}
              </span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Active Teachers</span>
              <span className="stat-value" style={{ color: 'var(--ok)' }}>
                {stats.active_teachers ?? teachers.filter(t => t.status === 'ACTIVE').length}
              </span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Pending Student Enrollments</span>
              <span className="stat-value" style={{ color: pendingEnrollments.length > 0 ? 'var(--warn)' : 'var(--ink)' }}>
                {stats.pending_student_enrollments ?? pendingEnrollments.length}
              </span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Total Classes & Sections</span>
              <span className="stat-value">{stats.total_sections ?? sections.length}</span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            {/* Quick Approvals Preview */}
            <div className="card">
              <div className="card-header">
                <h3>Teacher Approvals Pending</h3>
                <span className="badge badge-unverified">{pendingTeachers.length} Pending</span>
              </div>
              {pendingTeachers.length === 0 ? (
                <EmptyState
                  icon={<UserCheck size={24} />}
                  title="No Pending Teacher Approvals"
                  description="All teacher accounts registered for your school have been reviewed and approved."
                />
              ) : (
                <div className="table-container">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Teacher</th>
                        <th>Role</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pendingTeachers.slice(0, 3).map((t) => (
                        <tr key={t.id}>
                          <td>
                            <div style={{ fontWeight: 600 }}>{t.full_name}</div>
                            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>{t.email}</div>
                          </td>
                          <td><span className="badge badge-info">{t.role}</span></td>
                          <td>
                            <div style={{ display: 'flex', gap: '6px' }}>
                              <button
                                onClick={() => handleApproveTeacher(t.id, t.role)}
                                className="btn btn-sm btn-ok"
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => handleRejectTeacher(t.id)}
                                className="btn btn-sm btn-bad"
                              >
                                Reject
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

            {/* Quick Student Section Approvals */}
            <div className="card">
              <div className="card-header">
                <h3>Student Section Requests</h3>
                <span className="badge badge-unverified">{pendingEnrollments.length} Pending</span>
              </div>
              {pendingEnrollments.length === 0 ? (
                <EmptyState
                  icon={<Users size={24} />}
                  title="No Pending Student Requests"
                  description="All student section assignments are up to date."
                />
              ) : (
                <div className="table-container">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Student</th>
                        <th>Section</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pendingEnrollments.slice(0, 3).map((e) => (
                        <tr key={e.id}>
                          <td>
                            <div style={{ fontWeight: 600 }}>{e.student_name}</div>
                            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>{e.roll_number || e.student_email}</div>
                          </td>
                          <td><span className="id-chip">{e.section_name}</span></td>
                          <td>
                            <div style={{ display: 'flex', gap: '6px' }}>
                              <button
                                onClick={() => handleApproveEnrollment(e.id)}
                                className="btn btn-sm btn-ok"
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => handleRejectEnrollment(e.id)}
                                className="btn btn-sm btn-bad"
                              >
                                Reject
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
          </div>
        </>
      )}

      {/* Approvals Queue Tab */}
      {activeTab === 'approvals' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          {/* Teacher Approvals Section */}
          <div className="card">
            <div className="card-header">
              <div>
                <h2>Teacher Approval Queue</h2>
                <p className="lead">Review teachers requesting access under your school code.</p>
              </div>
            </div>

            {teachers.length === 0 ? (
              <EmptyState
                icon={<UserCheck size={24} />}
                title="No Teachers Registered"
                description="Share your school code with teachers to have them sign up."
              />
            ) : (
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Requested Role</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {teachers.map((t) => (
                      <tr key={t.id}>
                        <td style={{ fontWeight: 600 }}>{t.full_name}</td>
                        <td>{t.email}</td>
                        <td>
                          <span className="badge badge-info">{t.role}</span>
                        </td>
                        <td>
                          {t.status === 'ACTIVE' && <span className="badge badge-approved">Approved</span>}
                          {t.status === 'PENDING_APPROVAL' && <span className="badge badge-unverified">Pending</span>}
                          {t.status === 'REJECTED' && <span className="badge badge-rejected">Rejected</span>}
                        </td>
                        <td>
                          {t.status === 'PENDING_APPROVAL' ? (
                            <div style={{ display: 'flex', gap: '6px' }}>
                              <button
                                onClick={() => handleApproveTeacher(t.id, 'CLASS_TEACHER')}
                                className="btn btn-sm btn-ok"
                                title="Approve as Class Teacher"
                              >
                                Approve as Class Teacher
                              </button>
                              <button
                                onClick={() => handleApproveTeacher(t.id, 'SUBJECT_TEACHER')}
                                className="btn btn-sm btn-secondary"
                                title="Approve as Subject Teacher"
                              >
                                Approve as Subject Teacher
                              </button>
                              <button
                                onClick={() => handleRejectTeacher(t.id)}
                                className="btn btn-sm btn-bad"
                              >
                                Reject
                              </button>
                            </div>
                          ) : (
                            <span style={{ fontSize: '13px', color: 'var(--muted)' }}>Reviewed</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Student Enrollments Queue Section */}
          <div className="card">
            <div className="card-header">
              <div>
                <h2>Student Section Enrollment Approvals</h2>
                <p className="lead">Rules.md A.7: Incharge or Class Teacher approves student into section.</p>
              </div>
            </div>

            {enrollments.length === 0 ? (
              <EmptyState
                icon={<Users size={24} />}
                title="No Enrollment Requests"
                description="Students will appear here once they register and pick a section."
              />
            ) : (
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Student Name</th>
                      <th>Identifier</th>
                      <th>Target Section</th>
                      <th>Requested Date</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {enrollments.map((e) => (
                      <tr key={e.id}>
                        <td style={{ fontWeight: 600 }}>{e.student_name}</td>
                        <td>{e.roll_number || e.student_email || '—'}</td>
                        <td>
                          <span className="id-chip">Class {e.class_level} · {e.section_name}</span>
                        </td>
                        <td style={{ fontSize: '12px', color: 'var(--muted)' }}>
                          {new Date(e.requested_at).toLocaleDateString()}
                        </td>
                        <td>
                          {e.status === 'APPROVED' && <span className="badge badge-approved">Enrolled</span>}
                          {e.status === 'PENDING_APPROVAL' && <span className="badge badge-unverified">Pending</span>}
                          {e.status === 'REJECTED' && <span className="badge badge-rejected">Rejected</span>}
                        </td>
                        <td>
                          {e.status === 'PENDING_APPROVAL' ? (
                            <div style={{ display: 'flex', gap: '6px' }}>
                              <button
                                onClick={() => handleApproveEnrollment(e.id)}
                                className="btn btn-sm btn-ok"
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => handleRejectEnrollment(e.id)}
                                className="btn btn-sm btn-bad"
                              >
                                Reject
                              </button>
                            </div>
                          ) : (
                            <span style={{ fontSize: '13px', color: 'var(--muted)' }}>Completed</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Classes & Subjects Tab */}
      {activeTab === 'sections' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          {/* Sections List */}
          <div className="card">
            <div className="card-header">
              <div>
                <h2>Classes & Sections</h2>
                <p className="lead">Manage school class levels (6 to 12) and sections.</p>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button onClick={() => setShowSecModal(true)} className="btn btn-primary btn-sm">
                  <PlusCircle size={15} /> Add Section
                </button>
                <button
                  onClick={() => {
                    if (teachers.length === 0 || sections.length === 0 || subjects.length === 0) {
                      alert('You need active teachers, sections, and subjects before assigning.');
                      return;
                    }
                    setShowAssignModal(true);
                  }}
                  className="btn btn-secondary btn-sm"
                >
                  <ShieldCheck size={15} /> Assign Teacher
                </button>
              </div>
            </div>

            {sections.length === 0 ? (
              <EmptyState
                icon={<Layers size={24} />}
                title="No Sections Created Yet"
                description="Create your school's classes and sections (e.g. 10-A, 12-PCM) to start assigning teachers and enrolling students."
                actionText="Create First Section"
                onAction={() => setShowSecModal(true)}
              />
            ) : (
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Class</th>
                      <th>Section Name</th>
                      <th>Class Teacher</th>
                      <th>Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sections.map((s) => (
                      <tr key={s.id}>
                        <td><strong>Class {s.class_level}</strong></td>
                        <td><span className="id-chip">{s.section_name}</span></td>
                        <td>{s.class_teacher_name || <span style={{ color: 'var(--muted)', fontStyle: 'italic' }}>Unassigned</span>}</td>
                        <td style={{ fontSize: '12px', color: 'var(--muted)' }}>
                          {new Date(s.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Subjects List */}
          <div className="card">
            <div className="card-header">
              <div>
                <h2>Academic Subjects</h2>
                <p className="lead">Configured subject packs for your curriculum (ICSE / ISC / JEE / NEET).</p>
              </div>
              <button onClick={() => setShowSubModal(true)} className="btn btn-primary btn-sm">
                <PlusCircle size={15} /> Add Subject
              </button>
            </div>

            {subjects.length === 0 ? (
              <EmptyState
                icon={<BookOpen size={24} />}
                title="No Subjects Configured"
                description="Add subjects like Mathematics, Physics, Chemistry, Computer Science."
                actionText="Add Subject"
                onAction={() => setShowSubModal(true)}
              />
            ) : (
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Subject Name</th>
                      <th>Subject Code</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {subjects.map((sub) => (
                      <tr key={sub.id}>
                        <td style={{ fontWeight: 600 }}>{sub.name}</td>
                        <td><span className="id-chip">{sub.code}</span></td>
                        <td><span className="badge badge-approved">Active</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal: Create Section */}
      {showSecModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <h2 style={{ marginBottom: '16px' }}>Create New Section</h2>
            <form onSubmit={handleCreateSection}>
              <div className="form-group">
                <label className="form-label">Class Level (6 to 12)</label>
                <select
                  className="select"
                  value={newClassLevel}
                  onChange={(e) => setNewClassLevel(Number(e.target.value))}
                >
                  {[6, 7, 8, 9, 10, 11, 12].map((lvl) => (
                    <option key={lvl} value={lvl}>Class {lvl}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Section Name (e.g., 10-A, 12-PCM)</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g. 10-A"
                  required
                  value={newSectionName}
                  onChange={(e) => setNewSectionName(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
                <button type="button" onClick={() => setShowSecModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Section
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Create Subject */}
      {showSubModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <h2 style={{ marginBottom: '16px' }}>Add Subject</h2>
            <form onSubmit={handleCreateSubject}>
              <div className="form-group">
                <label className="form-label">Subject Name</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g. Mathematics"
                  required
                  value={newSubName}
                  onChange={(e) => setNewSubName(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Subject Code (2-6 letters)</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g. MTH"
                  required
                  value={newSubCode}
                  onChange={(e) => setNewSubCode(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
                <button type="button" onClick={() => setShowSubModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Subject
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Assign Teacher */}
      {showAssignModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <h2 style={{ marginBottom: '16px' }}>Assign Teacher to Section & Subject</h2>
            <form onSubmit={handleAssignTeacher}>
              <div className="form-group">
                <label className="form-label">Select Teacher</label>
                <select
                  className="select"
                  required
                  value={assignTeacherId}
                  onChange={(e) => setAssignTeacherId(e.target.value)}
                >
                  <option value="">-- Choose Teacher --</option>
                  {teachers
                    .filter((t) => t.status === 'ACTIVE')
                    .map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.full_name} ({t.role})
                      </option>
                    ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Select Section</label>
                <select
                  className="select"
                  required
                  value={assignSectionId}
                  onChange={(e) => setAssignSectionId(e.target.value)}
                >
                  <option value="">-- Choose Section --</option>
                  {sections.map((s) => (
                    <option key={s.id} value={s.id}>
                      Class {s.class_level} · {s.section_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Select Subject</label>
                <select
                  className="select"
                  required
                  value={assignSubjectId}
                  onChange={(e) => setAssignSubjectId(e.target.value)}
                >
                  <option value="">-- Choose Subject --</option>
                  {subjects.map((sub) => (
                    <option key={sub.id} value={sub.id}>
                      {sub.name} ({sub.code})
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
                <button type="button" onClick={() => setShowAssignModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Confirm Assignment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
