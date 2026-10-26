export type Role = 'student' | 'admin';

export type Gender = 'male' | 'female' | 'other';

export type Category = 'GEN' | 'OBC' | 'SC' | 'ST' | 'EWS';

export type QualificationLevel = '10th' | '12th' | 'Graduate' | 'Post Graduate' | 'Doctorate';

export type QualificationStatus = 'completed' | 'appearing';

export type EligibilityStatus = 'eligible' | 'review_required' | 'not_eligible';

export interface StudentQualification {
  id?: number;
  level: QualificationLevel;
  degree?: string;
  status: QualificationStatus;
  passing_year?: number | null;
  percentage?: number | string | null;
}

export interface StudentProfile {
  id: number;
  date_of_birth: string | null;
  gender: Gender;
  category: Category;
  domicile_state: string;
  qualifications: StudentQualification[];
  additional_certifications?: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  student_profile?: StudentProfile;
  created_at?: string;
}

export interface EligibilityRule {
  id: number;
  min_qualification_level: QualificationLevel;
  allowed_status: 'completed_only' | 'appearing_allowed';
  age_relaxations: Record<string, number>;
  domicile_requirement: string;
  min_percentage?: number | string | null;
  conditions_summary?: string;
  additional_certification_requirement?: string;
}

export interface EligibilityDetails {
  calculated_age: number | null;
  age_relaxation_applied: number;
  effective_max_age: number;
  min_age: number;
  min_qualification_required: string;
  is_expired: boolean;
}

export interface EligibilityResult {
  status: EligibilityStatus;
  reasons: string[];
  warnings: string[];
  failed_criteria: string[];
  missing_info: string[];
  details: EligibilityDetails;
}

export interface Job {
  id: number;
  title: string;
  organization: string;
  advertisement_number?: string;
  recruitment_year?: number;
  category: string;
  application_start_date: string;
  application_deadline: string;
  age_cutoff_date: string;
  min_age: number;
  max_age: number;
  total_vacancies?: number | null;
  application_fee_details?: Record<string, any>;
  vacancy_details?: any[];
  selection_process?: string;
  original_url: string;
  source_name: string;
  source_type?: 'manual' | 'url' | 'pdf';
  uploaded_pdf?: string | null;
  description: string;
  status: 'draft' | 'processing' | 'pending_review' | 'approved' | 'rejected' | 'failed';
  is_published: boolean;
  is_expired: boolean;
  ai_extraction_metadata?: {
    conflicts?: string[];
    warnings?: string[];
    confidence_score?: number;
    detected_links?: Record<string, string>;
    extraction_engine?: string;
    [key: string]: any;
  };
  ai_confidence_score?: number | null;
  review_notes?: string;
  created_at: string;
  updated_at?: string;
  rule?: EligibilityRule;
  eligibility?: EligibilityResult;
}

export interface JobMatchesSummary {
  total_jobs: number;
  eligible_count: number;
  review_required_count: number;
  not_eligible_count: number;
  selected_filter: string;
}

export interface JobMatchesResponse {
  summary: JobMatchesSummary;
  has_profile: boolean;
  student_category?: string;
  student_domicile?: string;
  jobs: Job[];
}
