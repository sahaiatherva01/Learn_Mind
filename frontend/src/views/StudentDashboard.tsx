import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { EmptyState } from '../components/EmptyState';
import type { Section } from '../types';
import {
  Sparkles,
  CalendarCheck,
  BookOpen,
  ArrowRight,
  Clock,
  CheckCircle2,
} from 'lucide-react';

export const StudentDashboard: React.FC = () => {
  const { user, refreshProfile } = useAuth();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [availableSections, setAvailableSections] = useState<Section[]>([]);
  const [selectedSecId, setSelectedSecId] = useState<string>('');
  const [feedback, setFeedback] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [dashRes, secRes] = await Promise.all([
        api.getStudentDashboard().catch(() => null),
        api.getSections().catch(() => []),
      ]);
      setDashboardData(dashRes);
      setAvailableSections(secRes || []);
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRequestEnrollment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSecId) return;
    try {
      await api.requestSectionEnrollment(selectedSecId);
      setFeedback('Section enrollment requested. Waiting for Class Teacher or Incharge approval.');
      await refreshProfile();
      await loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const enrollment = dashboardData?.enrollment || user?.enrollment;
  const isApproved = enrollment?.status === 'APPROVED';
  const isPending = enrollment?.status === 'PENDING_APPROVAL';
  const subjects = dashboardData?.subjects || [];

  return (
    <div className="page-body">
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h1>Hello, {user?.full_name}</h1>
          <span className="badge badge-info">Student</span>
        </div>
        <p className="lead">
          Your focused practice dashboard for ICSE / ISC / JEE / NEET preparation.
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

      {/* Section Enrollment Status Banner */}
      <div className="card" style={{ marginBottom: '28px', borderLeft: isApproved ? '4px solid var(--ok)' : '4px solid var(--warn)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              {isApproved ? (
                <CheckCircle2 size={18} color="var(--ok)" />
              ) : (
                <Clock size={18} color="var(--warn)" />
              )}
              <h3 style={{ fontSize: '16px' }}>
                {isApproved
                  ? `Enrolled in Class ${enrollment?.class_level} · Section ${enrollment?.section_name}`
                  : isPending
                  ? `Enrollment Pending Approval for Class ${enrollment?.class_level} · Section ${enrollment?.section_name}`
                  : 'Not Enrolled in a Section Yet'}
              </h3>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--muted)' }}>
              {isApproved
                ? 'Your section is approved. You will receive scheduled tests and assignments from your teachers.'
                : isPending
                ? 'Your request is awaiting approval from your Class Teacher or school Incharge.'
                : 'Select your class section below to join your academic stream.'}
            </p>
          </div>

          {!isApproved && (
            <form onSubmit={handleRequestEnrollment} style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <select
                className="select"
                style={{ width: '220px', height: '38px', padding: '6px 12px' }}
                value={selectedSecId}
                onChange={(e) => setSelectedSecId(e.target.value)}
                required
              >
                <option value="">-- Choose Section --</option>
                {availableSections.map((sec) => (
                  <option key={sec.id} value={sec.id}>
                    Class {sec.class_level} · {sec.section_name}
                  </option>
                ))}
              </select>
              <button type="submit" className="btn btn-primary btn-sm">
                {isPending ? 'Change Section' : 'Join Section'}
              </button>
            </form>
          )}
        </div>
      </div>

      {/* Quick Summary Cards */}
      <div className="stat-grid">
        <div className="stat-card">
          <span className="stat-label">Active Subjects</span>
          <span className="stat-value">{subjects.length}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Saved Questions</span>
          <span className="stat-value">{dashboardData?.stats?.bookmarks_count ?? 0}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Tests Completed</span>
          <span className="stat-value">{dashboardData?.stats?.tests_attempted ?? 0}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Weak Topics</span>
          <span className="stat-value" style={{ color: 'var(--ok)' }}>0 (All Good)</span>
        </div>
      </div>

      {/* Subjects Overview */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <div>
            <h2>My Curriculum & Subjects</h2>
            <p className="lead">Academic subjects taught in your assigned section.</p>
          </div>
        </div>

        {subjects.length === 0 ? (
          <EmptyState
            icon={<BookOpen size={24} />}
            title={isApproved ? "No Subjects Configured Yet" : "Enrollment Pending"}
            description={
              isApproved
                ? "Your teachers will assign subjects (Maths, Physics, Chemistry, CS) to this section soon."
                : "Once your Class Teacher approves your enrollment, your assigned subjects and syllabus will appear here."
            }
          />
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '16px' }}>
            {subjects.map((sub: any) => (
              <div
                key={sub.id}
                style={{
                  border: '1px solid var(--line)',
                  borderRadius: 'var(--radius-md)',
                  padding: '16px',
                  background: 'var(--bg)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '15px' }}>{sub.name}</div>
                  <span className="id-chip" style={{ marginTop: '4px' }}>{sub.code}</span>
                </div>
                <button className="btn btn-secondary btn-sm" title="Practice Subject">
                  <ArrowRight size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Upcoming Tests & Practice Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Proctored Tests */}
        <div className="card">
          <div className="card-header">
            <h3>Upcoming Scheduled Tests</h3>
            <span className="badge badge-info">Proctored</span>
          </div>
          <EmptyState
            icon={<CalendarCheck size={24} />}
            title="No Scheduled Tests"
            description="When your teacher schedules a worksheet, quiz, or mock test, it will appear here with your duration and proctoring guidelines."
          />
        </div>

        {/* Study Assistant Teaser (Rules.md D.2) */}
        <div className="card">
          <div className="card-header">
            <h3>AI Study Assistant</h3>
            <span className="badge badge-approved">Strictly Grounded</span>
          </div>
          <EmptyState
            icon={<Sparkles size={24} />}
            title="Syllabus Grounded Assistant"
            description="Ask questions about your coursework. The assistant uses the Explain → Example → Try yourself → Practice → Check workflow with zero hallucinations."
            secondaryText="Phase 4 will activate the interactive study assistant."
          />
        </div>
      </div>
    </div>
  );
};
