export interface Skill {
  id: string;
  name: string;
  category: 'Languages' | 'Frameworks' | 'Databases' | 'Tools & DevOps' | 'Core Concepts' | 'Soft Skills' | 'Technical';
  proficiency: 'Beginner' | 'Intermediate' | 'Expert';
  years_of_experience?: number;
}

export interface Education {
  id: string;
  institution: string;
  degree: string;
  field_of_study?: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  grade_or_gpa?: string;
  location?: string;
  description?: string;
}

export interface Experience {
  id: string;
  company_name: string;
  role_title: string;
  employment_type: 'Full-time' | 'Internship' | 'Contract' | 'Freelance';
  location: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  description?: string;
  highlights: string[];
  technologies_used: string[];
}

export interface Project {
  id: string;
  title: string;
  description?: string;
  role?: string;
  technologies: string[];
  repo_url?: string;
  live_url?: string;
  start_date?: string;
  end_date?: string;
  highlights: string[];
}

export interface Certification {
  id: string;
  name: string;
  issuing_organization: string;
  issue_date?: string;
  expiration_date?: string;
  credential_id?: string;
  credential_url?: string;
}

export interface MasterCV {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  phone?: string;
  location: string;
  summary?: string;
  github_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  website_url?: string;
  version: number;
  is_primary: boolean;
  source_filename?: string;
  raw_text?: string;
  created_at: string;
  updated_at: string;
  skills: Skill[];
  education: Education[];
  experience: Experience[];
  projects: Project[];
  certifications: Certification[];
}

export type JobStatus = 'discovered' | 'saved' | 'ignored' | 'applied' | 'archived';

export interface Job {
  id: string;
  company: string;
  job_title: string;
  location: string;
  job_url?: string;
  source_url?: string;
  description: string;
  raw_description?: string;
  responsibilities?: string[];
  required_skills: string[];
  preferred_skills: string[];
  experience_requirement: string;
  education_requirement: string;
  job_type: 'Full-time' | 'Internship' | 'Hybrid' | 'Remote';
  salary?: string;
  source: string;
  status: JobStatus;
  job_status?: JobStatus;
  discovered_at?: string;
  posting_date?: string;
  deadline?: string;
  duplicate_status?: 'unique' | 'duplicate';
  canonical_job_id?: string;
  dedup_hash?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface JobDiscoveryRun {
  id: string;
  triggered_at: string;
  completed_at?: string;
  status: 'running' | 'completed' | 'failed';
  sources_checked: string[];
  keywords_used: string[];
  total_discovered: number;
  new_jobs_added: number;
  duplicates_skipped: number;
  rejected_non_lahore: number;
  rejected_non_entry: number;
  error_message?: string;
}

export interface JobDiscoverySourceInfo {
  id: string;
  name: string;
  type: 'company_careers' | 'job_board' | 'search_engine';
  is_active: boolean;
  base_url: string;
  description: string;
}

export type ApplicationStatus = 
  | 'DRAFT' 
  | 'REVIEW_REQUIRED' 
  | 'READY_FOR_SUBMISSION' 
  | 'SUBMITTED' 
  | 'REJECTED' 
  | 'WITHDRAWN' 
  | 'INTERVIEW' 
  | 'OFFER'
  | 'draft'
  | 'ready'
  | 'applied'
  | 'screening'
  | 'interview'
  | 'offered';

export interface ApplicationQuestionAnswer {
  question_key: string;
  question_text: string;
  answer_text?: string | null;
  status: 'AUTO_ANSWERED' | 'REQUIRES_USER_INPUT' | 'USER_EDITED';
  source_evidence?: string;
}

export interface Application {
  id: string;
  user_id: string;
  job_id: string;
  master_cv_id: string;
  tailored_cv_id?: string;
  match_result_id?: string;
  status: ApplicationStatus;
  readiness_status?: 'READY' | 'REVIEW_REQUIRED' | string;
  cover_letter?: string;
  candidate_profile?: Record<string, any>;
  application_fields?: Record<string, any>;
  application_answers?: ApplicationQuestionAnswer[];
  application_package?: Record<string, any>;
  user_edits?: Record<string, any>;
  validation_errors?: string[];
  evidence_map?: Array<Record<string, any>>;
  applied_at?: string;
  interview_date?: string;
  review_timestamp?: string;
  approval_timestamp?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface JobMatchEvaluation {
  job_id: string;
  job_title: string;
  company: string;
  location: string;
  match_score: number;
  match_score_decimal: number;
  recommendation: 'STRONG MATCH' | 'GOOD MATCH' | 'MODERATE MATCH' | 'WEAK MATCH' | string;
  required_skills: string[];
  relevant_experience: string[];
  partial: string[];
  missing: string[];
  formatted_report: string;
}

