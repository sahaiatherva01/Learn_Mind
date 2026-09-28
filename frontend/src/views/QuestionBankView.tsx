import {
  Search,
  Filter,
  Bookmark,
  Database,
  X,
  AlertTriangle
} from 'lucide-react';
import { api } from '../api';
import type { QuestionItem, User } from '../types';
import { QuestionCard } from '../components/QuestionCard';
import { SolveTwiceInspectorModal } from '../components/SolveTwiceInspectorModal';

interface QuestionBankViewProps {
  currentUser: User;
}

export const QuestionBankView: React.FC<QuestionBankViewProps> = ({ currentUser }) => {
  const isTeacher = ['ADMIN', 'INCHARGE', 'CLASS_TEACHER', 'SUBJECT_TEACHER'].includes(currentUser.role);

  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedClass, setSelectedClass] = useState<number | undefined>();
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [selectedOrigin, setSelectedOrigin] = useState<string>('');

  const [bookmarkedQids, setBookmarkedQids] = useState<Set<string>>(new Set());
  const [favouritedQids, setFavouritedQids] = useState<Set<string>>(new Set());
  const [filterOnlyBookmarks, setFilterOnlyBookmarks] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Inspector & Version Modals
  const [inspectQuestion, setInspectQuestion] = useState<QuestionItem | null>(null);
  const [editQuestionItem, setEditQuestionItem] = useState<QuestionItem | null>(null);
  const [editBody, setEditBody] = useState('');
  const [editAnswer, setEditAnswer] = useState('');
  const [editSolution, setEditSolution] = useState('');

  useEffect(() => {
    loadQuestions();
    loadBookmarks();
  }, [selectedSubject, selectedClass, selectedStatus, selectedOrigin]);

  const loadQuestions = async (queryText: string = searchQuery) => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.searchQuestions({
        q: queryText || undefined,
        subject: selectedSubject || undefined,
        class_level: selectedClass || undefined,
        status: selectedStatus || undefined,
        origin: selectedOrigin || undefined,
        limit: 50,
      });
      setQuestions(res.questions || []);
      setTotalCount(res.total || 0);
    } catch (err: any) {
      setError(err?.message || 'Failed to search question bank');
    } finally {
      setLoading(false);
    }
  };

  const loadBookmarks = async () => {
    try {
      const qids = await api.listBookmarks();
      setBookmarkedQids(new Set(qids || []));
    } catch (err) {
      console.error('Failed to load bookmarks', err);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadQuestions(searchQuery);
  };

  const handleStatusChange = async (qid: string, version: number, newStatus: string) => {
    try {
      await api.updateQuestionStatus(qid, version, newStatus);
      setQuestions((prev) =>
        prev.map((q) => {
          if (q.id === qid) {
            return {
              ...q,
              version_data: {
                ...q.version_data,
                verification_status: newStatus as any,
              },
            };
          }
          return q;
        })
      );
    } catch (err: any) {
      alert(err?.message || 'Failed to update status');
    }
  };

  const handleToggleBookmark = async (qid: string) => {
    try {
      const res = await api.toggleBookmark(qid);
      setBookmarkedQids((prev) => {
        const next = new Set(prev);
        if (res.bookmarked) next.add(qid);
        else next.delete(qid);
        return next;
      });
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleFavourite = async (qid: string) => {
    try {
      const res = await api.toggleFavourite(qid);
      setFavouritedQids((prev) => {
        const next = new Set(prev);
        if (res.favourited) next.add(qid);
        else next.delete(qid);
        return next;
      });
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpenEditVersion = (q: QuestionItem) => {
    setEditQuestionItem(q);
    setEditBody(q.version_data.body);
    setEditAnswer(q.version_data.answer);
    setEditSolution(q.version_data.solution || '');
  };

  const handleSubmitNewVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editQuestionItem) return;

    try {
      setLoading(true);
      await api.createQuestionVersion(editQuestionItem.id, {
        body: editBody,
        options: editQuestionItem.version_data.options,
        answer: editAnswer,
        solution: editSolution,
        verification_status: 'UNVERIFIED',
      });
      setEditQuestionItem(null);
      loadQuestions();
    } catch (err: any) {
      alert(err?.message || 'Failed to create new version');
    } finally {
      setLoading(false);
    }
  };

  const displayedQuestions = filterOnlyBookmarks
    ? questions.filter((q) => bookmarkedQids.has(q.id))
    : questions;

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', color: '#f8fafc' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Database color="#38bdf8" /> Question Bank
          </h1>
          <p style={{ margin: 0, color: '#94a3b8', fontSize: '14px' }}>
            Multi-modal ID Search • Versioned Bank • {isTeacher ? 'Full Verification Audit & Management' : 'Approved Practice Questions'}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setFilterOnlyBookmarks(!filterOnlyBookmarks)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: '6px',
              background: filterOnlyBookmarks ? '#0284c7' : '#1e293b',
              border: '1px solid #334155',
              color: filterOnlyBookmarks ? '#ffffff' : '#38bdf8',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <Bookmark size={16} /> Bookmarks ({bookmarkedQids.size})
          </button>
        </div>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#ef4444', padding: '10px 14px', borderRadius: '6px', marginBottom: '16px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={16} /> {error}
        </div>
      )}

      {/* Omnibar Search Form */}
      <form onSubmit={handleSearchSubmit} style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', gap: '10px', background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '6px 12px', alignItems: 'center' }}>
          <Search size={18} color="#94a3b8" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Short ID (Q-8K3F2A), Long ID (MTH-12-CAL-DEF-000482), short@v2, or question text..."
            style={{ flex: 1, background: 'transparent', border: 'none', color: '#f8fafc', fontSize: '14px', outline: 'none' }}
          />
          <button
            type="submit"
            style={{ padding: '6px 16px', borderRadius: '6px', background: '#0284c7', border: 'none', color: '#ffffff', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}
          >
            Search
          </button>
        </div>
      </form>

      {/* Filters Bar */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '20px', alignItems: 'center', background: '#0f172a', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#94a3b8', fontSize: '12px', fontWeight: 600 }}>
          <Filter size={14} /> Filters:
        </div>

        {/* Subject Filter */}
        <select
          value={selectedSubject}
          onChange={(e) => setSelectedSubject(e.target.value)}
          style={{ padding: '6px 10px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '12px' }}
        >
          <option value="">All Subjects</option>
          <option value="Mathematics">Mathematics</option>
          <option value="Physics">Physics</option>
          <option value="Chemistry">Chemistry</option>
          <option value="Computer Science">Computer Science</option>
        </select>

        {/* Class Filter */}
        <select
          value={selectedClass || ''}
          onChange={(e) => setSelectedClass(e.target.value ? Number(e.target.value) : undefined)}
          style={{ padding: '6px 10px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '12px' }}
        >
          <option value="">All Classes</option>
          <option value="9">Class 9</option>
          <option value="10">Class 10</option>
          <option value="11">Class 11</option>
          <option value="12">Class 12</option>
        </select>

        {/* Status Filter (Teacher only) */}
        {isTeacher && (
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            style={{ padding: '6px 10px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '12px' }}
          >
            <option value="">All Verification Statuses</option>
            <option value="APPROVED">Approved</option>
            <option value="UNVERIFIED">Unverified (Auto ✓)</option>
            <option value="NEEDS_REVIEW">Needs Review ⚠</option>
            <option value="REJECTED">Rejected</option>
          </select>
        )}

        {/* Origin Filter */}
        <select
          value={selectedOrigin}
          onChange={(e) => setSelectedOrigin(e.target.value)}
          style={{ padding: '6px 10px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '12px' }}
        >
          <option value="">All Origins</option>
          <option value="AI_SIMILAR">AI Similar</option>
          <option value="AI_HIGHER">AI Higher Order</option>
          <option value="SOURCE_COPY">Source Copy</option>
          <option value="TEACHER_AUTHORED">Teacher Authored</option>
        </select>

        <button
          onClick={() => {
            setSelectedSubject('');
            setSelectedClass(undefined);
            setSelectedStatus('');
            setSelectedOrigin('');
            setSearchQuery('');
            loadQuestions('');
          }}
          style={{ marginLeft: 'auto', background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '12px', cursor: 'pointer', textDecoration: 'underline' }}
        >
          Reset Filters
        </button>
      </div>

      {/* Results Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', color: '#94a3b8', fontSize: '13px' }}>
        <span>Showing <strong>{displayedQuestions.length}</strong> of <strong>{totalCount}</strong> questions in bank</span>
        {loading && <span style={{ color: '#38bdf8' }}>Searching bank...</span>}
      </div>

      {/* Questions List */}
      {displayedQuestions.length === 0 && !loading ? (
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
          <Database size={40} style={{ opacity: 0.3, marginBottom: '12px' }} />
          <div style={{ fontSize: '16px', fontWeight: 600, color: '#cbd5e1', marginBottom: '4px' }}>No Questions Found</div>
          <div style={{ fontSize: '13px' }}>Try adjusting your search query or filter selections.</div>
        </div>
      ) : (
        <div>
          {displayedQuestions.map((q) => (
            <QuestionCard
              key={`${q.id}-v${q.version_data.version}`}
              question={q}
              isTeacher={isTeacher}
              onStatusChange={handleStatusChange}
              onOpenInspector={(item) => setInspectQuestion(item)}
              onEditVersion={handleOpenEditVersion}
              isBookmarked={bookmarkedQids.has(q.id)}
              isFavourited={favouritedQids.has(q.id)}
              onToggleBookmark={handleToggleBookmark}
              onToggleFavourite={handleToggleFavourite}
            />
          ))}
        </div>
      )}

      {/* Solve-Twice Inspector Modal */}
      {inspectQuestion && (
        <SolveTwiceInspectorModal
          question={inspectQuestion}
          onClose={() => setInspectQuestion(null)}
          onApprove={(qid, version) => handleStatusChange(qid, version, 'APPROVED')}
        />
      )}

      {/* Edit & Version Modal */}
      {editQuestionItem && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '12px', width: '100%', maxWidth: '650px', maxHeight: '90vh', overflowY: 'auto', color: '#f8fafc', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #1e293b', paddingBottom: '12px' }}>
              <div>
                <h2 style={{ fontSize: '17px', fontWeight: 700, margin: 0 }}>Create New Version (v{editQuestionItem.current_version + 1})</h2>
                <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                  Rules.md B.2: Immutable QID {editQuestionItem.short_id} ({editQuestionItem.long_id})
                </div>
              </div>
              <button onClick={() => setEditQuestionItem(null)} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmitNewVersion}>
              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Question Body:</label>
                <textarea
                  value={editBody}
                  onChange={(e) => setEditBody(e.target.value)}
                  rows={4}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
                />
              </div>

              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Answer Key:</label>
                <input
                  type="text"
                  value={editAnswer}
                  onChange={(e) => setEditAnswer(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
                />
              </div>

              <div style={{ marginBottom: '18px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>Solution Steps & Derivation:</label>
                <textarea
                  value={editSolution}
                  onChange={(e) => setEditSolution(e.target.value)}
                  rows={3}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', fontSize: '13px' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                <button
                  type="button"
                  onClick={() => setEditQuestionItem(null)}
                  style={{ padding: '8px 16px', borderRadius: '6px', background: '#334155', border: 'none', color: '#f8fafc', fontSize: '13px', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  style={{ padding: '8px 20px', borderRadius: '6px', background: '#0284c7', border: 'none', color: '#ffffff', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}
                >
                  Save as v{editQuestionItem.current_version + 1}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
