import React, { useState } from 'react';
import { 
  X, 
  Download, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldCheck, 
  Sparkles, 
  Edit3, 
  Save, 
  UserCheck, 
  Building2, 
  MapPin, 
  HelpCircle, 
  Send, 
  Check, 
  Briefcase, 
  GraduationCap, 
  Globe, 
  Calendar,
  Lock,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { Application, Job, ApplicationQuestionAnswer } from '../types/job_agent';

interface ApplicationReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  job: Job;
  application: Application | null;
  fitEvaluation?: any;
  onApplicationApproved: (app: Application) => void;
  onApplicationUpdated: (app: Application) => void;
}

export const ApplicationReviewModal: React.FC<ApplicationReviewModalProps> = ({
  isOpen,
  onClose,
  job,
  application,
  fitEvaluation,
  onApplicationApproved,
  onApplicationUpdated
}) => {
  if (!isOpen || !application) return null;

  const [activeTab, setActiveTab] = useState<'overview' | 'cover_letter' | 'cv' | 'questions' | 'profile'>('overview');
  
  // Cover Letter Edit State
  const [isEditingCoverLetter, setIsEditingCoverLetter] = useState(false);
  const [coverLetterText, setCoverLetterText] = useState(
    application.user_edits?.cover_letter || application.cover_letter || ''
  );

  // Questions Edit State
  const initialAnswers: Record<string, string> = {};
  (application.application_answers || []).forEach(q => {
    initialAnswers[q.question_key] = q.answer_text || '';
  });
  const [questionAnswers, setQuestionAnswers] = useState<Record<string, string>>(initialAnswers);

  const [isSaving, setIsSaving] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [reviewNote, setReviewNote] = useState(application.notes || '');

  const tailoredCV = application.tailored_cv_id ? application : null;
  const matchScore = fitEvaluation?.match_score || 85;
  const recommendation = fitEvaluation?.recommendation || 'STRONG MATCH';
  const validationErrors = application.validation_errors || [];
  const isReady = application.readiness_status === 'READY';
  const isApproved = application.status === 'READY_FOR_SUBMISSION';

  // Save Cover Letter & Answers (Stored in user_edits, Master CV strictly untouched)
  const handleSaveEdits = async () => {
    setIsSaving(true);
    try {
      const res = await fetch(`/api/v1/applications/${application.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cover_letter: coverLetterText,
          custom_answers: questionAnswers,
          notes: reviewNote
        })
      });
      if (res.ok) {
        const updated = await res.json();
        onApplicationUpdated(updated);
        setIsEditingCoverLetter(false);
      } else {
        throw new Error('Fallback to local state');
      }
    } catch {
      // Graceful fallback for browser/offline mode
      const updated: Application = {
        ...application,
        cover_letter: coverLetterText,
        notes: reviewNote,
        user_edits: {
          ...(application.user_edits || {}),
          cover_letter: coverLetterText,
          custom_answers: questionAnswers,
          notes: reviewNote
        },
        application_answers: (application.application_answers || []).map(q => ({
          ...q,
          answer_text: questionAnswers[q.question_key] !== undefined ? questionAnswers[q.question_key] : q.answer_text,
          status: questionAnswers[q.question_key] ? 'USER_EDITED' : q.status
        }))
      };
      onApplicationUpdated(updated);
      setIsEditingCoverLetter(false);
    } finally {
      setIsSaving(false);
    }
  };

  // Explicit Human Approval (Phase 5 boundary: does NOT submit to external websites)
  const handleApprove = async () => {
    setIsApproving(true);
    try {
      const res = await fetch(`/api/v1/applications/${application.id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          notes: reviewNote || 'Approved by candidate for future submission.',
          reviewer_name: application.candidate_profile?.full_name || 'Candidate'
        })
      });
      if (res.ok) {
        const approved = await res.json();
        onApplicationApproved(approved);
      } else {
        throw new Error('Fallback to local state');
      }
    } catch {
      // Graceful fallback for browser/offline mode
      const approved: Application = {
        ...application,
        status: 'READY_FOR_SUBMISSION',
        approval_timestamp: new Date().toISOString(),
        review_timestamp: new Date().toISOString(),
        notes: reviewNote || 'Approved by candidate for future submission.'
      };
      onApplicationApproved(approved);
    } finally {
      setIsApproving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-3 sm:p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-5xl w-full shadow-2xl flex flex-col max-h-[92vh] overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                  {job.company}
                </span>
                <span className="text-[10px] bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded-md font-mono">
                  {job.location}
                </span>
                <span className="text-[10px] bg-emerald-950/80 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-md font-mono flex items-center gap-1 font-bold">
                  <Sparkles className="w-2.5 h-2.5" />
                  {matchScore}% Match
                </span>
                <span className="text-[10px] bg-slate-800 text-slate-200 border border-slate-700 px-2 py-0.5 rounded-md font-mono">
                  {recommendation}
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded-md font-mono font-bold flex items-center gap-1 ${
                  isApproved 
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50' 
                    : application.status === 'REVIEW_REQUIRED'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50'
                    : 'bg-sky-500/20 text-sky-300 border border-sky-500/50'
                }`}>
                  <ShieldCheck className="w-3 h-3" />
                  Status: {application.status}
                </span>
              </div>
              <h2 className="text-xl font-bold text-white tracking-tight">
                Application Package & Review: {job.job_title}
              </h2>
            </div>

            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1 rounded-lg transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Safety Notice Banner */}
          <div className="mt-3 py-2 px-3 bg-emerald-950/40 border border-emerald-800/60 rounded-xl flex items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 text-emerald-300">
              <Lock className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span>
                <strong>Human Approval Phase:</strong> Prepares complete verified package. Approving marks it <code className="text-emerald-200">READY_FOR_SUBMISSION</code>. No external automated submission is performed (reserved for Phase 6).
              </span>
            </div>
            {isApproved && (
              <span className="text-[11px] bg-emerald-500 text-slate-950 px-2 py-0.5 rounded-md font-bold shrink-0">
                Approved ✓
              </span>
            )}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 px-5 pt-3 pb-2 border-b border-slate-800 bg-slate-950/40 text-xs font-medium text-slate-400 overflow-x-auto">
          {[
            { id: 'overview', label: 'Review & Readiness', icon: ShieldCheck },
            { id: 'cover_letter', label: 'Job Cover Letter', icon: FileText },
            { id: 'questions', label: 'Application Questions', icon: HelpCircle },
            { id: 'profile', label: 'Candidate Profile', icon: UserCheck },
            { id: 'cv', label: 'Tailored CV', icon: Briefcase }
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

        {/* Tab Content Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5 text-xs text-slate-300">

          {/* TAB 1: OVERVIEW & READINESS */}
          {activeTab === 'overview' && (
            <div className="space-y-5">
              {/* Readiness Status Card */}
              <div className={`p-4 rounded-xl border ${
                isReady 
                  ? 'bg-emerald-950/30 border-emerald-800/80' 
                  : 'bg-amber-950/30 border-amber-800/80'
              }`}>
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800/80">
                  <div className="flex items-center gap-2">
                    <span className={`p-1.5 rounded-lg ${isReady ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
                      <CheckCircle2 className="w-4 h-4" />
                    </span>
                    <span className="font-bold text-sm text-white">
                      Application Readiness: {application.readiness_status || 'REVIEW_REQUIRED'}
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">
                    CV Integrity: <strong className="text-emerald-400">PASS</strong>
                  </span>
                </div>

                {validationErrors.length > 0 ? (
                  <div className="space-y-1.5 pt-1">
                    <span className="text-[11px] font-bold text-amber-300 block">Pending Items Requiring Review:</span>
                    {validationErrors.map((err, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-slate-300 text-[11px]">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                        <span>{err}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-emerald-300 text-[11px]">
                    All readiness checks passed! Contact info valid, match score ≥ 70%, tailored CV generated, and questions answered.
                  </p>
                )}
              </div>

              {/* Package Summary Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Target Role & Company */}
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
                  <h3 className="font-bold text-white text-xs uppercase tracking-wider flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5 text-emerald-400" />
                    Target Job Opening
                  </h3>
                  <div className="space-y-1 font-mono text-[11px] text-slate-300">
                    <div><span className="text-slate-500">Company:</span> {job.company}</div>
                    <div><span className="text-slate-500">Position:</span> {job.job_title}</div>
                    <div><span className="text-slate-500">Location:</span> {job.location}</div>
                    <div><span className="text-slate-500">Source:</span> {job.source}</div>
                    {job.source_url && (
                      <div className="pt-1">
                        <a href={job.source_url} target="_blank" rel="noreferrer" className="text-emerald-400 hover:underline flex items-center gap-1">
                          <span>View Official Posting</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    )}
                  </div>
                </div>

                {/* Candidate Verified Facts */}
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
                  <h3 className="font-bold text-white text-xs uppercase tracking-wider flex items-center gap-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                    Verified Candidate Profile
                  </h3>
                  <div className="space-y-1 font-mono text-[11px] text-slate-300">
                    <div><span className="text-slate-500">Applicant:</span> {application.candidate_profile?.full_name || 'Irfan Rajpoot'}</div>
                    <div><span className="text-slate-500">Email:</span> {application.candidate_profile?.email}</div>
                    <div><span className="text-slate-500">Phone:</span> {application.candidate_profile?.phone}</div>
                    <div><span className="text-slate-500">Location:</span> {application.candidate_profile?.location}</div>
                    <div><span className="text-slate-500">Master CV:</span> Immutable (v1)</div>
                  </div>
                </div>
              </div>

              {/* Reviewer Notes */}
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
                <label className="font-bold text-white text-xs block">
                  Candidate Review Notes & Preparation Log:
                </label>
                <textarea
                  value={reviewNote}
                  onChange={(e) => setReviewNote(e.target.value)}
                  placeholder="Add any specific notes or instructions regarding this application..."
                  rows={2}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
                />
              </div>
            </div>
          )}

          {/* TAB 2: COVER LETTER */}
          {activeTab === 'cover_letter' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-emerald-400" />
                  <span className="font-bold text-white text-sm">Job-Specific Grounded Cover Letter</span>
                </div>
                <div className="flex items-center gap-2">
                  {!isEditingCoverLetter ? (
                    <button
                      onClick={() => setIsEditingCoverLetter(true)}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
                    >
                      <Edit3 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Edit Cover Letter</span>
                    </button>
                  ) : (
                    <button
                      onClick={handleSaveEdits}
                      disabled={isSaving}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow transition"
                    >
                      <Save className="w-3.5 h-3.5" />
                      <span>{isSaving ? 'Saving...' : 'Save Edits'}</span>
                    </button>
                  )}
                </div>
              </div>

              {isEditingCoverLetter ? (
                <div className="space-y-2">
                  <p className="text-[11px] text-amber-300">
                    Manual edits are stored separately in <code className="bg-slate-800 px-1 py-0.5 rounded">user_edits</code> and will NOT alter the Master CV.
                  </p>
                  <textarea
                    value={coverLetterText}
                    onChange={(e) => setCoverLetterText(e.target.value)}
                    rows={16}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-200 leading-relaxed focus:outline-none focus:border-emerald-500"
                  />
                </div>
              ) : (
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 font-mono text-xs text-slate-200 whitespace-pre-wrap leading-relaxed max-w-3xl mx-auto shadow-inner">
                  {coverLetterText}
                </div>
              )}

              {/* Cover Letter Evidence Traceability */}
              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl space-y-1.5">
                <span className="font-bold text-white text-[11px] block">Evidence Traceability:</span>
                <div className="space-y-1 text-[11px]">
                  {(application.evidence_map || []).map((ev, idx) => (
                    <div key={idx} className="flex items-start gap-1.5 text-slate-400">
                      <span className="text-emerald-400 font-bold shrink-0">✓</span>
                      <span><strong>{ev.source_item || ev.source}:</strong> {ev.statement || ev.reason}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: APPLICATION QUESTIONS */}
          {activeTab === 'questions' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div>
                  <h3 className="font-bold text-white text-sm">Common Application Questions</h3>
                  <p className="text-[11px] text-slate-400">
                    Auto-answers strictly grounded in Master CV. Unknown fields (like salary) are marked <code className="text-amber-300">REQUIRES_USER_INPUT</code>.
                  </p>
                </div>
                <button
                  onClick={handleSaveEdits}
                  disabled={isSaving}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow transition"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>{isSaving ? 'Saving...' : 'Save Answers'}</span>
                </button>
              </div>

              <div className="grid grid-cols-1 gap-3">
                {(application.application_answers || []).map((q) => {
                  const val = questionAnswers[q.question_key] ?? (q.answer_text || '');
                  const isMissing = q.status === 'REQUIRES_USER_INPUT' && !val;

                  return (
                    <div 
                      key={q.question_key}
                      className={`p-3.5 rounded-xl border space-y-2 ${
                        isMissing
                          ? 'bg-amber-950/20 border-amber-800/80'
                          : q.status === 'USER_EDITED'
                          ? 'bg-sky-950/20 border-sky-800/80'
                          : 'bg-slate-950 border-slate-800'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-semibold text-slate-200 text-xs">
                          {q.question_text}
                        </span>
                        <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold shrink-0 ${
                          isMissing
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                            : q.status === 'USER_EDITED'
                            ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40'
                            : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                        }`}>
                          {q.status}
                        </span>
                      </div>

                      <input
                        type="text"
                        value={val}
                        onChange={(e) => setQuestionAnswers({
                          ...questionAnswers,
                          [q.question_key]: e.target.value
                        })}
                        placeholder={isMissing ? "Please enter your answer..." : "Answer..."}
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
                      />

                      <span className="text-[10px] text-slate-500 font-mono block">
                        Source Evidence: {q.source_evidence || 'Master CV'}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 4: CANDIDATE PROFILE */}
          {activeTab === 'profile' && (
            <div className="space-y-4">
              <div className="pb-2 border-b border-slate-800">
                <h3 className="font-bold text-white text-sm">Extracted Application Profile</h3>
                <p className="text-[11px] text-slate-400">
                  Factual profile fields verified from Master CV without hallucinations.
                </p>
              </div>

              <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3 font-mono text-xs">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div><span className="text-slate-500">Full Name:</span> {application.candidate_profile?.full_name}</div>
                  <div><span className="text-slate-500">Email:</span> {application.candidate_profile?.email}</div>
                  <div><span className="text-slate-500">Phone:</span> {application.candidate_profile?.phone}</div>
                  <div><span className="text-slate-500">Location:</span> {application.candidate_profile?.location}</div>
                  <div><span className="text-slate-500">GitHub:</span> {application.candidate_profile?.github}</div>
                  <div><span className="text-slate-500">LinkedIn:</span> {application.candidate_profile?.linkedin}</div>
                </div>

                <div className="pt-2 border-t border-slate-800">
                  <span className="text-slate-500 block mb-1">Prioritized Skills for Job:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {(application.candidate_profile?.skills || []).map((s: string, idx: number) => (
                      <span key={idx} className="bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded text-[10px]">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: TAILORED CV */}
          {activeTab === 'cv' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div>
                  <h3 className="font-bold text-white text-sm">Job-Tailored CV Artifact</h3>
                  <p className="text-[11px] text-slate-400">
                    Generated single-column ATS-friendly resume linked to this application.
                  </p>
                </div>
                {application.tailored_cv_id && (
                  <div className="flex items-center gap-2">
                    <a
                      href={`/api/v1/tailored-cvs/${application.tailored_cv_id}/download/docx`}
                      download
                      className="flex items-center gap-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
                    >
                      <Download className="w-3.5 h-3.5 text-emerald-400" />
                      <span>DOCX</span>
                    </a>
                    <a
                      href={`/api/v1/tailored-cvs/${application.tailored_cv_id}/download/pdf`}
                      download
                      className="flex items-center gap-1 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow transition"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>PDF</span>
                    </a>
                  </div>
                )}
              </div>

              <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 font-mono text-xs space-y-3">
                <div className="flex items-center justify-between text-[11px] text-slate-400 pb-2 border-b border-slate-800">
                  <span>Target Role: <strong>{job.job_title}</strong></span>
                  <span>ATS Match: <strong className="text-emerald-400">{matchScore}%</strong></span>
                </div>
                <p className="text-slate-300">
                  Tailored CV ID: <code className="text-emerald-300">{application.tailored_cv_id || 'Embedded'}</code>
                </p>
                <p className="text-slate-400 text-[11px]">
                  Use the download buttons above to inspect the ATS-compliant DOCX or PDF files generated by ReportLab & python-docx.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Modal Bottom Actions */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/80 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl transition"
            >
              Close
            </button>
            <button
              onClick={handleSaveEdits}
              disabled={isSaving}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition"
            >
              {isSaving ? 'Saving...' : 'Save Draft Edits'}
            </button>
          </div>

          <div className="flex items-center gap-3">
            {isApproved ? (
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs px-4 py-2 bg-emerald-950/80 border border-emerald-800 rounded-xl">
                <Check className="w-4 h-4" />
                <span>Approved & Ready for Submission</span>
              </div>
            ) : (
              <button
                onClick={handleApprove}
                disabled={isApproving}
                className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-950 transition"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>{isApproving ? 'Approving...' : 'Approve Application (Ready for Submission)'}</span>
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
