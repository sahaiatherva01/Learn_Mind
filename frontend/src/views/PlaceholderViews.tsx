import React from 'react';
import { EmptyState } from '../components/EmptyState';
import {
  BookOpen,
  Sparkles,
  FileText,
  CalendarCheck,
  BarChart3,
  Bookmark,
  GraduationCap,
  UploadCloud,
} from 'lucide-react';

export const LibraryView: React.FC = () => {
  return (
    <div className="page-body">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1>Private Academic Library (RAG)</h1>
          <p className="lead">Rules.md A.3: Teacher uploads are private to the uploading teacher only.</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => alert('Phase 1 will enable active PDF chunking & ingestion pipeline.')}>
          <UploadCloud size={15} /> Upload PDF / Book
        </button>
      </div>

      <div className="card">
        <EmptyState
          icon={<BookOpen size={28} />}
          title="No Books or Papers Uploaded Yet"
          description="Upload textbook PDFs or question banks. The ingestion engine (Phase 1) will parse, chunk, embed, and tag chapters/topics for grounded question generation."
          actionText="Upload First Book (Phase 1)"
          onAction={() => alert('Phase 1 will enable active PDF chunking & ingestion pipeline.')}
          secondaryText="Supported formats: PDF (ICSE / ISC / JEE / NEET PCM+CS seeds)"
        />
      </div>
    </div>
  );
};

export const QuestionStudioView: React.FC = () => {
  return (
    <div className="page-body">
      <div style={{ marginBottom: '24px' }}>
        <h1>Question Studio</h1>
        <p className="lead">Rules.md B & C: Generate As-is, Similar, or Higher-level questions with Solve-Twice verification.</p>
      </div>

      {/* Studio Filter Bar Mockup from Design.md §38 */}
      <div className="card" style={{ marginBottom: '24px', background: 'var(--surface)' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center' }}>
          <select className="select" style={{ width: '160px' }}>
            <option>Mathematics</option>
            <option>Physics</option>
            <option>Chemistry</option>
            <option>Computer Science</option>
          </select>
          <select className="select" style={{ width: '120px' }}>
            <option>Class 10</option>
            <option>Class 12</option>
            <option>JEE Main</option>
            <option>NEET</option>
          </select>
          <select className="select" style={{ width: '160px' }}>
            <option>Integration</option>
            <option>Electrostatics</option>
            <option>Organic Reactions</option>
            <option>Data Structures</option>
          </select>
          <select className="select" style={{ width: '140px' }}>
            <option>Mode: Similar</option>
            <option>Mode: As-is</option>
            <option>Mode: Higher Level</option>
          </select>
          <button className="btn btn-primary btn-sm" onClick={() => alert('Phase 2 will activate the LangGraph Question Studio engine.')}>
            <Sparkles size={14} /> Generate Questions
          </button>
        </div>
      </div>

      <div className="card">
        <EmptyState
          icon={<Sparkles size={28} />}
          title="Question Studio Bank is Empty"
          description="Select a chapter, mode, and difficulty above. Generated questions will undergo Solve-Twice verification and receive immutable Question IDs (e.g. Q-8K3F2A · v1)."
          secondaryText="Phase 2 activates the LangGraph G3 generation & solve-twice verification graphs."
        />
      </div>
    </div>
  );
};

export const PapersView: React.FC = () => {
  return (
    <div className="page-body">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1>Papers & Worksheets</h1>
          <p className="lead">Presets: Worksheet, Quiz (Speed Mode), Question Paper, Class Test, Mock, Pre-Board.</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => alert('Phase 3 will enable Paper Blueprint generation & PDF export.')}>
          <FileText size={15} /> Create New Paper
        </button>
      </div>

      <div className="card">
        <EmptyState
          icon={<FileText size={28} />}
          title="No Papers Created Yet"
          description="Assemble papers from approved questions with blueprints balancing Easy/Medium/Hard distribution, PDF export, and teacher solution keys."
          actionText="Build New Paper (Phase 3)"
          onAction={() => alert('Phase 3 will enable Paper Blueprint generation & PDF export.')}
        />
      </div>
    </div>
  );
};

export const TestsView: React.FC = () => {
  return (
    <div className="page-body">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1>Scheduled Assessments & Proctoring</h1>
          <p className="lead">Schedule tests with tab-switch detection, timer constraints, and auto-grading.</p>
        </div>
      </div>

      <div className="card">
        <EmptyState
          icon={<CalendarCheck size={28} />}
          title="No Active Test Schedules"
          description="Schedule a proctored assessment for your assigned sections. Proctoring events (tab switches, blurs) are monitored transparently."
        />
      </div>
    </div>
  );
};

export const AnalyticsView: React.FC = () => {
  return (
    <div className="page-body">
      <div style={{ marginBottom: '24px' }}>
        <h1>Class Analytics & Remedial Planner</h1>
        <p className="lead">Weak-topic detection and automated 5-day structured remedial plan generation.</p>
      </div>

      <div className="card">
        <EmptyState
          icon={<BarChart3 size={28} />}
          title="No Assessment Data Yet"
          description="Once students submit proctored test attempts, topic-wise accuracy heatmaps, weak topics, and 5-day remedial plans will appear here."
        />
      </div>
    </div>
  );
};

export const StudentPracticeView: React.FC = () => {
  return (
    <div className="page-body">
      <div style={{ marginBottom: '24px' }}>
        <h1>Practice & Mock Tests</h1>
        <p className="lead">Practice questions from approved bank with instant feedback on objective questions.</p>
      </div>

      <div className="card">
        <EmptyState
          icon={<GraduationCap size={28} />}
          title="Practice Bank Ready for Activation"
          description="Practice assignments assigned by your teacher will appear here. Students see correct answers only after submission (Rules.md A.5)."
        />
      </div>
    </div>
  );
};

export const StudentAssistantView: React.FC = () => {
  return (
    <div className="page-body">
      <div style={{ marginBottom: '24px' }}>
        <h1>AI Study Assistant</h1>
        <p className="lead">Rules.md D.2: Strictly grounded in teacher-assigned materials + syllabus only.</p>
      </div>

      <div className="card">
        <EmptyState
          icon={<Sparkles size={28} />}
          title="Strictly Grounded Assistant"
          description="Ask questions about your coursework. The assistant uses the Explain → Example → Try yourself → Practice → Check workflow with zero hallucinations."
          secondaryText="Phase 4 delivers the complete LangGraph G7 study assistant graph."
        />
      </div>
    </div>
  );
};

export const BookmarksView: React.FC = () => {
  return (
    <div className="page-body">
      <div style={{ marginBottom: '24px' }}>
        <h1>Saved Questions & Notes</h1>
        <p className="lead">Rules.md B.3 & B.6: Bookmarked questions pinned by Question ID (QID).</p>
      </div>

      <div className="card">
        <EmptyState
          icon={<Bookmark size={28} />}
          title="No Bookmarked Questions"
          description="Bookmark tricky questions during practice or review to revisit them later."
        />
      </div>
    </div>
  );
};
