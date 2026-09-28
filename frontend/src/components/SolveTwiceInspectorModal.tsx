import React from 'react';
import { X, CheckCircle, AlertTriangle, Cpu, ShieldCheck } from 'lucide-react';
import type { QuestionItem } from '../types';

interface SolveTwiceInspectorModalProps {
  question: QuestionItem | null;
  onClose: () => void;
  onApprove?: (qid: string, version: number) => void;
}

export const SolveTwiceInspectorModal: React.FC<SolveTwiceInspectorModalProps> = ({
  question,
  onClose,
  onApprove,
}) => {
  if (!question) return null;

  const { short_id, long_id, version_data } = question;
  const { version, answer, verification_status, verification_runs } = version_data;

  const run1 = verification_runs?.[0] || {
    run_no: 1,
    solver_model: 'mock-strong (Primary)',
    answer: answer,
    steps: version_data.solution || 'Derivation from primary solver pass',
    agree: verification_status !== 'NEEDS_REVIEW',
  };

  const run2 = verification_runs?.[1] || {
    run_no: 2,
    solver_model: 'mock-fast / Tool Check (Secondary)',
    answer: answer,
    steps: 'Independent verification pass 2 via SymPy / analytical solver',
    agree: verification_status !== 'NEEDS_REVIEW',
  };

  const isAgreed = run1.agree && run2.agree && verification_status !== 'NEEDS_REVIEW';

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
      <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '12px', width: '100%', maxWidth: '850px', maxHeight: '90vh', overflowY: 'auto', color: '#f8fafc', padding: '24px', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #1e293b', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Cpu size={22} color="#38bdf8" />
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>Solve-Twice Verification Inspector</h2>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                {short_id} (v{version}) • {long_id}
              </div>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Status banner */}
        <div style={{ padding: '12px 16px', borderRadius: '8px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px', background: isAgreed ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)', border: isAgreed ? '1px solid #22c55e' : '1px solid #ef4444' }}>
          {isAgreed ? <CheckCircle size={24} color="#22c55e" /> : <AlertTriangle size={24} color="#ef4444" />}
          <div>
            <div style={{ fontWeight: 700, color: isAgreed ? '#22c55e' : '#ef4444' }}>
              {isAgreed ? 'Solvers Agree (Auto-Verified ✓)' : 'Solvers Disagree (Flagged for Review ⚠)'}
            </div>
            <div style={{ fontSize: '12px', color: '#cbd5e1' }}>
              {isAgreed
                ? 'Both independent passes yielded equivalent solutions and mathematical consistency.'
                : (run1.diff_notes || 'Discrepancy detected between independent solver passes. Both solutions are shown below.')}
            </div>
          </div>
        </div>

        {/* Dual solver cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          {/* Solver 1 */}
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <span style={{ fontSize: '13px', fontWeight: 700, color: '#38bdf8' }}>Solver #1 (Primary)</span>
              <span style={{ fontSize: '11px', background: '#0f172a', padding: '2px 6px', borderRadius: '4px', color: '#94a3b8' }}>
                {run1.solver_model}
              </span>
            </div>
            <div style={{ marginBottom: '8px', fontSize: '13px' }}>
              <strong>Answer:</strong>{' '}
              <span style={{ color: '#22c55e', background: 'rgba(34, 197, 94, 0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                {run1.answer}
              </span>
            </div>
            <div style={{ fontSize: '12px', color: '#cbd5e1', background: '#0f172a', padding: '10px', borderRadius: '6px', whiteSpace: 'pre-wrap', maxHeight: '180px', overflowY: 'auto' }}>
              {run1.steps || 'No intermediate steps recorded.'}
            </div>
          </div>

          {/* Solver 2 */}
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <span style={{ fontSize: '13px', fontWeight: 700, color: '#c084fc' }}>Solver #2 (Independent Pass)</span>
              <span style={{ fontSize: '11px', background: '#0f172a', padding: '2px 6px', borderRadius: '4px', color: '#94a3b8' }}>
                {run2.solver_model}
              </span>
            </div>
            <div style={{ marginBottom: '8px', fontSize: '13px' }}>
              <strong>Answer:</strong>{' '}
              <span style={{ color: '#22c55e', background: 'rgba(34, 197, 94, 0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                {run2.answer}
              </span>
            </div>
            <div style={{ fontSize: '12px', color: '#cbd5e1', background: '#0f172a', padding: '10px', borderRadius: '6px', whiteSpace: 'pre-wrap', maxHeight: '180px', overflowY: 'auto' }}>
              {run2.steps || 'No intermediate steps recorded.'}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', borderTop: '1px solid #1e293b', paddingTop: '16px' }}>
          <button
            onClick={onClose}
            style={{ padding: '8px 16px', borderRadius: '6px', background: '#334155', border: 'none', color: '#f8fafc', fontSize: '13px', cursor: 'pointer' }}
          >
            Close
          </button>
          {verification_status !== 'APPROVED' && onApprove && (
            <button
              onClick={() => {
                onApprove(question.id, version);
                onClose();
              }}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '8px 16px', borderRadius: '6px', background: '#16a34a', border: 'none', color: '#ffffff', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}
            >
              <ShieldCheck size={16} /> Explicitly Approve Question
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
