export type UserRole = 'ADMIN' | 'INCHARGE' | 'CLASS_TEACHER' | 'SUBJECT_TEACHER' | 'STUDENT';
export type UserStatus = 'PENDING_APPROVAL' | 'ACTIVE' | 'REJECTED' | 'SUSPENDED';
export type EnrollmentStatus = 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED';

export interface User {
  id: string;
  school_id?: string | null;
  school_name?: string | null;
  email?: string | null;
  roll_number?: string | null;
  school_code?: string | null;
  teacher_code?: string | null;
  full_name: string;
  role: UserRole;
  status: UserStatus;
  created_at: string;
  enrollment?: {
    id: string;
    status: EnrollmentStatus;
    section_id: string;
    section_name: string;
    class_level: number;
    school_name?: string;
  } | null;
  assignments?: Array<{
    assignment_id: string;
    section_id: string;
    section_name: string;
    class_level: number;
    subject_id: string;
    subject_name: string;
    subject_code: string;
  }>;
}

export interface School {
  id: string;
  name: string;
  code: string;
  board: string;
  status: string;
  created_at: string;
}

export interface Section {
  id: string;
  school_id: string;
  class_level: number;
  section_name: string;
  class_teacher_id?: string | null;
  class_teacher_name?: string | null;
  created_at: string;
}

export interface Subject {
  id: string;
  school_id: string;
  name: string;
  code: string;
  created_at: string;
}

export interface StudentEnrollment {
  id: string;
  student_id: string;
  student_name: string;
  student_email?: string | null;
  roll_number?: string | null;
  section_id: string;
  section_name: string;
  class_level: number;
  status: EnrollmentStatus;
  requested_at: string;
  reviewed_at?: string | null;
}

export interface TeacherAssignment {
  id: string;
  teacher_id: string;
  teacher_name?: string | null;
  section_id: string;
  section_name?: string | null;
  class_level?: number | null;
  subject_id: string;
  subject_name?: string | null;
  created_at: string;
}
