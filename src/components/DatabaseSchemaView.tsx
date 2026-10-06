import React, { useState } from 'react';
import { 
  Database, 
  Code2, 
  Server, 
  Table, 
  Key, 
  Link2, 
  Play, 
  CheckCircle, 
  Copy, 
  Terminal,
  FileCode,
  Layers
} from 'lucide-react';
import { MasterCV, Job, Application } from '../types/job_agent';

interface DatabaseSchemaViewProps {
  cv: MasterCV;
  jobs: Job[];
  applications: Application[];
}

export const DatabaseSchemaView: React.FC<DatabaseSchemaViewProps> = ({
  cv,
  jobs,
  applications
}) => {
  const [activeSubTab, setActiveSubTab] = useState<'erd' | 'sql' | 'models' | 'apiTester'>('erd');
  const [selectedEndpoint, setSelectedEndpoint] = useState<string>('GET /api/v1/cv');
  const [apiResponse, setApiResponse] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // PostgreSQL Tables Meta
  const schemaTables = [
    {
      name: 'users',
      description: 'Candidate profile accounts & regional target',
      columns: [
        { name: 'id', type: 'VARCHAR(36)', isPk: true },
        { name: 'email', type: 'VARCHAR(255) UNIQUE', isPk: false },
        { name: 'full_name', type: 'VARCHAR(255)', isPk: false },
        { name: 'is_active', type: 'BOOLEAN', isPk: false },
        { name: 'target_city', type: 'VARCHAR(100) (Lahore)', isPk: false },
        { name: 'created_at', type: 'TIMESTAMP', isPk: false }
      ]
    },
    {
      name: 'master_cv',
      description: 'Primary factual CV record with audit versioning',
      columns: [
        { name: 'id', type: 'VARCHAR(36)', isPk: true },
        { name: 'user_id', type: 'VARCHAR(36) FK -> users.id', isPk: false, isFk: true },
        { name: 'full_name', type: 'VARCHAR(255)', isPk: false },
        { name: 'email', type: 'VARCHAR(255)', isPk: false },
        { name: 'phone', type: 'VARCHAR(50)', isPk: false },
        { name: 'location', type: 'VARCHAR(255)', isPk: false },
        { name: 'summary', type: 'TEXT', isPk: false },
        { name: 'github_url', type: 'VARCHAR(500)', isPk: false },
        { name: 'linkedin_url', type: 'VARCHAR(500)', isPk: false },
        { name: 'portfolio_url', type: 'VARCHAR(500)', isPk: false },
        { name: 'version', type: 'INTEGER', isPk: false },
        { name: 'raw_text', type: 'TEXT', isPk: false }
      ]
    },
    {
      name: 'skills',
      description: 'Granular verified technical skills catalog',
      columns: [
        { name: 'id', type: 'VARCHAR(36)', isPk: true },
        { name: 'master_cv_id', type: 'VARCHAR(36) FK -> master_cv.id', isPk: false, isFk: true },
        { name: 'name', type: 'VARCHAR(100)', isPk: false },
        { name: 'category', type: 'VARCHAR(50)', isPk: false },
        { name: 'proficiency', type: 'VARCHAR(50)', isPk: false },
        { name: 'years_of_experience', type: 'REAL', isPk: false }
      ]
    },
    {
      name: 'education',
      description: 'Degrees, Universities (FAST, PUCIT, ITU, etc.)',
      columns: [
        { name: 'id', type: 'VARCHAR(36)', isPk: true },
        { name: 'master_cv_id', type: 'VARCHAR(36) FK -> master_cv.id', isPk: false, isFk: true },
        { name: 'institution', type: 'VARCHAR(255)', isPk: false },
        { name: 'degree', type: 'VARCHAR(255)', isPk: false },
        { name: 'field_of_study', type: 'VARCHAR(255)', isPk: false },
        { name: 'grade_or_gpa', type: 'VARCHAR(50)', isPk: false },
        { name: 'start_date / end_date', type: 'VARCHAR(50)', isPk: false }
      ]
    },
    {
      name: 'experience',
      description: 'Internships and engineering employment records',
      columns: [
        { name: 'id', type: 'VARCHAR(36)', isPk: true },
        { name: 'master_cv_id', type: 'VARCHAR(36) FK -> master_cv.id', isPk: false, isFk: true },
        { name: 'company_name', type: 'VARCHAR(255)', isPk: false },
        { name: 'role_title', type: 'VARCHAR(255)', isPk: false },
        { name: 'employment_type', type: 'VARCHAR(50)', isPk: false },
        { name: 'location', type: 'VARCHAR(100)', isPk: false },
        { name: 'highlights', type: 'JSONB', isPk: false },
        { name: 'technologies_used', type: 'JSONB', isPk: false }
      ]
    },
    {
      name: 'projects',
      description: 'Verified software projects & GitHub repositories',
      columns: [
        { name: 'id', type: 'VARCHAR(36)', isPk: true },
        { name: 'master_cv_id', type: 'VARCHAR(36) FK -> master_cv.id', isPk: false, isFk: true },
        { name: 'title', type: 'VARCHAR(255)', isPk: false },
        { name: 'role', type: 'VARCHAR(100)', isPk: false },
        { name: 'technologies', type: 'JSONB', isPk: false },
        { name: 'repo_url', type: 'VARCHAR(500)', isPk: false },
        { name: 'live_url', type: 'VARCHAR(500)', isPk: false }
      ]
    },
    {
      name: 'certifications',
      description: 'Professional credentials & course completions',
      columns: [
        { name: 'id', type: 'VARCHAR(36)', isPk: true },
        { name: 'master_cv_id', type: 'VARCHAR(36) FK -> master_cv.id', isPk: false, isFk: true },
        { name: 'name', type: 'VARCHAR(255)', isPk: false },
        { name: 'issuing_organization', type: 'VARCHAR(255)', isPk: false },
        { name: 'credential_url', type: 'VARCHAR(500)', isPk: false }
      ]
    },
    {
      name: 'jobs',
      description: 'Phase 2: Collected Lahore software house job opportunities',
      columns: [
        { name: 'id', type: 'VARCHAR(36)', isPk: true },
        { name: 'company', type: 'VARCHAR(255)', isPk: false },
        { name: 'job_title', type: 'VARCHAR(255)', isPk: false },
        { name: 'location', type: 'VARCHAR(255) (Lahore)', isPk: false },
        { name: 'source_url', type: 'VARCHAR(1000)', isPk: false },
        { name: 'raw_description', type: 'TEXT (Full JD)', isPk: false },
        { name: 'responsibilities', type: 'JSONB (List)', isPk: false },
        { name: 'required_skills', type: 'JSONB', isPk: false },
        { name: 'duplicate_status', type: 'VARCHAR(50) (unique/duplicate)', isPk: false },
        { name: 'dedup_hash', type: 'VARCHAR(64) (SHA-256)', isPk: false },
        { name: 'posting_date', type: 'VARCHAR(50)', isPk: false },
        { name: 'deadline', type: 'VARCHAR(50)', isPk: false },
        { name: 'status', type: 'VARCHAR(50) (discovered/saved/applied)', isPk: false }
      ]
    },
    {
      name: 'job_discovery_runs',
      description: 'Phase 2: Audit metrics for automated discovery crawls',
      columns: [
        { name: 'id', type: 'VARCHAR(36)', isPk: true },
        { name: 'triggered_at', type: 'TIMESTAMP', isPk: false },
        { name: 'completed_at', type: 'TIMESTAMP', isPk: false },
        { name: 'status', type: 'VARCHAR(50) (completed/failed)', isPk: false },
        { name: 'sources_checked', type: 'JSONB', isPk: false },
        { name: 'keywords_used', type: 'JSONB', isPk: false },
        { name: 'total_discovered', type: 'INTEGER', isPk: false },
        { name: 'new_jobs_added', type: 'INTEGER', isPk: false },
        { name: 'duplicates_skipped', type: 'INTEGER', isPk: false },
        { name: 'rejected_non_lahore', type: 'INTEGER', isPk: false }
      ]
    },
    {
      name: 'applications',
      description: 'Application pipeline tracker (draft to offer)',
      columns: [
        { name: 'id', type: 'VARCHAR(36)', isPk: true },
        { name: 'user_id', type: 'VARCHAR(36) FK -> users.id', isPk: false, isFk: true },
        { name: 'job_id', type: 'VARCHAR(36) FK -> jobs.id', isPk: false, isFk: true },
        { name: 'master_cv_id', type: 'VARCHAR(36) FK -> master_cv.id', isPk: false, isFk: true },
        { name: 'status', type: 'VARCHAR(50)', isPk: false },
        { name: 'applied_at', type: 'TIMESTAMP', isPk: false },
        { name: 'interview_date', type: 'TIMESTAMP', isPk: false }
      ]
    },
    {
      name: 'tailored_cvs',
      description: 'Job-specific customized CVs (Reserved for Phase 3)',
      columns: [
        { name: 'id', type: 'VARCHAR(36)', isPk: true },
        { name: 'master_cv_id', type: 'VARCHAR(36) FK -> master_cv.id', isPk: false, isFk: true },
        { name: 'job_id', type: 'VARCHAR(36) FK -> jobs.id', isPk: false, isFk: true },
        { name: 'tailored_content', type: 'JSONB', isPk: false },
        { name: 'match_score', type: 'REAL', isPk: false }
      ]
    }
  ];

  const handleRunMockEndpoint = () => {
    if (selectedEndpoint === 'GET /api/v1/cv') {
      setApiResponse(JSON.stringify(cv, null, 2));
    } else if (selectedEndpoint === 'GET /api/v1/jobs') {
      setApiResponse(JSON.stringify(jobs, null, 2));
    } else if (selectedEndpoint === 'POST /api/v1/jobs/discover') {
      setApiResponse(
        JSON.stringify(
          {
            id: `run-${Date.now()}`,
            triggered_at: new Date(Date.now() - 3000).toISOString(),
            completed_at: new Date().toISOString(),
            status: "completed",
            sources_checked: ["systems_limited", "arbisoft", "devsinc", "tintash", "netsol", "rozee_pk"],
            keywords_used: ["Python Developer", "Software Engineer", "Junior Developer"],
            total_discovered: 8,
            new_jobs_added: 3,
            duplicates_skipped: 2,
            rejected_non_lahore: 2,
            rejected_non_entry: 1
          },
          null,
          2
        )
      );
    } else if (selectedEndpoint === 'GET /api/v1/jobs/discovery-runs') {
      setApiResponse(
        JSON.stringify(
          [
            {
              id: "run-001",
              triggered_at: new Date(Date.now() - 86400000).toISOString(),
              completed_at: new Date(Date.now() - 86400000 + 20000).toISOString(),
              status: "completed",
              sources_checked: ["systems_limited", "arbisoft", "devsinc"],
              total_discovered: 12,
              new_jobs_added: 7,
              duplicates_skipped: 2,
              rejected_non_lahore: 2,
              rejected_non_entry: 1
            }
          ],
          null,
          2
        )
      );
    } else if (selectedEndpoint === 'GET /api/v1/applications') {
      setApiResponse(JSON.stringify(applications, null, 2));
    } else if (selectedEndpoint === 'GET /api/v1/skills') {
      setApiResponse(JSON.stringify(cv.skills, null, 2));
    } else if (selectedEndpoint === 'GET /api/v1/health') {
      setApiResponse(
        JSON.stringify(
          {
            status: 'online',
            app_name: 'Lahore AI Job Application Agent',
            version: '2.0.0-phase2',
            database_connected: true,
            target_city: 'Lahore',
            counts: {
              users: 1,
              master_cvs: 1,
              skills: cv.skills.length,
              jobs: jobs.length,
              applications: applications.length
            }
          },
          null,
          2
        )
      );
    }
  };

  const copyCode = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
                <Database className="w-5 h-5" />
              </span>
              <h2 className="text-xl font-bold text-white tracking-tight">PostgreSQL & FastAPI Architecture</h2>
              <span className="text-xs bg-emerald-950/60 text-emerald-400 border border-emerald-800/80 px-2.5 py-0.5 rounded-full font-medium">
                10 Schema Tables • REST APIs
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
              Inspect the clean relational schema, SQLAlchemy 2.0 ORM mappings, raw PostgreSQL DDL, and test live FastAPI endpoints.
            </p>
          </div>

          {/* Sub tabs */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 self-start md:self-auto text-xs">
            <button
              onClick={() => setActiveSubTab('erd')}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${
                activeSubTab === 'erd'
                  ? 'bg-emerald-500 text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Schema Diagram
            </button>
            <button
              onClick={() => setActiveSubTab('sql')}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${
                activeSubTab === 'sql'
                  ? 'bg-emerald-500 text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              PostgreSQL DDL
            </button>
            <button
              onClick={() => setActiveSubTab('models')}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${
                activeSubTab === 'models'
                  ? 'bg-emerald-500 text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              SQLAlchemy Models
            </button>
            <button
              onClick={() => setActiveSubTab('apiTester')}
              className={`px-3 py-1.5 rounded-lg font-medium transition ${
                activeSubTab === 'apiTester'
                  ? 'bg-emerald-500 text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              API Swagger Tester
            </button>
          </div>
        </div>
      </div>

      {/* Subtab 1: ERD Grid */}
      {activeSubTab === 'erd' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {schemaTables.map((tbl, i) => (
            <div
              key={tbl.name}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-lg flex flex-col justify-between space-y-3"
            >
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <Table className="w-4 h-4 text-emerald-400" />
                    <span className="font-mono font-bold text-sm text-white">{tbl.name}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 uppercase font-semibold">Table #{i + 1}</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1.5 italic">{tbl.description}</p>

                {/* Column details */}
                <div className="space-y-1 pt-3">
                  {tbl.columns.map(col => (
                    <div
                      key={col.name}
                      className="flex items-center justify-between text-[11px] font-mono py-1 px-1.5 rounded-md hover:bg-slate-950/60"
                    >
                      <div className="flex items-center gap-1.5">
                        {col.isPk ? (
                          <span title="Primary Key"><Key className="w-3 h-3 text-amber-400" /></span>
                        ) : col.isFk ? (
                          <span title="Foreign Key"><Link2 className="w-3 h-3 text-sky-400" /></span>
                        ) : (
                          <span className="w-3 h-3 inline-block" />
                        )}
                        <span className={col.isPk ? 'text-amber-300 font-semibold' : 'text-slate-300'}>
                          {col.name}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-500">{col.type}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Subtab 2: Raw PostgreSQL DDL */}
      {activeSubTab === 'sql' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
              <FileCode className="w-4 h-4 text-emerald-400" />
              <span>backend/init_db.sql</span>
            </div>
            <button
              onClick={() => copyCode(`-- Lahore AI Job Application Agent Schema\nCREATE TABLE users (...);`)}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700"
            >
              {copied ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy SQL'}</span>
            </button>
          </div>
          <pre className="p-4 bg-slate-950 rounded-xl font-mono text-xs text-slate-300 overflow-x-auto border border-slate-800/80 leading-relaxed max-h-[550px]">
{`-- ==============================================================
-- Lahore AI Job Application Agent - Phase 1 PostgreSQL Schema DDL
-- Database: job_agent_db
-- ==============================================================

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    target_city VARCHAR(100) DEFAULT 'Lahore',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS master_cv (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255) DEFAULT 'Lahore, Pakistan',
    summary TEXT,
    github_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    version INTEGER DEFAULT 1,
    is_primary BOOLEAN DEFAULT TRUE,
    raw_text TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) DEFAULT 'Technical',
    proficiency VARCHAR(50) DEFAULT 'Intermediate',
    years_of_experience REAL
);

CREATE TABLE IF NOT EXISTS education (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    institution VARCHAR(255) NOT NULL,
    degree VARCHAR(255) NOT NULL,
    field_of_study VARCHAR(255),
    grade_or_gpa VARCHAR(50),
    start_date VARCHAR(50),
    end_date VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS experience (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    role_title VARCHAR(255) NOT NULL,
    employment_type VARCHAR(50) DEFAULT 'Full-time',
    location VARCHAR(100) DEFAULT 'Lahore, Pakistan',
    highlights JSONB DEFAULT '[]',
    technologies_used JSONB DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    role VARCHAR(100),
    technologies JSONB DEFAULT '[]',
    repo_url VARCHAR(500),
    live_url VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS certifications (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255) NOT NULL,
    credential_url VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(36) PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    location VARCHAR(255) DEFAULT 'Lahore, Pakistan',
    job_url VARCHAR(1000),
    description TEXT NOT NULL,
    required_skills JSONB DEFAULT '[]',
    preferred_skills JSONB DEFAULT '[]',
    experience_requirement VARCHAR(100) DEFAULT 'Entry-level (0-1 years)',
    education_requirement VARCHAR(255) DEFAULT 'BS Computer Science',
    job_type VARCHAR(50) DEFAULT 'Full-time',
    salary VARCHAR(100),
    source VARCHAR(100) DEFAULT 'Manual',
    status VARCHAR(50) DEFAULT 'saved'
);

CREATE TABLE IF NOT EXISTS applications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id VARCHAR(36) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'draft',
    applied_at TIMESTAMP WITHOUT TIME ZONE,
    interview_date TIMESTAMP WITHOUT TIME ZONE,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS tailored_cvs (
    id VARCHAR(36) PRIMARY KEY,
    master_cv_id VARCHAR(36) NOT NULL REFERENCES master_cv(id) ON DELETE CASCADE,
    job_id VARCHAR(36) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    tailored_content JSONB DEFAULT '{}',
    match_score REAL,
    version INTEGER DEFAULT 1
);`}
          </pre>
        </div>
      )}

      {/* Subtab 3: SQLAlchemy Models */}
      {activeSubTab === 'models' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
              <Code2 className="w-4 h-4 text-emerald-400" />
              <span>backend/app/models/__init__.py</span>
            </div>
          </div>
          <pre className="p-4 bg-slate-950 rounded-xl font-mono text-xs text-slate-300 overflow-x-auto border border-slate-800/80 leading-relaxed max-h-[550px]">
{`from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    target_city = Column(String(100), default="Lahore")
    master_cvs = relationship("MasterCV", back_populates="user")
    applications = relationship("Application", back_populates="user")

class MasterCV(Base):
    __tablename__ = "master_cv"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    location = Column(String(255), default="Lahore, Pakistan")
    summary = Column(Text)
    github_url = Column(String(500))
    linkedin_url = Column(String(500))
    version = Column(Integer, default=1)
    
    skills = relationship("Skill", back_populates="master_cv", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="master_cv", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="master_cv", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="master_cv", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String(36), primary_key=True)
    company = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    location = Column(String(255), default="Lahore, Pakistan")
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    salary = Column(String(100))
    source = Column(String(100), default="Manual")
    status = Column(String(50), default="saved")

class Application(Base):
    __tablename__ = "applications"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    job_id = Column(String(36), ForeignKey("jobs.id"))
    master_cv_id = Column(String(36), ForeignKey("master_cv.id"))
    status = Column(String(50), default="draft")
    notes = Column(Text)`}
          </pre>
        </div>
      )}

      {/* Subtab 4: API Swagger Tester */}
      {activeSubTab === 'apiTester' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Server className="w-4 h-4 text-emerald-400" />
                FastAPI Interactive Endpoint Tester
              </h3>
              <p className="text-xs text-slate-400">Select an API route and test request execution against active state.</p>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={selectedEndpoint}
                onChange={e => {
                  setSelectedEndpoint(e.target.value);
                  setApiResponse(null);
                }}
                className="bg-slate-950 border border-slate-700 text-xs text-slate-200 px-3 py-2 rounded-xl focus:outline-none focus:border-emerald-500 font-mono"
              >
                <option value="GET /api/v1/cv">GET /api/v1/cv (Master CV)</option>
                <option value="GET /api/v1/skills">GET /api/v1/skills (Skills Taxonomy)</option>
                <option value="GET /api/v1/jobs">GET /api/v1/jobs (Lahore Jobs)</option>
                <option value="POST /api/v1/jobs/discover">POST /api/v1/jobs/discover (Run Discovery)</option>
                <option value="GET /api/v1/jobs/discovery-runs">GET /api/v1/jobs/discovery-runs (Run Metrics)</option>
                <option value="GET /api/v1/applications">GET /api/v1/applications (Pipelines)</option>
                <option value="GET /api/v1/health">GET /api/v1/health (Diagnostics)</option>
              </select>

              <button
                onClick={handleRunMockEndpoint}
                className="flex items-center gap-1.5 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs rounded-xl shadow transition"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Execute</span>
              </button>
            </div>
          </div>

          {/* Endpoint Details */}
          <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2">
              <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded font-bold">
                {selectedEndpoint.split(' ')[0]}
              </span>
              <span className="text-white">{selectedEndpoint.split(' ')[1]}</span>
            </div>
            <span className="text-slate-500">200 OK • Content-Type: application/json</span>
          </div>

          {/* Output Display */}
          {apiResponse ? (
            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Response Payload (JSON)
              </span>
              <pre className="p-4 bg-slate-950 rounded-xl font-mono text-xs text-emerald-300 overflow-x-auto border border-slate-800/80 leading-relaxed max-h-[400px]">
                {apiResponse}
              </pre>
            </div>
          ) : (
            <div className="text-center py-12 text-xs text-slate-500 bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
              Click <strong className="text-emerald-400">Execute</strong> to inspect endpoint output.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
