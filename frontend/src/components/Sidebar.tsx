import React from 'react';
import { useAuth } from '../context/AuthContext';
import {
  BrainCircuit,
  LayoutDashboard,
  Users,
  Layers,
  BookOpen,
  Sparkles,
  FileText,
  CalendarCheck,
  BarChart3,
  Bookmark,
  GraduationCap,
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab }) => {
  const { user } = useAuth();
  const role = user?.role;

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div style={{
        padding: '20px 24px',
        borderBottom: '1px solid var(--line)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <div style={{
          width: 36,
          height: 36,
          borderRadius: 'var(--radius-md)',
          background: 'var(--primary)',
          color: 'var(--primary-ink)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <BrainCircuit size={22} />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '16px', color: 'var(--ink)' }}>Learn_Mind</div>
          <div style={{ fontSize: '11px', color: 'var(--muted)' }}>Academic Intelligence</div>
        </div>
      </div>

      {/* Navigation Groups */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 0' }}>
        {/* Incharge / Admin Navigation */}
        {(role === 'ADMIN' || role === 'INCHARGE') && (
          <div className="nav-group">
            <div className="nav-heading">School Admin</div>
            <button
              className={`nav-item ${currentTab === 'incharge-dashboard' ? 'active' : ''}`}
              onClick={() => onSelectTab('incharge-dashboard')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <LayoutDashboard size={18} />
              <span>Dashboard</span>
            </button>
            <button
              className={`nav-item ${currentTab === 'incharge-approvals' ? 'active' : ''}`}
              onClick={() => onSelectTab('incharge-approvals')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <Users size={18} />
              <span>Approvals Queue</span>
            </button>
            <button
              className={`nav-item ${currentTab === 'incharge-sections' ? 'active' : ''}`}
              onClick={() => onSelectTab('incharge-sections')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <Layers size={18} />
              <span>Classes & Sections</span>
            </button>
          </div>
        )}

        {/* Teacher Navigation */}
        {(role === 'CLASS_TEACHER' || role === 'SUBJECT_TEACHER' || role === 'INCHARGE') && (
          <div className="nav-group">
            <div className="nav-heading">Teaching Workspace</div>
            <button
              className={`nav-item ${currentTab === 'teacher-dashboard' ? 'active' : ''}`}
              onClick={() => onSelectTab('teacher-dashboard')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <LayoutDashboard size={18} />
              <span>My Classes</span>
            </button>
            <button
              className={`nav-item ${currentTab === 'teacher-library' ? 'active' : ''}`}
              onClick={() => onSelectTab('teacher-library')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <BookOpen size={18} />
              <span>Library (RAG)</span>
            </button>
            <button
              className={`nav-item ${currentTab === 'teacher-studio' ? 'active' : ''}`}
              onClick={() => onSelectTab('teacher-studio')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <Sparkles size={18} />
              <span>Question Studio</span>
            </button>
            <button
              className={`nav-item ${currentTab === 'teacher-papers' ? 'active' : ''}`}
              onClick={() => onSelectTab('teacher-papers')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <FileText size={18} />
              <span>Papers & Worksheets</span>
            </button>
            <button
              className={`nav-item ${currentTab === 'teacher-tests' ? 'active' : ''}`}
              onClick={() => onSelectTab('teacher-tests')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <CalendarCheck size={18} />
              <span>Scheduled Tests</span>
            </button>
            <button
              className={`nav-item ${currentTab === 'teacher-analytics' ? 'active' : ''}`}
              onClick={() => onSelectTab('teacher-analytics')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <BarChart3 size={18} />
              <span>Analytics & Remedial</span>
            </button>
          </div>
        )}

        {/* Student Navigation */}
        {role === 'STUDENT' && (
          <div className="nav-group">
            <div className="nav-heading">Student Focus</div>
            <button
              className={`nav-item ${currentTab === 'student-dashboard' ? 'active' : ''}`}
              onClick={() => onSelectTab('student-dashboard')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <LayoutDashboard size={18} />
              <span>Dashboard</span>
            </button>
            <button
              className={`nav-item ${currentTab === 'student-practice' ? 'active' : ''}`}
              onClick={() => onSelectTab('student-practice')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <GraduationCap size={18} />
              <span>Practice & Mocks</span>
            </button>
            <button
              className={`nav-item ${currentTab === 'student-assistant' ? 'active' : ''}`}
              onClick={() => onSelectTab('student-assistant')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <Sparkles size={18} />
              <span>Study Assistant</span>
            </button>
            <button
              className={`nav-item ${currentTab === 'student-bookmarks' ? 'active' : ''}`}
              onClick={() => onSelectTab('student-bookmarks')}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <Bookmark size={18} />
              <span>Saved Questions</span>
            </button>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div style={{
        padding: '16px 20px',
        borderTop: '1px solid var(--line)',
        fontSize: '12px',
        color: 'var(--muted)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <span>Phase 0 · Green</span>
        <span className="badge badge-approved" style={{ fontSize: '10px' }}>v1.0.0</span>
      </div>
    </aside>
  );
};
