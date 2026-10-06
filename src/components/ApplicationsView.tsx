import React, { useState } from 'react';
import { Application, Job, ApplicationStatus } from '../types/job_agent';
import { 
  CheckCircle2, 
  Clock, 
  Calendar, 
  ArrowRight, 
  FileText, 
  Building2, 
  MessageSquare, 
  Trash2, 
  Check, 
  Award,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  UserCheck,
  Edit3
} from 'lucide-react';
import { ApplicationReviewModal } from './ApplicationReviewModal';
import { evaluateJobFit } from '../utils/matching';

interface ApplicationsViewProps {
  applications: Application[];
  jobs: Job[];
  onUpdateApplication: (appId: string, status: ApplicationStatus, notes?: string, interview_date?: string) => void;
  onDeleteApplication: (appId: string) => void;
}

export const ApplicationsView: React.FC<ApplicationsViewProps> = ({
  applications,
  jobs,
  onUpdateApplication,
  onDeleteApplication
}) => {
  const [selectedAppForReview, setSelectedAppForReview] = useState<Application | null>(null);
  const [selectedJobForReview, setSelectedJobForReview] = useState<Job | null>(null);
  const [activeReviewModal, setActiveReviewModal] = useState(false);

  const [selectedAppIdForNotes, setSelectedAppIdForNotes] = useState<string | null>(null);
  const [editNotes, setEditNotes] = useState('');
  const [editDate, setEditDate] = useState('');

  const jobsMap = new Map(jobs.map(j => [j.id, j]));

  const stages: { key: string; title: string; color: string; desc: string }[] = [
    { key: 'DRAFT', title: 'Draft Applications', color: 'border-slate-800 bg-slate-900/60', desc: 'Package prepared, awaiting review' },
    { key: 'REVIEW_REQUIRED', title: 'Review Required', color: 'border-amber-500/30 bg-amber-950/20', desc: 'Pending user answers or CV review' },
    { key: 'READY_FOR_SUBMISSION', title: 'Approved & Ready', color: 'border-emerald-500/30 bg-emerald-950/20', desc: 'Approved by human, ready for Phase 6' },
    { key: 'applied', title: 'Applied / Sent', color: 'border-sky-500/30 bg-sky-950/20', desc: 'Submitted externally' },
    { key: 'interview', title: 'Technical Interview', color: 'border-indigo-500/30 bg-indigo-950/20', desc: 'Interview scheduled' },
    { key: 'offered', title: 'Offer Extended', color: 'border-teal-500/40 bg-teal-950/30', desc: 'Offer received' }
  ];

  const handleOpenReviewModal = async (app: Application) => {
    const job = jobsMap.get(app.job_id);
    if (!job) return;

    // Fetch full application package from API if available
    try {
      const res = await fetch(`/api/v1/applications/${app.id}`);
      if (res.ok) {
        const fullApp = await res.json();
        setSelectedAppForReview(fullApp);
      } else {
        setSelectedAppForReview(app);
      }
    } catch {
      setSelectedAppForReview(app);
    }

    setSelectedJobForReview(job);
    setActiveReviewModal(true);
  };

  const handleApplicationApproved = (approvedApp: Application) => {
    onUpdateApplication(approvedApp.id, approvedApp.status, approvedApp.notes, approvedApp.interview_date);
    setSelectedAppForReview(approvedApp);
  };

  const handleApplicationUpdated = (updatedApp: Application) => {
    onUpdateApplication(updatedApp.id, updatedApp.status, updatedApp.notes, updatedApp.interview_date);
    setSelectedAppForReview(updatedApp);
  };

  const handleOpenNotes = (app: Application) => {
    setSelectedAppIdForNotes(app.id);
    setEditNotes(app.notes || '');
    setEditDate(app.interview_date ? app.interview_date.split('T')[0] : '');
  };

  const handleSaveNotes = () => {
    if (!selectedAppIdForNotes) return;
    const current = applications.find(a => a.id === selectedAppIdForNotes);
    if (!current) return;
    onUpdateApplication(selectedAppIdForNotes, current.status, editNotes, editDate ? new Date(editDate).toISOString() : undefined);
    setSelectedAppIdForNotes(null);
  };

  // Status mapping helper
  const mapStatusKey = (status: string) => {
    const s = (status || '').toUpperCase();
    if (s === 'DRAFT' || s === 'SAVED') return 'DRAFT';
    if (s === 'REVIEW_REQUIRED') return 'REVIEW_REQUIRED';
    if (s === 'READY_FOR_SUBMISSION' || s === 'READY') return 'READY_FOR_SUBMISSION';
    if (s === 'APPLIED') return 'applied';
    if (s === 'INTERVIEW') return 'interview';
    if (s === 'OFFERED' || s === 'OFFER') return 'offered';
    return 'DRAFT';
  };

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </span>
            <h2 className="text-xl font-bold text-white tracking-tight">Phase 5: Application Preparation & Human Approval</h2>
            <span className="text-xs bg-slate-800 text-slate-300 border border-slate-700 px-2.5 py-0.5 rounded-full font-medium">
              {applications.length} Packages
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Every application package includes verified job facts, job-tailored CV, grounded cover letter, and candidate questions. 
            <strong> Requires explicit human review before transitioning to Ready for Submission.</strong>
          </p>
        </div>
      </div>

      {/* Kanban Stages Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {stages.map(stage => {
          const stageApps = applications.filter(a => mapStatusKey(a.status) === stage.key);

          return (
            <div
              key={stage.key}
              className={`rounded-2xl border p-3 flex flex-col h-full min-h-[460px] ${stage.color}`}
            >
              {/* Column Header */}
              <div className="pb-3 mb-3 border-b border-slate-800/80">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white tracking-tight">
                    {stage.title}
                  </span>
                  <span className="text-[10px] bg-slate-950/80 text-slate-300 border border-slate-800 px-2 py-0.5 rounded-full font-mono font-bold">
                    {stageApps.length}
                  </span>
                </div>
                <span className="text-[10px] text-slate-500 block mt-0.5">{stage.desc}</span>
              </div>

              {/* Application Cards */}
              <div className="space-y-3 flex-1 overflow-y-auto">
                {stageApps.length === 0 ? (
                  <div className="text-center py-10 text-[11px] text-slate-500 italic">
                    No applications
                  </div>
                ) : (
                  stageApps.map(app => {
                    const job = jobsMap.get(app.job_id);
                    if (!job) return null;
                    const fit = evaluateJobFit(job);
                    const isApproved = app.status === 'READY_FOR_SUBMISSION';
                    const isReady = app.readiness_status === 'READY';

                    return (
                      <div
                        key={app.id}
                        className="bg-slate-950 border border-slate-800/80 hover:border-slate-700 p-3.5 rounded-xl space-y-2.5 shadow-md transition group"
                      >
                        {/* Company & Title */}
                        <div>
                          <div className="flex items-center justify-between">
                            <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider">
                              {job.company}
                            </span>
                            <button
                              onClick={() => onDeleteApplication(app.id)}
                              className="opacity-0 group-hover:opacity-100 text-slate-600 hover:text-rose-400 transition"
                              title="Delete from applications"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                          </div>
                          <h4 className="text-xs font-bold text-white mt-0.5 line-clamp-1">
                            {job.job_title}
                          </h4>
                        </div>

                        {/* Badges: Match Score & Readiness */}
                        <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono">
                          <span className="bg-emerald-950/60 text-emerald-300 border border-emerald-800 px-1.5 py-0.5 rounded">
                            {fit.match_score}% Match
                          </span>
                          <span className={`px-1.5 py-0.5 rounded ${
                            isReady
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                              : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                          }`}>
                            {app.readiness_status || 'REVIEW_REQUIRED'}
                          </span>
                        </div>

                        {/* Interview Date */}
                        {app.interview_date && (
                          <div className="flex items-center gap-1.5 text-[10px] font-mono text-emerald-300 bg-emerald-950/50 border border-emerald-800/60 p-1.5 rounded-lg">
                            <Calendar className="w-3 h-3 text-emerald-400 shrink-0" />
                            <span>{new Date(app.interview_date).toLocaleDateString()}</span>
                          </div>
                        )}

                        {/* Review / Approval Status Tag */}
                        {isApproved ? (
                          <div className="flex items-center gap-1 text-[10px] text-emerald-300 font-bold bg-emerald-950/40 border border-emerald-800 p-1.5 rounded-lg">
                            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                            <span>Approved for Submission</span>
                          </div>
                        ) : (
                          <button
                            onClick={() => handleOpenReviewModal(app)}
                            className="w-full flex items-center justify-center gap-1.5 py-1.5 px-2 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-600/40 rounded-lg text-[11px] font-semibold transition"
                          >
                            <Edit3 className="w-3 h-3" />
                            <span>Review & Approve</span>
                          </button>
                        )}

                        {/* Card Footer Actions */}
                        <div className="pt-2 border-t border-slate-900 flex items-center justify-between text-[11px]">
                          <button
                            onClick={() => handleOpenReviewModal(app)}
                            className="text-slate-400 hover:text-white flex items-center gap-1 transition text-[10px]"
                          >
                            <FileText className="w-3 h-3" />
                            <span>Inspect</span>
                          </button>

                          <button
                            onClick={() => handleOpenNotes(app)}
                            className="text-slate-500 hover:text-slate-300 text-[10px]"
                          >
                            Notes
                          </button>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Edit Notes Modal */}
      {selectedAppIdForNotes && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-sm font-bold text-white">Application Notes & Interview Date</h3>
            <div className="space-y-3">
              <div>
                <label className="text-[11px] font-bold text-slate-400 block mb-1">Interview Date:</label>
                <input
                  type="date"
                  value={editDate}
                  onChange={(e) => setEditDate(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                />
              </div>
              <div>
                <label className="text-[11px] font-bold text-slate-400 block mb-1">Notes:</label>
                <textarea
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => setSelectedAppIdForNotes(null)}
                className="px-3 py-1.5 bg-slate-800 text-slate-300 text-xs rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveNotes}
                className="px-3 py-1.5 bg-emerald-600 text-white text-xs font-bold rounded-lg"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Application Review & Approval Modal */}
      {selectedJobForReview && (
        <ApplicationReviewModal
          isOpen={activeReviewModal}
          onClose={() => {
            setActiveReviewModal(false);
            setSelectedJobForReview(null);
            setSelectedAppForReview(null);
          }}
          job={selectedJobForReview}
          application={selectedAppForReview}
          fitEvaluation={evaluateJobFit(selectedJobForReview)}
          onApplicationApproved={handleApplicationApproved}
          onApplicationUpdated={handleApplicationUpdated}
        />
      )}
    </div>
  );
};
