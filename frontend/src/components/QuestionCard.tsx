import React, { useState } from 'react';
import {
  CheckCircle,
  AlertTriangle,
  Clock,
  XCircle,
  Bookmark,
  Star,
  Copy,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Cpu,
  Edit3
import type { QuestionItem } from '../types';

interface QuestionCardProps {
  question: QuestionItem;
  isTeacher?: boolean;
  onStatusChange?: (qid: string, version: number, newStatus: string) => void;
  onOpenInspector?: (question: QuestionItem) => void;
  onEditVersion?: (question: QuestionItem) => void;
  isBookmarked?: boolean;
  isFavourited?: boolean;
  onToggleBookmark?: (qid: string) => void;
  onToggleFavourite?: (qid: string) => void;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  isTeacher = false,
  onStatusChange,
  onOpenInspector,
  onEditVersion,
  isBookmarked = false,
  isFavourited = false,
  onToggleBookmark,
  onToggleFavourite,
}) => {
  const [showSolution, setShowSolution] = useState(false);
  const [copiedId, setCopiedId] = useState(false);

  const { short_id, long_id, origin, source_ref, version_data } = question;
  const { version, body, options, answer, solution, verification_status, meta, verification_runs } = version_data;

  const handleCopyId = () => {
    navigator.clipboard.writeText(short_id);
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
  };

  const getStatusBadge = () => {
    switch (verification_status) {
      case 'APPROVED':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600, background: 'rgba(34, 197, 94, 0.15)', color: '#22c55e' }}>
            <CheckCircle size={14} /> Approved
          </span>
        );
      case 'NEEDS_REVIEW':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600, background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' }}>
            <AlertTriangle size={14} /> Needs Review ⚠
          </span>
        );
      case 'REJECTED':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600, background: 'rgba(156, 163, 175, 0.15)', color: '#9ca3af' }}>
            <XCircle size={14} /> Rejected
          </span>
        );
      case 'UNVERIFIED':
      default:
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600, background: 'rgba(234, 179, 8, 0.15)', color: '#eab308' }}>
            <Clock size={14} /> Unverified (Auto ✓)
          </span>
        );
    }
  };

  const getOriginBadge = () => {
    let label: string = origin;
    let bg = 'rgba(59, 130, 246, 0.15)';
    let color = '#60a5fa';

    if (origin === 'SOURCE_COPY') {
      label = 'Source Copy';
      bg = 'rgba(168, 85, 247, 0.15)';
      color = '#c084fc';
    } else if (origin === 'AI_HIGHER') {
      label = 'Higher Order';
      bg = 'rgba(249, 115, 22, 0.15)';
      color = '#fb923c';
    } else if (origin === 'TEACHER_AUTHORED') {
      label = 'Teacher Authored';
      bg = 'rgba(20, 184, 166, 0.15)';
      color = '#2dd4bf';
    }

    return (
      <span style={{ padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 500, background: bg, color }}>
        {label}
      </span>
    );
  };

  return (
    <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '16px', marginBottom: '16px', color: '#f8fafc' }}>
      {/* Header bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <button
            onClick={handleCopyId}
            title="Click to copy Short ID"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '3px 8px', borderRadius: '4px', background: '#0f172a', border: '1px solid #475569', color: '#38bdf8', fontSize: '12px', fontWeight: 700, cursor: 'pointer' }}
          >
            <Copy size={12} /> {short_id} {copiedId && '✓'}
          </button>
          <span style={{ fontSize: '12px', color: '#94a3b8', fontFamily: 'monospace' }}>{long_id}</span>
          <span style={{ padding: '2px 6px', borderRadius: '4px', background: '#334155', color: '#cbd5e1', fontSize: '11px', fontWeight: 600 }}>
            v{version}
          </span>
          {getOriginBadge()}
          {getStatusBadge()}
        </div>

        {/* Action icons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {onToggleBookmark && (
            <button
              onClick={() => onToggleBookmark(question.id)}
              style={{ background: 'transparent', border: 'none', color: isBookmarked ? '#38bdf8' : '#64748b', cursor: 'pointer', padding: '4px' }}
              title={isBookmarked ? 'Remove Bookmark' : 'Bookmark'}
            >
              <Bookmark size={18} fill={isBookmarked ? '#38bdf8' : 'none'} />
            </button>
          )}
          {onToggleFavourite && (
            <button
              onClick={() => onToggleFavourite(question.id)}
              style={{ background: 'transparent', border: 'none', color: isFavourited ? '#eab308' : '#64748b', cursor: 'pointer', padding: '4px' }}
              title={isFavourited ? 'Remove Favourite' : 'Favourite'}
            >
              <Star size={18} fill={isFavourited ? '#eab308' : 'none'} />
            </button>
          )}
        </div>
      </div>

      {/* Metadata tags */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px', fontSize: '12px', color: '#94a3b8' }}>
        {meta?.subject && <span style={{ background: '#0f172a', padding: '2px 6px', borderRadius: '4px' }}>Subject: <strong>{meta.subject}</strong></span>}
        {meta?.class_level && <span style={{ background: '#0f172a', padding: '2px 6px', borderRadius: '4px' }}>Class: <strong>{meta.class_level}</strong></span>}
        {meta?.chapter && <span style={{ background: '#0f172a', padding: '2px 6px', borderRadius: '4px' }}>Chapter: <strong>{meta.chapter}</strong></span>}
        {meta?.topic && <span style={{ background: '#0f172a', padding: '2px 6px', borderRadius: '4px' }}>Topic: <strong>{meta.topic}</strong></span>}
        {meta?.marks && <span style={{ background: '#0f172a', padding: '2px 6px', borderRadius: '4px' }}>Marks: <strong>{meta.marks}</strong></span>}
        {meta?.difficulty && <span style={{ background: '#0f172a', padding: '2px 6px', borderRadius: '4px' }}>Diff: <strong>{meta.difficulty}</strong></span>}
      </div>

      {/* Teacher-only Source label per Rules.md A.4 */}
      {isTeacher && source_ref && (
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: '#c084fc', background: 'rgba(168, 85, 247, 0.1)', padding: '3px 8px', borderRadius: '4px', marginBottom: '12px' }}>
          <BookOpen size={12} /> Source: {source_ref} (Teacher only)
        </div>
      )}

      {/* Question Body */}
      <div style={{ fontSize: '15px', lineHeight: 1.6, marginBottom: '12px', whiteSpace: 'pre-wrap', color: '#f1f5f9' }}>
        {body}
      </div>

      {/* Options if MCQ */}
      {options && options.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '8px', marginBottom: '14px' }}>
          {options.map((opt, idx) => (
            <div
              key={idx}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                background: '#0f172a',
                border: '1px solid #334155',
                fontSize: '13px',
                color: '#e2e8f0',
              }}
            >
              {opt}
            </div>
          ))}
        </div>
      )}

      {/* Answer & Teacher Solution drawer */}
      <div style={{ borderTop: '1px solid #334155', paddingTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '13px', fontWeight: 600, color: '#38bdf8' }}>
            Answer Key: <span style={{ color: '#22c55e', background: 'rgba(34, 197, 94, 0.1)', padding: '2px 6px', borderRadius: '4px' }}>{answer}</span>
          </span>

          {isTeacher && solution && (
            <button
              onClick={() => setShowSolution(!showSolution)}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '12px', cursor: 'pointer' }}
            >
              {showSolution ? <ChevronUp size={14} /> : <ChevronDown size={14} />} {showSolution ? 'Hide Solution Steps' : 'View Solution Steps'}
            </button>
          )}
        </div>

        {/* Teacher Actions */}
        {isTeacher && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {onOpenInspector && (
              <button
                onClick={() => onOpenInspector(question)}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 8px', borderRadius: '4px', background: '#334155', border: 'none', color: '#f8fafc', fontSize: '12px', cursor: 'pointer' }}
                title="Inspect Solve-Twice verification runs"
              >
                <Cpu size={14} /> Solve-Twice ({verification_runs?.length || 2} runs)
              </button>
            )}

            {onEditVersion && (
              <button
                onClick={() => onEditVersion(question)}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 8px', borderRadius: '4px', background: '#334155', border: 'none', color: '#f8fafc', fontSize: '12px', cursor: 'pointer' }}
                title="Edit and create new version"
              >
                <Edit3 size={14} /> Edit (v{version + 1})
              </button>
            )}

            {verification_status !== 'APPROVED' && onStatusChange && (
              <button
                onClick={() => onStatusChange(question.id, version, 'APPROVED')}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 10px', borderRadius: '4px', background: '#16a34a', border: 'none', color: '#ffffff', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
              >
                Approve
              </button>
            )}
          </div>
        )}
      </div>

      {/* Expanded Solution for Teacher */}
      {isTeacher && showSolution && solution && (
        <div style={{ marginTop: '12px', padding: '12px', borderRadius: '6px', background: '#0f172a', border: '1px solid #1e293b', fontSize: '13px', color: '#cbd5e1' }}>
          <div style={{ fontWeight: 600, color: '#38bdf8', marginBottom: '6px' }}>Teacher Solution & Derivation:</div>
          <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>{solution}</div>
        </div>
      )}
    </div>
  );
};
