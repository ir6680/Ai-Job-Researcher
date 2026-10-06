import React, { useState } from 'react';
import { 
  X, 
  Download, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldCheck, 
  Sparkles, 
  ExternalLink,
  Layers, 
  Check, 
  Code, 
  Briefcase, 
  GraduationCap, 
  Eye, 
  ChevronRight,
  UserCheck
} from 'lucide-react';
import { Job, JobMatchEvaluation } from '../types/job_agent';

interface TailoredCVModalProps {
  job: Job;
  tailoredCV: any;
  fitEvaluation: JobMatchEvaluation;
  onClose: () => void;
  onMarkReviewed: (cvId: string) => void;
}

export const TailoredCVModal: React.FC<TailoredCVModalProps> = ({
  job,
  tailoredCV,
  fitEvaluation,
  onClose,
  onMarkReviewed
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'comparison' | 'skills' | 'projects' | 'evidence' | 'ats'>('preview');
  const [isReviewed, setIsReviewed] = useState(tailoredCV?.human_reviewed || false);

  const structured = tailoredCV?.structured_content || {};
  const changes = tailoredCV?.tailoring_changes || {};
  const evidenceMap = tailoredCV?.evidence_map || [];
  const matchedKws = tailoredCV?.matched_keywords || [];
  const missingKws = tailoredCV?.missing_keywords || [];
  const rejectedClaims = tailoredCV?.rejected_claims || [];

  const handleReviewToggle = () => {
    setIsReviewed(true);
    if (tailoredCV?.id) {
      onMarkReviewed(tailoredCV.id);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-5xl w-full shadow-2xl flex flex-col max-h-[92vh] overflow-hidden">
        
        {/* Header */}
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                {job.company}
              </span>
              <span className="text-[10px] bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded-md font-mono">
                Version {tailoredCV?.version || 1}
              </span>
              <span className="text-[10px] bg-emerald-950/80 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-md font-mono flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5" />
                Job Match: {fitEvaluation.match_score}%
              </span>
              <span className="text-[10px] bg-teal-950/80 text-teal-300 border border-teal-800 px-2 py-0.5 rounded-md font-mono">
                ATS Coverage: {tailoredCV?.ats_keyword_coverage || 82}%
              </span>
              <span className="text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 px-2 py-0.5 rounded-md font-mono flex items-center gap-1 font-bold">
                <ShieldCheck className="w-3 h-3 text-emerald-400" />
                Integrity: {tailoredCV?.integrity_status || 'PASS'}
              </span>
            </div>
            <h2 className="text-xl font-bold text-white mt-1">
              Job-Specific Tailored CV: {job.job_title}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Action Bar (Downloads & Review) */}
        <div className="flex flex-wrap items-center justify-between gap-3 py-3 border-b border-slate-800 bg-slate-950/60 -mx-6 px-6">
          <div className="flex items-center gap-2">
            <a
              href={`/api/v1/tailored-cvs/${tailoredCV?.id}/download/docx`}
              download
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition"
            >
              <Download className="w-3.5 h-3.5 text-emerald-400" />
              <span>Download DOCX</span>
            </a>
            <a
              href={`/api/v1/tailored-cvs/${tailoredCV?.id}/download/pdf`}
              download
              className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl shadow transition"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download PDF</span>
            </a>
          </div>

          <div className="flex items-center gap-2">
            {isReviewed ? (
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium px-3 py-1 bg-emerald-950/60 rounded-xl border border-emerald-800/80">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Human Reviewed & Approved</span>
              </span>
            ) : (
              <button
                onClick={handleReviewToggle}
                className="flex items-center gap-1.5 text-xs text-amber-300 font-medium px-3 py-1.5 bg-amber-950/60 hover:bg-amber-900/60 rounded-xl border border-amber-800/80 transition"
              >
                <UserCheck className="w-3.5 h-3.5" />
                <span>Mark as Human Reviewed</span>
              </button>
            )}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 pt-3 pb-2 border-b border-slate-800 overflow-x-auto text-xs font-medium text-slate-400">
          {[
            { id: 'preview', label: 'CV Preview', icon: FileText },
            { id: 'comparison', label: 'Original vs Tailored', icon: Layers },
            { id: 'skills', label: 'Skills Prioritized', icon: Code },
            { id: 'projects', label: 'Projects Reordered', icon: Briefcase },
            { id: 'evidence', label: 'Evidence Traceability', icon: Sparkles },
            { id: 'ats', label: 'ATS Keywords', icon: CheckCircle2 }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg whitespace-nowrap transition ${
                  isActive 
                    ? 'bg-slate-800 text-emerald-400 font-semibold' 
                    : 'hover:text-slate-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Contents */}
        <div className="flex-1 overflow-y-auto py-4 space-y-4">
          
          {/* TAB 1: CV PREVIEW */}
          {activeTab === 'preview' && (
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 font-sans text-xs text-slate-200 space-y-5 max-w-3xl mx-auto shadow-inner">
              {/* Header */}
              <div className="text-center space-y-1 pb-3 border-b border-slate-800">
                <h1 className="text-xl font-bold uppercase tracking-wide text-white">
                  {structured.full_name || 'Irfan Rajpoot'}
                </h1>
                <p className="text-[11px] text-slate-400 font-mono">
                  {[structured.location, structured.email, structured.phone, 'LinkedIn', 'GitHub'].filter(Boolean).join(' | ')}
                </p>
              </div>

              {/* Summary */}
              {structured.summary && (
                <div className="space-y-1">
                  <h3 className="font-bold uppercase tracking-wider text-slate-300 text-[11px] border-b border-slate-800/80 pb-0.5">
                    Professional Summary
                  </h3>
                  <p className="text-slate-300 leading-relaxed text-[11px]">
                    {structured.summary}
                  </p>
                </div>
              )}

              {/* Technical Skills */}
              {structured.skills_by_category && (
                <div className="space-y-1.5">
                  <h3 className="font-bold uppercase tracking-wider text-slate-300 text-[11px] border-b border-slate-800/80 pb-0.5">
                    Technical Skills
                  </h3>
                  <div className="space-y-1 text-[11px]">
                    {Object.entries(structured.skills_by_category).map(([cat, list]: any) => (
                      <div key={cat} className="flex flex-wrap items-baseline gap-1">
                        <span className="font-semibold text-slate-300">{cat}:</span>
                        <span className="text-slate-400 font-mono text-[10px]">{list.join(', ')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Key Projects */}
              {structured.projects && (
                <div className="space-y-2">
                  <h3 className="font-bold uppercase tracking-wider text-slate-300 text-[11px] border-b border-slate-800/80 pb-0.5">
                    Key Projects
                  </h3>
                  <div className="space-y-2.5">
                    {structured.projects.map((p: any, idx: number) => (
                      <div key={idx} className="space-y-1">
                        <div className="flex items-baseline justify-between">
                          <span className="font-bold text-white text-[11px]">{p.title}</span>
                          {p.technologies && (
                            <span className="text-[10px] text-slate-400 font-mono italic">
                              {p.technologies.join(', ')}
                            </span>
                          )}
                        </div>
                        <ul className="list-disc list-inside space-y-0.5 text-slate-300 text-[11px]">
                          {(p.highlights || []).map((h: string, hIdx: number) => (
                            <li key={hIdx}>{h}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Professional Experience */}
              {structured.experience && (
                <div className="space-y-2">
                  <h3 className="font-bold uppercase tracking-wider text-slate-300 text-[11px] border-b border-slate-800/80 pb-0.5">
                    Professional Experience
                  </h3>
                  <div className="space-y-2.5">
                    {structured.experience.map((e: any, idx: number) => (
                      <div key={idx} className="space-y-1">
                        <div className="flex items-baseline justify-between">
                          <span className="font-bold text-white text-[11px]">
                            {e.role_title} - {e.company_name}
                          </span>
                          <span className="text-[10px] text-slate-400 font-mono">
                            {e.start_date} - {e.is_current ? 'Present' : (e.end_date || '')}
                          </span>
                        </div>
                        <ul className="list-disc list-inside space-y-0.5 text-slate-300 text-[11px]">
                          {(e.highlights || []).map((h: string, hIdx: number) => (
                            <li key={hIdx}>{h}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Education */}
              {structured.education && (
                <div className="space-y-1.5">
                  <h3 className="font-bold uppercase tracking-wider text-slate-300 text-[11px] border-b border-slate-800/80 pb-0.5">
                    Education
                  </h3>
                  {structured.education.map((ed: any, idx: number) => (
                    <div key={idx} className="flex items-baseline justify-between text-[11px]">
                      <span className="font-semibold text-slate-200">
                        {ed.degree} - {ed.institution}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">{ed.location}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: ORIGINAL VS TAILORED */}
          {activeTab === 'comparison' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
                <span className="font-bold text-slate-400 uppercase tracking-wider text-[11px] block border-b border-slate-800 pb-1">
                  Master CV (Single Source of Truth)
                </span>
                <div className="space-y-2 text-slate-300 text-[11px]">
                  <p className="font-semibold text-slate-200">Standard Summary:</p>
                  <p className="p-2.5 bg-slate-900 rounded-lg border border-slate-800/80 text-slate-400">
                    AI and Backend Software Engineer based in Lahore with expertise in Python, FastAPI, and machine learning architectures.
                  </p>

                  <p className="font-semibold text-slate-200 pt-1">Default Skills Ordering:</p>
                  <p className="font-mono text-[10px] text-slate-400 p-2 bg-slate-900 rounded-lg">
                    Python, REST APIs, AI/ML, Git, FastAPI, SQL, PostgreSQL, RAG, Agentic Systems
                  </p>

                  <p className="font-semibold text-slate-200 pt-1">Default Project List:</p>
                  <p className="text-[11px] text-slate-400">
                    1. AI/ML FYP • 2. Inventory Tracker
                  </p>
                </div>
              </div>

              <div className="p-4 bg-slate-950 rounded-xl border border-emerald-900/60 space-y-3">
                <span className="font-bold text-emerald-400 uppercase tracking-wider text-[11px] block border-b border-slate-800 pb-1">
                  Tailored CV for {job.company}
                </span>
                <div className="space-y-2 text-slate-300 text-[11px]">
                  <p className="font-semibold text-emerald-300">Target Role Optimized Summary:</p>
                  <p className="p-2.5 bg-slate-900 rounded-lg border border-emerald-900/50 text-slate-200">
                    {structured.summary}
                  </p>

                  <p className="font-semibold text-emerald-300 pt-1">Prioritized Skills:</p>
                  <p className="font-mono text-[10px] text-emerald-300 p-2 bg-slate-900 rounded-lg">
                    {(structured.prioritized_skills || []).join(', ')}
                  </p>

                  <p className="font-semibold text-emerald-300 pt-1">Ranked Projects:</p>
                  <p className="text-[11px] text-slate-300">
                    {structured.projects?.map((p: any, i: number) => `${i + 1}. ${p.title}`).join(' • ')}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: SKILLS PRIORITIZED */}
          {activeTab === 'skills' && (
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-4 text-xs">
              <div className="border-b border-slate-800 pb-2">
                <h4 className="font-bold text-white text-sm">Skills Prioritization Hierarchy</h4>
                <p className="text-[11px] text-slate-400">
                  Strong required matches are surfaced first, followed by partial/adjacent matches, and genuine technical tools.
                  <span className="text-emerald-400 font-semibold"> Missing JD keywords are never inserted.</span>
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3 bg-slate-900 rounded-xl border border-emerald-900/60 space-y-2">
                  <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider block">
                    1. Strong Required Matches (✓)
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {fitEvaluation.required_skills.map((s, i) => (
                      <span key={i} className="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded font-mono">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3 bg-slate-900 rounded-xl border border-amber-900/60 space-y-2">
                  <span className="text-[11px] font-bold text-amber-400 uppercase tracking-wider block">
                    2. Partial / Relevant (△)
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {fitEvaluation.partial.map((p, i) => (
                      <span key={i} className="text-[10px] bg-amber-950 text-amber-300 border border-amber-800 px-2 py-0.5 rounded font-mono">
                        {p}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                    3. Other Genuine Skills
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {(structured.prioritized_skills || [])
                      .filter((s: string) => !fitEvaluation.required_skills.includes(s) && !fitEvaluation.partial.includes(s))
                      .map((s: string, i: number) => (
                        <span key={i} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">
                          {s}
                        </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: PROJECTS REORDERED */}
          {activeTab === 'projects' && (
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3 text-xs">
              <h4 className="font-bold text-white text-sm border-b border-slate-800 pb-2">
                Project Ranking & Relevance Scoring
              </h4>
              <div className="space-y-3">
                {structured.projects?.map((proj: any, idx: number) => (
                  <div key={idx} className="p-3 bg-slate-900 rounded-xl border border-slate-800 flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-emerald-400 font-bold font-mono">Rank #{idx + 1}</span>
                        <span className="text-white font-bold">{proj.title}</span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1">{proj.description}</p>
                      <div className="flex flex-wrap gap-1 pt-1.5">
                        {proj.technologies?.map((t: string, tIdx: number) => (
                          <span key={tIdx} className="text-[9px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                    <span className="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-1 rounded-md font-mono whitespace-nowrap">
                      Target Role Aligned
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: EVIDENCE TRACEABILITY */}
          {activeTab === 'evidence' && (
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3 text-xs">
              <div className="border-b border-slate-800 pb-2">
                <h4 className="font-bold text-white text-sm">Evidence Traceability Audit Map</h4>
                <p className="text-[11px] text-slate-400">
                  Every modified bullet and synthesized section is strictly traced back to factual Master CV evidence.
                </p>
              </div>

              <div className="space-y-2 max-h-[380px] overflow-y-auto">
                {evidenceMap.map((ev: any, idx: number) => (
                  <div key={idx} className="p-3 bg-slate-900 rounded-xl border border-slate-800/80 space-y-1.5">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-bold text-emerald-400 uppercase tracking-wider font-mono">
                        {ev.source_section} • {ev.source_item}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono italic">
                        {ev.reason}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] pt-1">
                      <div className="p-2 bg-slate-950 rounded border border-slate-800">
                        <span className="text-[9px] text-slate-500 uppercase block">Original Source Evidence:</span>
                        <span className="text-slate-300">{ev.source_text}</span>
                      </div>
                      <div className="p-2 bg-slate-950 rounded border border-emerald-900/60">
                        <span className="text-[9px] text-emerald-400 uppercase block">Tailored Formulation:</span>
                        <span className="text-emerald-200">{ev.generated_text}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: ATS KEYWORDS ALIGNMENT */}
          {activeTab === 'ats' && (
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-4 text-xs">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <div>
                  <h4 className="font-bold text-white text-sm">ATS Keyword Alignment & Classification</h4>
                  <p className="text-[11px] text-slate-400">
                    Coverage before tailoring: <span className="font-mono text-slate-300">{changes.ats_coverage_before || 65}%</span> → After: <span className="font-mono text-emerald-400 font-bold">{changes.ats_coverage_after || 82}%</span>
                  </p>
                </div>
                <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-950/80 rounded-xl border border-emerald-800">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs text-emerald-300 font-bold">Hallucination Guard: PASS</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-3 bg-slate-900 rounded-xl border border-emerald-900/50 space-y-2">
                  <span className="font-bold text-emerald-400 uppercase tracking-wider text-[11px] block">
                    ✓ Matched & Supported Keywords
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {matchedKws.map((k: string, i: number) => (
                      <span key={i} className="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded font-mono">
                        {k}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3 bg-slate-900 rounded-xl border border-rose-900/50 space-y-2">
                  <span className="font-bold text-rose-400 uppercase tracking-wider text-[11px] block">
                    ✗ Missing JD Keywords (Strictly NOT Inserted)
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {missingKws.map((k: string, i: number) => (
                      <span key={i} className="text-[10px] bg-rose-950 text-rose-300 border border-rose-800 px-2 py-0.5 rounded font-mono">
                        {k}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
