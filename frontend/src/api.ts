import type { User, Section, Subject, StudentEnrollment, TeacherAssignment } from './types';

const API_BASE = '/api/v1';

function getAuthHeader(): HeadersInit {
  const token = localStorage.getItem('learn_mind_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data?.error?.message || data?.message || 'Request failed';
    throw new Error(errorMsg);
  }

  return data as T;
}

export const api = {
  // Auth
  async registerSchool(payload: any) {
    return request<{ access_token: string; user: User }>('/auth/register-school', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async registerTeacher(payload: any) {
    return request<User>('/auth/register-teacher', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async registerStudent(payload: any) {
    return request<{ access_token: string; user: User }>('/auth/register-student', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async login(payload: any) {
    return request<{ access_token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getMe() {
    return request<User>('/auth/me');
  },

  // Sections & Subjects
  async getSections() {
    return request<Section[]>('/sections');
  },

  async createSection(payload: { class_level: number; section_name: string; class_teacher_id?: string }) {
    return request<Section>('/sections', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getSubjects() {
    return request<Subject[]>('/subjects');
  },

  async createSubject(payload: { name: string; code: string }) {
    return request<Subject>('/subjects', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async assignTeacherToSection(payload: { teacher_id: string; section_id: string; subject_id: string }) {
    return request<TeacherAssignment>('/sections/assign-teacher', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Incharge
  async getInchargeDashboard() {
    return request<{ stats: Record<string, number> }>('/incharge/dashboard');
  },

  async getInchargeTeachers(statusFilter?: string) {
    const query = statusFilter ? `?status_filter=${statusFilter}` : '';
    return request<User[]>(`/incharge/teachers${query}`);
  },

  async approveTeacher(teacherId: string, role?: string) {
    return request<User>(`/incharge/teachers/${teacherId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ role }),
    });
  },

  async rejectTeacher(teacherId: string) {
    return request<User>(`/incharge/teachers/${teacherId}/reject`, {
      method: 'POST',
    });
  },

  async getInchargeEnrollments(statusFilter?: string) {
    const query = statusFilter ? `?status_filter=${statusFilter}` : '';
    return request<StudentEnrollment[]>(`/incharge/enrollments${query}`);
  },

  async approveInchargeEnrollment(enrollmentId: string) {
    return request<StudentEnrollment>(`/incharge/enrollments/${enrollmentId}/approve`, {
      method: 'POST',
    });
  },

  async rejectInchargeEnrollment(enrollmentId: string) {
    return request<StudentEnrollment>(`/incharge/enrollments/${enrollmentId}/reject`, {
      method: 'POST',
    });
  },

  // Teacher
  async getTeacherDashboard() {
    return request<any>('/teacher/dashboard');
  },

  async getTeacherAssignments() {
    return request<TeacherAssignment[]>('/teacher/assignments');
  },

  async getTeacherStudentsRoster(sectionId?: string) {
    const query = sectionId ? `?section_id=${sectionId}` : '';
    return request<any[]>(`/teacher/students${query}`);
  },

  async getTeacherEnrollments() {
    return request<StudentEnrollment[]>('/teacher/enrollments');
  },

  async approveTeacherEnrollment(enrollmentId: string) {
    return request<StudentEnrollment>(`/teacher/enrollments/${enrollmentId}/approve`, {
      method: 'POST',
    });
  },

  async rejectTeacherEnrollment(enrollmentId: string) {
    return request<StudentEnrollment>(`/teacher/enrollments/${enrollmentId}/reject`, {
      method: 'POST',
    });
  },

  // Student
  async getStudentDashboard() {
    return request<any>('/student/dashboard');
  },

  async requestSectionEnrollment(sectionId: string) {
    return request<StudentEnrollment>('/student/request-enrollment', {
      method: 'POST',
      body: JSON.stringify({ section_id: sectionId }),
    });
  },

  // Library & RAG
  async uploadLibraryFile(file: File, disclaimerAccepted: boolean = true) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('disclaimer_accepted', disclaimerAccepted ? 'true' : 'false');

    const token = localStorage.getItem('learn_mind_token');
    const headers: HeadersInit = token ? { Authorization: `Bearer ${token}` } : {};

    const response = await fetch(`${API_BASE}/library/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data?.error?.message || data?.message || 'File upload failed');
    }
    return data;
  },

  async getLibraryFiles() {
    return request<any[]>('/library/files');
  },

  async getFileDetails(fileId: string) {
    return request<any>(`/library/files/${fileId}`);
  },

  async deleteLibraryFile(fileId: string) {
    return request<{ message: string }>(`/library/files/${fileId}`, {
      method: 'DELETE',
    });
  },

  async searchLibrary(query: string, topK: number = 5, chapter?: string, kind?: string) {
    let url = `/library/search?query=${encodeURIComponent(query)}&top_k=${topK}`;
    if (chapter) url += `&chapter=${encodeURIComponent(chapter)}`;
    if (kind) url += `&kind=${encodeURIComponent(kind)}`;
    return request<{ query: string; results_count: number; results: any[] }>(url);
  },

  async getSyllabusTree(board?: string) {
    const query = board ? `?board=${board}` : '';
    return request<{ total_nodes: number; tree: any }>(`/library/syllabus${query}`);
  },

  // --- Phase 2: Question Studio & Question Bank ---
  async getSubjectPacks() {
    return request<any[]>('/studio/subject-packs');
  },

  async generateDraftQuestion(payload: {
    subject: string;
    class_level: number;
    chapter: string;
    topic: string;
    question_type?: string;
    difficulty?: string;
    marks?: number;
    mode?: string;
    chunk_id?: string | null;
    mixed_topics?: string | null;
  }) {
    return request<any>('/studio/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async saveDraftQuestion(payload: any) {
    return request<any>('/studio/save-draft', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async interpretQuestionSet(payload: {
    raw_text: string;
    board?: string;
    class_level?: number;
    subject?: string;
  }) {
    return request<any>('/studio/interpret-set', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async confirmImportQuestionSet(payload: {
    questions: any[];
    source_ref?: string;
  }) {
    return request<any>('/studio/confirm-import-set', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async searchQuestions(params?: {
    q?: string;
    subject?: string;
    class_level?: number;
    chapter?: string;
    status?: string;
    origin?: string;
    limit?: number;
    offset?: number;
  }) {
    const searchParams = new URLSearchParams();
    if (params?.q) searchParams.append('q', params.q);
    if (params?.subject) searchParams.append('subject', params.subject);
    if (params?.class_level) searchParams.append('class_level', String(params.class_level));
    if (params?.chapter) searchParams.append('chapter', params.chapter);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.origin) searchParams.append('origin', params.origin);
    if (params?.limit) searchParams.append('limit', String(params.limit));
    if (params?.offset) searchParams.append('offset', String(params.offset));

    const qs = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<{ total: number; questions: any[] }>(`/questions/search${qs}`);
  },

  async getQuestionDetail(qid: string, version?: number) {
    const query = version ? `?v=${version}` : '';
    return request<any>(`/questions/${qid}${query}`);
  },

  async createQuestionManual(payload: any) {
    return request<any>('/questions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async createQuestionVersion(qid: string, payload: any) {
    return request<any>(`/questions/${qid}/versions`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async updateQuestionStatus(qid: string, version: number, status: string) {
    return request<any>(`/questions/${qid}/versions/${version}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },

  async toggleBookmark(qid: string) {
    return request<{ bookmarked: boolean; qid: string }>('/questions/bookmark', {
      method: 'POST',
      body: JSON.stringify({ qid }),
    });
  },

  async listBookmarks() {
    return request<string[]>('/questions/bookmarks/list');
  },

  async toggleFavourite(qid: string) {
    return request<{ favourited: boolean; qid: string }>('/questions/favourite', {
      method: 'POST',
      body: JSON.stringify({ qid }),
    });
  },

  async addOrUpdateNote(qid: string, note_text: string) {
    return request<{ qid: string; note_text: string }>('/questions/note', {
      method: 'POST',
      body: JSON.stringify({ qid, note_text }),
    });
  },

  async createCollection(name: string, description?: string) {
    return request<{ id: string; name: string }>('/questions/collections', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    });
  },

  async addToCollection(collection_id: string, qid: string, version: number = 1) {
    return request<any>('/questions/collections/items', {
      method: 'POST',
      body: JSON.stringify({ collection_id, qid, version }),
    });
  },
};

