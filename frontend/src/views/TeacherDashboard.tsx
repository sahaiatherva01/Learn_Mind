import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { EmptyState } from '../components/EmptyState';
import type { StudentEnrollment } from '../types';
import {
  BookOpen,
  Sparkles,
  FileText,
  GraduationCap,
  Layers,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';

interface TeacherDashboardProps {
  onNavigateTab?: (tab: string) => void;
}

export const TeacherDashboard: React.FC<TeacherDashboardProps> = ({ onNavigateTab }) => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [enrollments, setEnrollments] = useState<StudentEnrollment[]>([]);
  const [studentsRoster, setStudentsRoster] = useState<any[]>([]);
  const [rosterFilterSec] = useState<string>('');
  const [feedback, setFeedback] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [dashRes, enrRes, rosterRes] = await Promise.all([
        api.getTeacherDashboard().catch(() => null),
        api.getTeacherEnrollments().catch(() => []),
        api.getTeacherStudentsRoster().catch(() => []),
      ]);

      setDashboardData(dashRes);
      setEnrollments(enrRes || []);
      setStudentsRoster(rosterRes || []);
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApproveEnrollment = async (enrollmentId: string) => {
    try {
      await api.approveTeacherEnrollment(enrollmentId);
      setFeedback('Student enrollment approved');
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleRejectEnrollment = async (enrollmentId: string) => {
    try {
      await api.rejectTeacherEnrollment(enrollmentId);
      setFeedback('Student enrollment rejected');
      loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const stats = dashboardData?.stats || {};
  const assignments = dashboardData?.assignments || [];
  const classSections = dashboardData?.class_teacher_sections || [];
  const isClassTeacher = classSections.length > 0;

  const filteredRoster = rosterFilterSec
    ? studentsRoster.filter((s) => s.section?.id === rosterFilterSec)
    : studentsRoster;

  return (
    <div className="page-body">
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h1>Welcome, {user?.full_name}</h1>
          <span className="badge badge-info">{user?.role}</span>
        </div>
        <p className="lead">
          Your academic teaching workspace for creating source-grounded questions, scheduling assessments, and tracking student mastery.
        </p>
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

      {/* Stats Row */}
      <div className="stat-grid">
        <div className="stat-card">
          <span className="stat-label">My Assigned Classes</span>
          <span className="stat-value">{stats.assigned_classes_count ?? assignments.length}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Class Teacher Sections</span>
          <span className="stat-value">{stats.class_teacher_sections_count ?? classSections.length}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Total Students Monitored</span>
          <span className="stat-value">{stats.total_students_count ?? 0}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Pending Section Approvals</span>
          <span className="stat-value" style={{ color: enrollments.length > 0 ? 'var(--warn)' : 'var(--ink)' }}>
            {enrollments.length}
          </span>
        </div>
      </div>

      {/* Quick Launchpad for Core Features */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <div style={{ width: 36, height: 36, borderRadius: 'var(--radius-md)', background: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <BookOpen size={20} />
              </div>
              <h3 style={{ fontSize: '16px' }}>Private Library (RAG)</h3>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--muted)', marginBottom: '16px' }}>
              Upload textbook PDFs, chapters, or syllabus seeds. Ground question generation privately in your materials.
            </p>
          </div>
          <button
            onClick={() => onNavigateTab && onNavigateTab('teacher-library')}
            className="btn btn-secondary btn-sm"
            style={{ width: '100%', justifyContent: 'space-between' }}
          >
            <span>Go to Library (Phase 1)</span>
            <ArrowRight size={15} />
          </button>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <div style={{ width: 36, height: 36, borderRadius: 'var(--radius-md)', background: 'var(--info-bg)', color: 'var(--info)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Sparkles size={20} />
              </div>
              <h3 style={{ fontSize: '16px' }}>Question Studio</h3>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--muted)', marginBottom: '16px' }}>
              Generate As-is / Similar / Higher-level questions with Solve-Twice verification across PCM+CS.
            </p>
          </div>
          <button
            onClick={() => onNavigateTab && onNavigateTab('teacher-studio')}
            className="btn btn-secondary btn-sm"
            style={{ width: '100%', justifyContent: 'space-between' }}
          >
            <span>Open Question Studio</span>
            <ArrowRight size={15} />
          </button>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <div style={{ width: 36, height: 36, borderRadius: 'var(--radius-md)', background: 'var(--ok-bg)', color: 'var(--ok)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <FileText size={20} />
              </div>
              <h3 style={{ fontSize: '16px' }}>Paper & Test Presets</h3>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--muted)', marginBottom: '16px' }}>
              Assemble Worksheets, Quizzes, Question Papers, and Pre-Boards with auto PDF exports and answer keys.
            </p>
          </div>
          <button
            onClick={() => onNavigateTab && onNavigateTab('teacher-papers')}
            className="btn btn-secondary btn-sm"
            style={{ width: '100%', justifyContent: 'space-between' }}
          >
            <span>Create Paper (Phase 3)</span>
            <ArrowRight size={15} />
          </button>
        </div>
      </div>

      {/* Assigned Classes and Subjects Section */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <div>
            <h2>My Assigned Classes & Subjects</h2>
            <p className="lead">Rules.md A.6: Teachers act only on assigned sections & subjects.</p>
          </div>
        </div>

        {assignments.length === 0 ? (
          <EmptyState
            icon={<Layers size={24} />}
            title="No Teaching Assignments Yet"
            description="Your school Incharge will assign you to specific class sections and academic subjects."
            secondaryText="Contact your school Incharge to be assigned to Class 10/12 sections."
          />
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '16px' }}>
            {assignments.map((a: any) => (
              <div
                key={a.id || a.assignment_id}
                style={{
                  border: '1px solid var(--line)',
                  borderRadius: 'var(--radius-md)',
                  padding: '16px',
                  background: 'var(--bg)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span className="id-chip">Class {a.class_level} · {a.section_name}</span>
                  <span className="badge badge-info">{a.subject_code}</span>
                </div>
                <div style={{ fontWeight: 600, fontSize: '15px' }}>{a.subject_name}</div>
                <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '4px' }}>
                  Active Section Assignment
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Class Teacher Section Approvals (Rules.md A.7) */}
      {isClassTeacher && (
        <div className="card" style={{ marginBottom: '32px' }}>
          <div className="card-header">
            <div>
              <h2>Class Teacher: Pending Student Enrollments</h2>
              <p className="lead">
                As the Class Teacher, approve or reject students requesting to join your designated section(s).
              </p>
            </div>
            <span className="badge badge-unverified">{enrollments.length} Pending</span>
          </div>

          {enrollments.length === 0 ? (
            <EmptyState
              icon={<ShieldCheck size={24} />}
              title="All Student Enrollments Handled"
              description="There are currently no pending student section approval requests for your class."
            />
          ) : (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Student Name</th>
                    <th>Roll Number / Email</th>
                    <th>Section</th>
                    <th>Requested At</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {enrollments.map((e) => (
                    <tr key={e.id}>
                      <td style={{ fontWeight: 600 }}>{e.student_name}</td>
                      <td>{e.roll_number || e.student_email || '—'}</td>
                      <td><span className="id-chip">Class {e.class_level} · {e.section_name}</span></td>
                      <td style={{ fontSize: '12px', color: 'var(--muted)' }}>
                        {new Date(e.requested_at).toLocaleDateString()}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '8px' }}>
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
      )}

      {/* Student Roster Lookup (PRD §6) */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2>Student Roster Lookup</h2>
            <p className="lead">PRD §6: All teachers have basic profile/roster access across school classes.</p>
          </div>
        </div>

        {studentsRoster.length === 0 ? (
          <EmptyState
            icon={<GraduationCap size={24} />}
            title="No Students Registered"
            description="Students will appear here once registered under your school."
          />
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Email</th>
                  <th>Roll Number</th>
                  <th>Section</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredRoster.map((s) => (
                  <tr key={s.id}>
                    <td style={{ fontWeight: 600 }}>{s.full_name}</td>
                    <td>{s.email || '—'}</td>
                    <td>{s.roll_number || '—'}</td>
                    <td>
                      {s.section ? (
                        <span className="id-chip">Class {s.section.class_level} · {s.section.section_name}</span>
                      ) : (
                        <span style={{ color: 'var(--muted)', fontStyle: 'italic' }}>Unassigned</span>
                      )}
                    </td>
                    <td>
                      {s.section?.enrollment_status === 'APPROVED' && (
                        <span className="badge badge-approved">Enrolled</span>
                      )}
                      {s.section?.enrollment_status === 'PENDING_APPROVAL' && (
                        <span className="badge badge-unverified">Pending</span>
                      )}
                      {!s.section && <span className="badge badge-info">No Section</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
