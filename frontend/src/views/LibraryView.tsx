import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { EmptyState } from '../components/EmptyState';
import {
  BookOpen,
  UploadCloud,
  Search,
  FileText,
  Trash2,
} from 'lucide-react';

export const LibraryView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'files' | 'search' | 'syllabus'>('files');
  const [files, setFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<any | null>(null);
  const [fileDetails, setFileDetails] = useState<any | null>(null);
  const [syllabusTree, setSyllabusTree] = useState<any>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  // Upload modal state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedUploadFile, setSelectedUploadFile] = useState<File | null>(null);
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(true);
  const [uploading, setUploading] = useState(false);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchKind, setSearchKind] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  const loadFiles = async () => {
    try {
      const data = await api.getLibraryFiles();
      setFiles(data);
    } catch (err: any) {
      console.error(err);
    }
  };

  const loadSyllabus = async () => {
    try {
      const data = await api.getSyllabusTree();
      setSyllabusTree(data.tree);
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadFiles();
    loadSyllabus();
  }, []);

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUploadFile) {
      alert('Please select a PDF file to upload.');
      return;
    }
    if (!disclaimerAccepted) {
      alert('You must accept the copyright disclaimer to upload teaching materials.');
      return;
    }

    setUploading(true);
    try {
      await api.uploadLibraryFile(selectedUploadFile, disclaimerAccepted);
      setShowUploadModal(false);
      setSelectedUploadFile(null);
      setFeedback('Book uploaded and indexed successfully into your private library.');
      await loadFiles();
    } catch (err: any) {
      alert(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteFile = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this book and its indexed chunks?')) return;
    try {
      await api.deleteLibraryFile(fileId);
      setFeedback('Book deleted from your library.');
      if (selectedFile?.id === fileId) {
        setSelectedFile(null);
        setFileDetails(null);
      }
      loadFiles();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleInspectFile = async (file: any) => {
    setSelectedFile(file);
    try {
      const details = await api.getFileDetails(file.id);
      setFileDetails(details);
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const res = await api.searchLibrary(searchQuery.trim(), 10, undefined, searchKind || undefined);
      setSearchResults(res.results || []);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="page-body">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1>Private Academic Library (RAG)</h1>
            <span className="badge badge-approved">Private to You</span>
          </div>
          <p className="lead">
            Upload textbooks, lecture notes, or question banks. The RAG engine parses, chunks, and tags content for verified question generation.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`btn btn-sm ${activeTab === 'files' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('files')}
          >
            My Books ({files.length})
          </button>
          <button
            className={`btn btn-sm ${activeTab === 'search' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('search')}
          >
            Search Inside Files
          </button>
          <button
            className={`btn btn-sm ${activeTab === 'syllabus' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('syllabus')}
          >
            Curriculum Syllabus Tree
          </button>
          <button
            className="btn btn-sm btn-primary"
            onClick={() => setShowUploadModal(true)}
            style={{ marginLeft: '8px' }}
          >
            <UploadCloud size={15} /> Upload PDF
          </button>
        </div>
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

      {/* TAB 1: MY BOOKS */}
      {activeTab === 'files' && (
        <div style={{ display: 'grid', gridTemplateColumns: selectedFile ? '1fr 1fr' : '1fr', gap: '24px' }}>
          <div className="card">
            <div className="card-header">
              <h2>Uploaded Books & Documents</h2>
              <span className="badge badge-info">{files.length} Books</span>
            </div>

            {files.length === 0 ? (
              <EmptyState
                icon={<BookOpen size={28} />}
                title="Your Private Library is Empty"
                description="Upload standard textbooks or question banks in PDF format. Content remains strictly private to your account (Rules.md A.3)."
                actionText="Upload First Book"
                onAction={() => setShowUploadModal(true)}
                secondaryText="Supported: ICSE, ISC, JEE, NEET syllabus seeds for PCM+CS"
              />
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {files.map((file) => (
                  <div
                    key={file.id}
                    style={{
                      border: selectedFile?.id === file.id ? '2px solid var(--primary)' : '1px solid var(--line)',
                      borderRadius: 'var(--radius-md)',
                      padding: '16px',
                      background: 'var(--surface)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                    onClick={() => handleInspectFile(file)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                      <div style={{
                        width: 40,
                        height: 40,
                        borderRadius: 'var(--radius-md)',
                        background: 'var(--primary-light)',
                        color: 'var(--primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <FileText size={20} />
                      </div>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '15px' }}>{file.filename}</div>
                        <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '2px' }}>
                          {(file.file_size / 1024).toFixed(1)} KB · {file.metadata?.chunks_count ?? 0} indexed chunks
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      {file.status === 'READY' ? (
                        <span className="badge badge-approved">Ready</span>
                      ) : (
                        <span className="badge badge-unverified">Processing</span>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteFile(file.id);
                        }}
                        className="btn btn-sm btn-secondary"
                        style={{ color: 'var(--bad)', padding: '6px 10px' }}
                        title="Delete Book"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* File Chunk Inspector */}
          {selectedFile && fileDetails && (
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 style={{ fontSize: '16px' }}>Indexed Chunks: {fileDetails.filename}</h3>
                  <span style={{ fontSize: '12px', color: 'var(--muted)' }}>
                    {fileDetails.total_chunks} Chunks · Detected Chapters: {fileDetails.metadata?.detected_chapters?.join(', ') || 'General'}
                  </span>
                </div>
                <button
                  onClick={() => { setSelectedFile(null); setFileDetails(null); }}
                  className="btn btn-sm btn-secondary"
                >
                  Close
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '550px', overflowY: 'auto' }}>
                {fileDetails.chunks_preview?.map((c: any) => (
                  <div
                    key={c.id}
                    style={{
                      border: '1px solid var(--line)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '12px',
                      background: 'var(--bg)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span className="id-chip">Page {c.page_number}</span>
                      <span className={`badge ${c.kind === 'question' ? 'badge-info' : c.kind === 'solution' ? 'badge-approved' : 'badge-unverified'}`}>
                        {c.kind}
                      </span>
                    </div>
                    {c.chapter && (
                      <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--primary)', marginBottom: '4px' }}>
                        {c.chapter} {c.topic && `· ${c.topic}`}
                      </div>
                    )}
                    <p style={{ fontSize: '13px', color: 'var(--ink-secondary)', lineHeight: 1.4 }}>
                      {c.content_snippet}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: HYBRID SEARCH */}
      {activeTab === 'search' && (
        <div className="card">
          <div className="card-header">
            <div>
              <h2>Search Inside Your Library</h2>
              <p className="lead">Rules.md A.3 & A.4: Hybrid semantic + BM25 keyword search across your private indexed books.</p>
            </div>
          </div>

          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', marginBottom: '24px' }}>
            <div style={{ flex: 1, position: 'relative' }}>
              <input
                type="text"
                className="input"
                placeholder="Search formulas, concepts, or questions (e.g. integration by parts, Coulomb's law)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                required
              />
            </div>
            <select
              className="select"
              style={{ width: '160px' }}
              value={searchKind}
              onChange={(e) => setSearchKind(e.target.value)}
            >
              <option value="">All Kinds</option>
              <option value="question">Questions Only</option>
              <option value="theory">Theory Only</option>
              <option value="solution">Solutions</option>
            </select>
            <button type="submit" disabled={searching} className="btn btn-primary">
              <Search size={15} /> {searching ? 'Searching...' : 'Search'}
            </button>
          </form>

          {searchResults.length === 0 ? (
            <EmptyState
              icon={<Search size={28} />}
              title={searchQuery ? "No Matching Chunks Found" : "Search Your Private Books"}
              description={
                searchQuery
                  ? "Try adjusting your search query or uploading additional reference materials."
                  : "Type a query above to retrieve relevant theory paragraphs, questions, and page citations."
              }
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {searchResults.map((res) => (
                <div
                  key={res.chunk_id}
                  style={{
                    border: '1px solid var(--line)',
                    borderRadius: 'var(--radius-md)',
                    padding: '16px',
                    background: 'var(--surface)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="badge badge-info">{res.kind}</span>
                      {res.chapter && (
                        <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--primary)' }}>
                          {res.chapter} {res.topic && `· ${res.topic}`}
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="id-chip" title="Similarity Score">
                        Match {(res.score * 100).toFixed(0)}%
                      </span>
                      <span className="badge badge-approved" title="Teacher Only Source Label (Rules.md A.4)">
                        {res.source_label}
                      </span>
                    </div>
                  </div>

                  <p style={{ fontSize: '14px', color: 'var(--ink)', lineHeight: 1.5, fontFamily: res.kind === 'question' ? 'var(--font-serif)' : 'inherit' }}>
                    {res.content}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: CURRICULUM SYLLABUS TREE */}
      {activeTab === 'syllabus' && (
        <div className="card">
          <div className="card-header">
            <div>
              <h2>Configured Syllabus Hierarchy</h2>
              <p className="lead">Seeded ICSE & ISC Class 10/12 PCM+CS chapter trees used for auto-tagging and question constraints.</p>
            </div>
          </div>

          {!syllabusTree ? (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>Loading syllabus tree...</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {Object.entries(syllabusTree).map(([board, classes]: [string, any]) => (
                <div key={board} style={{ border: '1px solid var(--line)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
                  <h3 style={{ color: 'var(--primary)', marginBottom: '12px' }}>{board} Curriculum</h3>
                  {Object.entries(classes).map(([classLvl, subjects]: [string, any]) => (
                    <div key={classLvl} style={{ marginLeft: '12px', marginBottom: '16px' }}>
                      <h4 style={{ fontSize: '14px', marginBottom: '8px' }}>{classLvl}</h4>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
                        {Object.entries(subjects).map(([subject, chapters]: [string, any]) => (
                          <div
                            key={subject}
                            style={{
                              background: 'var(--bg)',
                              borderRadius: 'var(--radius-sm)',
                              padding: '12px',
                              border: '1px solid var(--line)',
                            }}
                          >
                            <div style={{ fontWeight: 600, fontSize: '13px', marginBottom: '6px' }}>{subject}</div>
                            <ul style={{ paddingLeft: '16px', fontSize: '12px', color: 'var(--muted)' }}>
                              {Object.keys(chapters).slice(0, 4).map((ch) => (
                                <li key={ch}>{ch}</li>
                              ))}
                              {Object.keys(chapters).length > 4 && (
                                <li style={{ fontStyle: 'italic' }}>+{Object.keys(chapters).length - 4} more chapters</li>
                              )}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Upload PDF Modal */}
      {showUploadModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <h2 style={{ marginBottom: '16px' }}>Upload Teaching Document (PDF)</h2>
            <form onSubmit={handleUploadSubmit}>
              <div className="form-group">
                <label className="form-label">Select PDF File (Max 50MB)</label>
                <input
                  type="file"
                  accept="application/pdf"
                  className="input"
                  required
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setSelectedUploadFile(e.target.files[0]);
                    }
                  }}
                />
              </div>

              {/* Copyright Disclaimer per Rules.md D.8 */}
              <div style={{
                background: 'var(--info-bg)',
                border: '1px solid rgba(28, 126, 214, 0.2)',
                borderRadius: 'var(--radius-md)',
                padding: '14px',
                marginTop: '16px',
                marginBottom: '20px',
              }}>
                <label style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={disclaimerAccepted}
                    onChange={(e) => setDisclaimerAccepted(e.target.checked)}
                    style={{ marginTop: '3px' }}
                    required
                  />
                  <span style={{ fontSize: '13px', color: 'var(--ink)' }}>
                    <strong>Copyright Disclaimer (Rules.md D.8):</strong> I confirm that I have the legal right to use this material for teaching. Uploaded files remain private to my account and will not be distributed publicly.
                  </span>
                </label>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="btn btn-secondary"
                  disabled={uploading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading || !disclaimerAccepted}
                  className="btn btn-primary"
                >
                  {uploading ? 'Parsing & Indexing...' : 'Upload & Process PDF'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
