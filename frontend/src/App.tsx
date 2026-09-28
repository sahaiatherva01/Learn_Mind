import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { AuthView } from './views/AuthView';
import { InchargeDashboard } from './views/InchargeDashboard';
import { TeacherDashboard } from './views/TeacherDashboard';
import { StudentDashboard } from './views/StudentDashboard';
import {
  LibraryView,
  QuestionStudioView,
  PapersView,
  TestsView,
  AnalyticsView,
  StudentPracticeView,
  StudentAssistantView,
  BookmarksView,
} from './views/PlaceholderViews';

const AppContent: React.FC = () => {
  const { user, loading } = useAuth();
  const [currentTab, setCurrentTab] = useState<string>('');

  useEffect(() => {
    if (user) {
      if (user.role === 'ADMIN' || user.role === 'INCHARGE') {
        setCurrentTab('incharge-dashboard');
      } else if (user.role === 'CLASS_TEACHER' || user.role === 'SUBJECT_TEACHER') {
        setCurrentTab('teacher-dashboard');
      } else if (user.role === 'STUDENT') {
        setCurrentTab('student-dashboard');
      }
    }
  }, [user?.role]);

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg)',
        fontFamily: 'var(--font-ui)',
        color: 'var(--muted)',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontWeight: 600, fontSize: '18px', color: 'var(--ink)', marginBottom: '6px' }}>
            Learn_Mind
          </div>
          <div style={{ fontSize: '14px' }}>Loading academic workspace...</div>
        </div>
      </div>
    );
  }

  if (!user) {
    return <AuthView />;
  }

  const renderActiveView = () => {
    switch (currentTab) {
      // Incharge views
      case 'incharge-dashboard':
        return <InchargeDashboard initialTab="dashboard" />;
      case 'incharge-approvals':
        return <InchargeDashboard initialTab="approvals" />;
      case 'incharge-sections':
        return <InchargeDashboard initialTab="sections" />;

      // Teacher views
      case 'teacher-dashboard':
        return <TeacherDashboard onNavigateTab={(tab) => setCurrentTab(tab)} />;
      case 'teacher-library':
        return <LibraryView />;
      case 'teacher-studio':
        return <QuestionStudioView />;
      case 'teacher-papers':
        return <PapersView />;
      case 'teacher-tests':
        return <TestsView />;
      case 'teacher-analytics':
        return <AnalyticsView />;

      // Student views
      case 'student-dashboard':
        return <StudentDashboard />;
      case 'student-practice':
        return <StudentPracticeView />;
      case 'student-assistant':
        return <StudentAssistantView />;
      case 'student-bookmarks':
        return <BookmarksView />;

      default:
        if (user.role === 'STUDENT') return <StudentDashboard />;
        if (user.role === 'ADMIN' || user.role === 'INCHARGE') return <InchargeDashboard />;
        return <TeacherDashboard onNavigateTab={(tab) => setCurrentTab(tab)} />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar currentTab={currentTab} onSelectTab={(tab) => setCurrentTab(tab)} />
      <div className="main-content">
        <TopBar />
        <main>{renderActiveView()}</main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
