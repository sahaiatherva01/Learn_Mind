import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  UploadCloud,
  Cpu,
  CheckCircle,
  AlertTriangle,
  BookOpen,
  ShieldCheck,
  RefreshCw,
  Edit2
} from 'lucide-react';
import { api } from '../api';
import type { SubjectPack, StudioGenerateResponse } from '../types';
import { SolveTwiceInspectorModal } from '../components/SolveTwiceInspectorModal';
import { QuestionSetImporterModal } from '../components/QuestionSetImporterModal';

export const QuestionStudioView: React.FC = () => {
  const [subjectPacks, setSubjectPacks] = useState<SubjectPack[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('Mathematics');
  const [selectedClass, setSelectedClass] = useState<number>(12);
  const [selectedChapter, setSelectedChapter] = useState<string>('');
  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('MCQ');
  const [difficulty, setDifficulty] = useState<string>('MEDIUM');
  const [marks, setMarks] = useState<number>(1);
  const [mode, setMode] = useState<string>('AI_SIMILAR');
  const [mixedTopics, setMixedTopics] = useState<string>('');

  // RAG Library source chunks
  const [libraryFiles, setLibraryFiles] = useState<any[]>([]);
  const [selectedChunkId, setSelectedChunkId] = useState<string>('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Generated draft result
  const [draftResult, setDraftResult] = useState<StudioGenerateResponse | null>(null);
  const [isEditingDraft, setIsEditingDraft] = useState(false);
  const [editedBody, setEditedBody] = useState('');
  const [editedAnswer, setEditedAnswer] = useState('');
  const [editedSolution, setEditedSolution] = useState('');

  // Modals
  const [showInspector, setShowInspector] = useState(false);
  const [showImporter, setShowImporter] = useState(false);

  useEffect(() => {
    loadSubjectPacks();
    loadLibraryFiles();
  }, []);

  const loadSubjectPacks = async () => {
    try {
      const packs = await api.getSubjectPacks();
      setSubjectPacks(packs);
      if (packs.length > 0) {
        setSelectedSubject(packs[0].subject);
        if (packs[0].chapters && packs[0].chapters.length > 0) {
          setSelectedChapter(packs[0].chapters[0].name);
          if (packs[0].chapters[0].topics && packs[0].chapters[0].topics.length > 0) {
            setSelectedTopic(packs[0].chapters[0].topics[0].name);
          }
        }
      }
    } catch (err: any) {
      console.error('Failed to load subject packs', err);
    }
  };

  const loadLibraryFiles = async () => {
    try {
      const files = await api.getLibraryFiles();
      setLibraryFiles(files || []);
    } catch (err) {
      console.error('Failed to load files', err);
    }
  };

  const currentPack = subjectPacks.find(
    (p) => p.subject.toLowerCase() === selectedSubject.toLowerCase()
  );

  const handleSubjectChange = (subj: string) => {
    setSelectedSubject(subj);
    const pack = subjectPacks.find((p) => p.subject.toLowerCase() === subj.toLowerCase());
    if (pack && pack.chapters && pack.chapters.length > 0) {
      setSelectedChapter(pack.chapters[0].name);
      if (pack.chapters[0].topics && pack.chapters[0].topics.length > 0) {
        setSelectedTopic(pack.chapters[0].topics[0].name);
      }
    }
  };

  const handleChapterChange = (chap: string) => {
    setSelectedChapter(chap);
    if (currentPack) {
      const chapterObj = currentPack.chapters?.find((c) => c.name === chap);
      if (chapterObj && chapterObj.topics && chapterObj.topics.length > 0) {
        setSelectedTopic(chapterObj.topics[0].name);
      }
    }
  };

  const handleGenerate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      setSuccessMsg(null);
      const res = await api.generateDraftQuestion({
        subject: selectedSubject,
        class_level: selectedClass,
        chapter: selectedChapter || 'General',
        topic: selectedTopic || 'General',
        question_type: selectedType,
        difficulty,
        marks,
        mode,
        chunk_id: selectedChunkId || null,
        mixed_topics: mode === 'MIXED_TOPICS' ? mixedTopics : null,
      });
      setDraftResult(res);
      setEditedBody(res.draft.body);
      setEditedAnswer(res.draft.answer);
      setEditedSolution(res.draft.solution || '');
      setIsEditingDraft(false);
    } catch (err: any) {
      setError(err?.message || 'Failed to generate question draft');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveToBank = async (approve: boolean = false) => {
    if (!draftResult) return;
    try {
      setLoading(true);
      setError(null);
      const payload = {
        ...draftResult,
        draft: {
          ...draftResult.draft,
          body: editedBody,
          answer: editedAnswer,
          solution: editedSolution,
        },
        approve,
      };
      const res = await api.saveDraftQuestion(payload);
      setSuccessMsg(
        `Question ${res.short_id} successfully saved to Bank with status: ${approve ? 'APPROVED' : 'UNVERIFIED'}`
      );
      setDraftResult(null);
    } catch (err: any) {
      setError(err?.message || 'Failed to save question to bank');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', color: '#f8fafc' }}>
      {/* View Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sparkles color="#38bdf8" /> Question Studio
          </h1>
          <p style={{ margin: 0, color: '#94a3b8', fontSize: '14px' }}>
            G3 Question Intelligence Engine • Solve-Twice Dual Verification • Config-driven Subject Packs
          </p>
        </div>

        <button
          onClick={() => setShowImporter(true)}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 18px', borderRadius: '8px', background: '#1e293b', border: '1px solid #334155', color: '#38bdf8', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}
        >
          <UploadCloud size={16} /> Import Question Set (G2 Graph)
        </button>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#ef4444', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} /> {error}
        </div>
      )}

      {successMsg && (
        <div style={{ background: 'rgba(34, 197, 94, 0.1)', border: '1px solid #22c55e', color: '#22c55e', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle size={18} /> {successMsg}
        </div>
      )}

      {/* Main Studio Workspace: 2-column layout */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
        {/* Left Column: Generation Parameters */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '24px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 700, margin: '0 0 16px 0', color: '#cbd5e1' }}>
            1. Generation Specifications
          </h2>

          <form onSubmit={handleGenerate}>
            {/* Subject and Class */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px', marginBottom: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Subject</label>
                <select
                  value={selectedSubject}
                  onChange={(e) => handleSubjectChange(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
                >
                  {subjectPacks.map((p) => (
                    <option key={p.code} value={p.subject}>{p.subject} ({p.code})</option>
                  ))}
                  {!subjectPacks.length && <option value="Mathematics">Mathematics (MTH)</option>}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Class</label>
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(Number(e.target.value))}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
                >
                  <option value={9}>Class 9</option>
                  <option value={10}>Class 10</option>
                  <option value={11}>Class 11</option>
                  <option value={12}>Class 12</option>
                </select>
              </div>
            </div>

            {/* Chapter and Topic */}
            <div style={{ marginBottom: '14px' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Chapter</label>
              <select
                value={selectedChapter}
                onChange={(e) => handleChapterChange(e.target.value)}
                style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
              >
                {currentPack?.chapters?.map((ch) => (
                  <option key={ch.code} value={ch.name}>{ch.name}</option>
                ))}
                {!currentPack?.chapters?.length && <option value="Calculus">Calculus</option>}
              </select>
            </div>

            <div style={{ marginBottom: '14px' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Topic</label>
              <select
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
              >
                {currentPack?.chapters
                  ?.find((c) => c.name === selectedChapter)
                  ?.topics?.map((tp) => (
                    <option key={tp.code} value={tp.name}>{tp.name}</option>
                  ))}
                {!currentPack?.chapters?.length && <option value="Definite Integrals">Definite Integrals</option>}
              </select>
            </div>

            {/* Type, Difficulty, Marks */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Type</label>
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#f8fafc', fontSize: '12px' }}
                >
                  <option value="MCQ">MCQ (1m)</option>
                  <option value="NUMERICAL">Numerical</option>
                  <option value="STEP_BY_STEP">Derivation</option>
                  <option value="CODE_OUTPUT">Code Output</option>
                  <option value="REACTION_CHAIN">Reaction Chain</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Difficulty</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#f8fafc', fontSize: '12px' }}
                >
                  <option value="EASY">Easy</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HARD">Hard (JEE/Adv)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Marks</label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={marks}
                  onChange={(e) => setMarks(Number(e.target.value))}
                  style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#f8fafc', fontSize: '12px' }}
                />
              </div>
            </div>

            {/* Mode selection */}
            <div style={{ marginBottom: '14px' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Generation Mode</label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                {[
                  { id: 'AI_SIMILAR', label: 'Similar to Source' },
                  { id: 'AI_HIGHER', label: 'Higher Level (Bloom+)' },
                  { id: 'SOURCE_COPY', label: 'Exact Source Copy' },
                  { id: 'MIXED_TOPICS', label: 'Mixed Topics' },
                ].map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => setMode(m.id)}
                    style={{
                      padding: '8px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: 600,
                      background: mode === m.id ? '#0284c7' : '#0f172a',
                      border: mode === m.id ? '1px solid #38bdf8' : '1px solid #334155',
                      color: mode === m.id ? '#ffffff' : '#94a3b8',
                      cursor: 'pointer',
                    }}
                  >
                    {m.label}
                  </button>
                ))}
              </div>
            </div>

            {mode === 'MIXED_TOPICS' && (
              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>
                  Cross-Topic Synthesis:
                </label>
                <input
                  type="text"
                  value={mixedTopics}
                  onChange={(e) => setMixedTopics(e.target.value)}
                  placeholder="e.g. Integrate with Trigonometric Substitution or Kinematics"
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
                />
              </div>
            )}

            {/* Library Grounding */}
            {libraryFiles.length > 0 && (
              <div style={{ marginBottom: '20px', padding: '12px', borderRadius: '8px', background: '#0f172a', border: '1px solid #334155' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 600, color: '#c084fc', marginBottom: '6px' }}>
                  <BookOpen size={14} /> Ground from Uploaded Book (Optional):
                </div>
                <select
                  value={selectedChunkId}
                  onChange={(e) => setSelectedChunkId(e.target.value)}
                  style={{ width: '100%', padding: '6px 10px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '12px' }}
                >
                  <option value="">None (Use Standard Syllabus Constraints)</option>
                  {libraryFiles.map((f) => (
                    <option key={f.id} value={f.id}>{f.filename} ({f.total_chunks} chunks)</option>
                  ))}
                </select>
              </div>
            )}

            {/* Generate Button */}
            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #0284c7 0%, #2563eb 100%)',
                border: 'none',
                color: '#ffffff',
                fontSize: '14px',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                cursor: loading ? 'not-allowed' : 'pointer',
                boxShadow: '0 4px 12px rgba(2, 132, 199, 0.3)',
              }}
            >
              {loading ? <RefreshCw size={18} className="spin" /> : <Sparkles size={18} />}
              {loading ? 'Executing Dual-Solver Pipeline...' : 'Generate with Solve-Twice Verification'}
            </button>
          </form>
        </div>

        {/* Right Column: Interactive Live Preview & Solve-Twice Verification */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '24px', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 700, margin: '0 0 16px 0', color: '#cbd5e1' }}>
            2. Live Draft & Dual-Solver Verification
          </h2>

          {!draftResult ? (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#64748b', padding: '40px 20px', textAlign: 'center' }}>
              <Cpu size={48} style={{ opacity: 0.4, marginBottom: '16px' }} />
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#94a3b8', marginBottom: '6px' }}>Ready to Draft Question</div>
              <div style={{ fontSize: '13px', maxWidth: '300px' }}>
                Select parameters on the left and trigger generation. Every question is verified by two independent solver passes.
              </div>
            </div>
          ) : (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
              {/* Solve-Twice Status Banner */}
              <div
                style={{
                  padding: '12px',
                  borderRadius: '8px',
                  marginBottom: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: draftResult.verification.agree ? 'rgba(34, 197, 94, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                  border: draftResult.verification.agree ? '1px solid #22c55e' : '1px solid #ef4444',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {draftResult.verification.agree ? <CheckCircle size={20} color="#22c55e" /> : <AlertTriangle size={20} color="#ef4444" />}
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 700, color: draftResult.verification.agree ? '#22c55e' : '#ef4444' }}>
                      {draftResult.verification.agree ? 'Dual Solvers Agree (Auto-Checked ✓)' : 'Solvers Disagree (Needs Review ⚠)'}
                    </div>
                    <div style={{ fontSize: '11px', color: '#cbd5e1' }}>
                      Status: <strong>{draftResult.verification.status}</strong>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => setShowInspector(true)}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 8px', borderRadius: '4px', background: '#0f172a', border: '1px solid #475569', color: '#38bdf8', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}
                >
                  <Cpu size={12} /> Inspect Solvers
                </button>
              </div>

              {/* Draft Content (View / Edit) */}
              <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '16px', marginBottom: '16px', flex: 1, overflowY: 'auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: '#38bdf8' }}>Question Body</span>
                  <button
                    onClick={() => setIsEditingDraft(!isEditingDraft)}
                    style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '11px', cursor: 'pointer' }}
                  >
                    <Edit2 size={12} /> {isEditingDraft ? 'Cancel Edit' : 'Edit Text'}
                  </button>
                </div>

                {isEditingDraft ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <textarea
                      value={editedBody}
                      onChange={(e) => setEditedBody(e.target.value)}
                      rows={4}
                      style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#1e293b', border: '1px solid #475569', color: '#f8fafc', fontSize: '13px' }}
                    />
                    <div>
                      <label style={{ fontSize: '11px', color: '#94a3b8' }}>Answer Key:</label>
                      <input
                        type="text"
                        value={editedAnswer}
                        onChange={(e) => setEditedAnswer(e.target.value)}
                        style={{ width: '100%', padding: '6px', borderRadius: '4px', background: '#1e293b', border: '1px solid #475569', color: '#f8fafc', fontSize: '13px' }}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: '11px', color: '#94a3b8' }}>Solution Steps:</label>
                      <textarea
                        value={editedSolution}
                        onChange={(e) => setEditedSolution(e.target.value)}
                        rows={3}
                        style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#1e293b', border: '1px solid #475569', color: '#f8fafc', fontSize: '13px' }}
                      />
                    </div>
                  </div>
                ) : (
                  <div>
                    <div style={{ fontSize: '14px', lineHeight: 1.5, marginBottom: '12px', whiteSpace: 'pre-wrap', color: '#f1f5f9' }}>
                      {editedBody}
                    </div>

                    {draftResult.draft.options && (
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', marginBottom: '12px' }}>
                        {draftResult.draft.options.map((opt, i) => (
                          <div key={i} style={{ padding: '6px 10px', borderRadius: '4px', background: '#1e293b', fontSize: '12px', color: '#cbd5e1' }}>
                            {opt}
                          </div>
                        ))}
                      </div>
                    )}

                    <div style={{ borderTop: '1px solid #1e293b', paddingTop: '10px', fontSize: '13px' }}>
                      <span style={{ color: '#38bdf8', fontWeight: 600 }}>Answer: </span>
                      <span style={{ color: '#22c55e', background: 'rgba(34, 197, 94, 0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                        {editedAnswer}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                <button
                  onClick={() => handleSaveToBank(false)}
                  disabled={loading}
                  style={{ flex: 1, padding: '10px 16px', borderRadius: '6px', background: '#334155', border: 'none', color: '#f8fafc', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}
                >
                  Save as Unverified
                </button>

                <button
                  onClick={() => handleSaveToBank(true)}
                  disabled={loading}
                  style={{ flex: 1, padding: '10px 16px', borderRadius: '6px', background: '#16a34a', border: 'none', color: '#ffffff', fontSize: '13px', fontWeight: 700, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px', cursor: 'pointer' }}
                >
                  <ShieldCheck size={16} /> Approve & Save
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Solve-Twice Inspector Modal */}
      {showInspector && draftResult && (
        <SolveTwiceInspectorModal
          question={{
            id: 'draft',
            short_id: 'DRAFT',
            long_id: 'DRAFT-PREVIEW',
            origin: draftResult.mode as any,
            owner_teacher_id: '',
            current_version: 1,
            version_data: {
              id: 'draft-v1',
              version: 1,
              body: editedBody,
              options: draftResult.draft.options,
              answer: editedAnswer,
              solution: editedSolution,
              verification_status: draftResult.verification.status,
              meta: {},
              verification_runs: [
                {
                  run_no: 1,
                  solver_model: draftResult.verification.solver1.model,
                  answer: draftResult.verification.solver1.answer,
                  steps: draftResult.verification.solver1.steps,
                  agree: draftResult.verification.agree,
                  diff_notes: draftResult.verification.diff_notes,
                },
                {
                  run_no: 2,
                  solver_model: draftResult.verification.solver2.model,
                  answer: draftResult.verification.solver2.answer,
                  steps: draftResult.verification.solver2.steps,
                  agree: draftResult.verification.agree,
                  diff_notes: draftResult.verification.diff_notes,
                },
              ],
            },
            created_at: new Date().toISOString(),
          }}
          onClose={() => setShowInspector(false)}
          onApprove={() => handleSaveToBank(true)}
        />
      )}

      {/* Question Set Importer Modal */}
      {showImporter && (
        <QuestionSetImporterModal
          onClose={() => setShowImporter(false)}
          onImportSuccess={() => setSuccessMsg('Question set successfully imported with Solve-Twice verification!')}
        />
      )}
    </div>
  );
};
