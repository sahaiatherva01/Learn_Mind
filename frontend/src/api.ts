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
};
