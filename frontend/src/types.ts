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

// --- Phase 2: Questions, Studio, Verification ---
export type QuestionOrigin = 'SOURCE_COPY' | 'AI_SIMILAR' | 'AI_HIGHER' | 'TEACHER_AUTHORED';
export type VerificationStatus = 'UNVERIFIED' | 'NEEDS_REVIEW' | 'APPROVED' | 'REJECTED';

export interface VerificationRun {
  run_no: number;
  solver_model: string;
  answer: string;
  steps?: string | null;
  agree: boolean;
  diff_notes?: string | null;
}

export interface QuestionVersionData {
  id: string;
  version: number;
  body: string;
  options?: string[] | null;
  answer: string;
  solution?: string | null;
  verification_status: VerificationStatus;
  meta: {
    subject?: string;
    class_level?: number;
    chapter?: string;
    topic?: string;
    marks?: number;
    difficulty?: string;
    question_type?: string;
    [key: string]: any;
  };
  verification_runs: VerificationRun[];
}

export interface QuestionItem {
  id: string;
  short_id: string;
  long_id: string;
  origin: QuestionOrigin;
  source_ref?: string | null;
  owner_teacher_id: string;
  current_version: number;
  all_versions?: Array<{
    version: number;
    verification_status: VerificationStatus;
    created_at: string;
  }>;
  version_data: QuestionVersionData;
  created_at: string;
}

export interface SubjectQuestionType {
  id: string;
  label: string;
  default_marks: number;
  tolerance?: number;
  options_count?: number;
}

export interface SubjectTopic {
  name: string;
  code: string;
}

export interface SubjectChapter {
  name: string;
  code: string;
  topics: SubjectTopic[];
}

export interface SubjectPack {
  subject: string;
  code: string;
  version: string;
  boards: string[];
  classes: number[];
  question_types: SubjectQuestionType[];
  chapters: SubjectChapter[];
}

export interface StudioGenerateResponse {
  subject: string;
  class_level: number;
  chapter: string;
  topic: string;
  question_type: string;
  difficulty: string;
  marks: number;
  mode: string;
  source_ref?: string | null;
  draft: {
    body: string;
    options?: string[] | null;
    answer: string;
    solution?: string | null;
  };
  verification: {
    agree: boolean;
    status: VerificationStatus;
    diff_notes?: string | null;
    solver1: {
      model: string;
      answer: string;
      steps: string;
    };
    solver2: {
      model: string;
      answer: string;
      steps: string;
      tool_meta?: any;
    };
  };
}

export interface InterpretSetResponse {
  interpretation_summary: string;
  detected_subject: string;
  detected_class: number;
  questions_count: number;
  questions: Array<{
    body: string;
    options?: string[] | null;
    answer: string;
    solution?: string | null;
    question_type: string;
    chapter?: string | null;
    topic?: string | null;
    difficulty: string;
    marks: number;
    [key: string]: any;
  }>;
}

