import React, { useState } from 'react';
import { X, UploadCloud, FileText, CheckCircle, AlertCircle, ArrowRight, Loader } from 'lucide-react';
import { api } from '../api';
import type { InterpretSetResponse } from '../types';

interface QuestionSetImporterModalProps {
  onClose: () => void;
  onImportSuccess?: () => void;
}

export const QuestionSetImporterModal: React.FC<QuestionSetImporterModalProps> = ({
  onClose,
  onImportSuccess,
}) => {
  const [step, setStep] = useState<'INPUT' | 'CONFIRM'>('INPUT');
  const [rawText, setRawText] = useState('');
  const [board, setBoard] = useState('ISC');
  const [classLevel, setClassLevel] = useState(12);
  const [subject, setSubject] = useState('Mathematics');
  const [sourceRef, setSourceRef] = useState('Imported Question Set 2026');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [interpretedData, setInterpretedData] = useState<InterpretSetResponse | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawText.trim()) {
      setError('Please paste question set text to analyze.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const res = await api.interpretQuestionSet({
        raw_text: rawText,
        board,
        class_level: classLevel,
        subject,
      });
      setInterpretedData(res);
      setStep('CONFIRM');
    } catch (err: any) {
      setError(err?.message || 'Failed to interpret question set');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!interpretedData || !interpretedData.questions.length) return;

    try {
      setLoading(true);
      setError(null);
      await api.confirmImportQuestionSet({
        questions: interpretedData.questions,
        source_ref: sourceRef,
      });
      if (onImportSuccess) onImportSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to import confirmed question set');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
      <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '12px', width: '100%', maxWidth: '850px', maxHeight: '90vh', overflowY: 'auto', color: '#f8fafc', padding: '24px', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #1e293b', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <UploadCloud size={24} color="#38bdf8" />
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Import Question Set</h2>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                G2 Interpretation Pipeline • Teacher Confirmation Step Required (Rules.md C.8)
              </div>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {error && (
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#ef4444', padding: '10px 14px', borderRadius: '6px', marginBottom: '16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={16} /> {error}
          </div>
        )}

        {/* STEP 1: Input and Configuration */}
        {step === 'INPUT' && (
          <form onSubmit={handleAnalyze}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Board / Exam</label>
                <select
                  value={board}
                  onChange={(e) => setBoard(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
                >
                  <option value="ICSE">ICSE</option>
                  <option value="ISC">ISC</option>
                  <option value="JEE">JEE</option>
                  <option value="NEET">NEET</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Class Level</label>
                <select
                  value={classLevel}
                  onChange={(e) => setClassLevel(Number(e.target.value))}
                  style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
                >
                  <option value={9}>Class 9</option>
                  <option value={10}>Class 10</option>
                  <option value={11}>Class 11</option>
                  <option value={12}>Class 12</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Subject</label>
                <select
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
                >
                  <option value="Mathematics">Mathematics</option>
                  <option value="Physics">Physics</option>
                  <option value="Chemistry">Chemistry</option>
                  <option value="Computer Science">Computer Science</option>
                </select>
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>
                Paste Raw Unformatted Questions / Exam Text:
              </label>
              <textarea
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="Example:&#10;Q1. Evaluate the integral of sin^2(x) from 0 to pi/2.&#10;Options: A) pi/4, B) pi/2, C) 1, D) 0&#10;Answer: A&#10;&#10;Q2. Solve dy/dx = 2x."
                rows={10}
                style={{ width: '100%', padding: '12px', borderRadius: '8px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px', fontFamily: 'monospace', resize: 'vertical' }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button
                type="button"
                onClick={onClose}
                style={{ padding: '8px 16px', borderRadius: '6px', background: '#334155', border: 'none', color: '#f8fafc', fontSize: '13px', cursor: 'pointer' }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '8px 20px', borderRadius: '6px', background: '#0284c7', border: 'none', color: '#ffffff', fontSize: '13px', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer' }}
              >
                {loading ? <Loader size={16} className="spin" /> : <ArrowRight size={16} />}
                {loading ? 'Analyzing Structure...' : 'Analyze & Interpret Set'}
              </button>
            </div>
          </form>
        )}

        {/* STEP 2: Interpretation Confirmation */}
        {step === 'CONFIRM' && interpretedData && (
          <div>
            {/* Interpretation Summary Box */}
            <div style={{ background: 'rgba(56, 189, 248, 0.1)', border: '1px solid #38bdf8', borderRadius: '8px', padding: '16px', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, color: '#38bdf8', marginBottom: '6px' }}>
                <FileText size={18} /> AI Interpretation Summary
              </div>
              <div style={{ fontSize: '14px', color: '#f1f5f9', lineHeight: 1.5 }}>
                {interpretedData.interpretation_summary}
              </div>
              <div style={{ marginTop: '10px', fontSize: '12px', color: '#94a3b8' }}>
                Total Questions Detected: <strong>{interpretedData.questions_count}</strong> • Subject: <strong>{interpretedData.detected_subject}</strong> • Class: <strong>{interpretedData.detected_class}</strong>
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>
                Source Citation / Reference Label (Teacher-Only):
              </label>
              <input
                type="text"
                value={sourceRef}
                onChange={(e) => setSourceRef(e.target.value)}
                style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
              />
            </div>

            {/* Extracted Questions Preview */}
            <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '12px', color: '#cbd5e1' }}>
              Extracted Questions Preview ({interpretedData.questions.length})
            </h3>

            <div style={{ maxHeight: '350px', overflowY: 'auto', marginBottom: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {interpretedData.questions.map((q, idx) => (
                <div key={idx} style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '12px', fontSize: '13px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', color: '#94a3b8', fontSize: '11px' }}>
                    <span>#{idx + 1} • Type: <strong>{q.question_type}</strong></span>
                    <span>Marks: <strong>{q.marks}</strong> | Diff: <strong>{q.difficulty}</strong></span>
                  </div>
                  <div style={{ color: '#f8fafc', whiteSpace: 'pre-wrap', marginBottom: '6px' }}>{q.body}</div>
                  <div style={{ color: '#38bdf8', fontSize: '12px' }}>Answer: <strong>{q.answer}</strong></div>
                </div>
              ))}
            </div>

            {/* Confirmation Actions */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #1e293b', paddingTop: '16px' }}>
              <button
                type="button"
                onClick={() => setStep('INPUT')}
                style={{ padding: '8px 16px', borderRadius: '6px', background: '#334155', border: 'none', color: '#f8fafc', fontSize: '13px', cursor: 'pointer' }}
              >
                Back to Edit Raw Input
              </button>

              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  type="button"
                  onClick={onClose}
                  style={{ padding: '8px 16px', borderRadius: '6px', background: '#334155', border: 'none', color: '#f8fafc', fontSize: '13px', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleConfirmImport}
                  disabled={loading}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '8px 20px', borderRadius: '6px', background: '#16a34a', border: 'none', color: '#ffffff', fontSize: '13px', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer' }}
                >
                  {loading ? <Loader size={16} className="spin" /> : <CheckCircle size={16} />}
                  {loading ? 'Importing & Verifying...' : 'Confirm Interpretation & Import to Bank'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
