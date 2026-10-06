/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { MasterCV, Job, Application, ApplicationStatus, JobStatus, JobDiscoveryRun } from './types/job_agent';
import { INITIAL_MASTER_CV, INITIAL_JOBS, INITIAL_APPLICATIONS } from './mock/initialData';
import { Navbar } from './components/Navbar';
import { MasterCVView } from './components/MasterCVView';
import { JobBoardView } from './components/JobBoardView';
import { ApplicationsView } from './components/ApplicationsView';
import { DatabaseSchemaView } from './components/DatabaseSchemaView';
import { LocalRunGuideModal } from './components/LocalRunGuideModal';
import { CheckCircle2 } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState<'cv' | 'jobs' | 'applications' | 'architecture'>('jobs');
  const [guideOpen, setGuideOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Load from local storage or defaults
  const [masterCV, setMasterCV] = useState<MasterCV>(() => {
    try {
      const saved = localStorage.getItem('lahore_job_agent_cv');
      return saved ? JSON.parse(saved) : INITIAL_MASTER_CV;
    } catch {
      return INITIAL_MASTER_CV;
    }
  });

  const [jobs, setJobs] = useState<Job[]>(() => {
    try {
      const saved = localStorage.getItem('lahore_job_agent_jobs');
      return saved ? JSON.parse(saved) : INITIAL_JOBS;
    } catch {
      return INITIAL_JOBS;
    }
  });

  const [applications, setApplications] = useState<Application[]>(() => {
    try {
      const saved = localStorage.getItem('lahore_job_agent_apps');
      return saved ? JSON.parse(saved) : INITIAL_APPLICATIONS;
    } catch {
      return INITIAL_APPLICATIONS;
    }
  });

  // Sync to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('lahore_job_agent_cv', JSON.stringify(masterCV));
    } catch (e) {
      console.error(e);
    }
  }, [masterCV]);

  useEffect(() => {
    try {
      localStorage.setItem('lahore_job_agent_jobs', JSON.stringify(jobs));
    } catch (e) {
      console.error(e);
    }
  }, [jobs]);

  useEffect(() => {
    try {
      localStorage.setItem('lahore_job_agent_apps', JSON.stringify(applications));
    } catch (e) {
      console.error(e);
    }
  }, [applications]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // CV Handlers
  const handleUpdateCV = (updated: MasterCV) => {
    setMasterCV(updated);
    showToast(`Master CV updated to version ${updated.version}`);
  };

  // Job Handlers (Phase 2 Discovery & Collection)
  const handleAddJob = (newJob: Job) => {
    setJobs(prev => [newJob, ...prev]);
    showToast(`Saved job opening at ${newJob.company}`);
  };

  const handleUpdateJobStatus = (jobId: string, status: JobStatus) => {
    setJobs(prev =>
      prev.map(j => (j.id === jobId ? { ...j, status, job_status: status, updated_at: new Date().toISOString() } : j))
    );
    showToast(`Job marked as ${status.toUpperCase()}`);
  };

  const handleDeleteJob = (jobId: string) => {
    setJobs(prev => prev.filter(j => j.id !== jobId));
    setApplications(prev => prev.filter(a => a.job_id !== jobId));
    showToast('Job removed from board');
  };

  const handleRefreshJob = (jobId: string) => {
    setJobs(prev =>
      prev.map(j => {
        if (j.id === jobId) {
          return {
            ...j,
            updated_at: new Date().toISOString()
          };
        }
        return j;
      })
    );
    showToast('Re-cleaned and normalized job listing');
  };

  const handleRunDiscovery = (run: JobDiscoveryRun, newJobs: Job[]) => {
    if (newJobs.length > 0) {
      setJobs(prev => {
        const existingIds = new Set(prev.map(j => j.id));
        const filteredNew = newJobs.filter(j => !existingIds.has(j.id));
        return [...filteredNew, ...prev];
      });
      showToast(`Discovery Run complete! Added ${newJobs.length} new Lahore jobs.`);
    } else {
      showToast('Discovery complete: No new unique jobs found.');
    }
  };

  const handleApplyJob = (jobId: string) => {
    const job = jobs.find(j => j.id === jobId);
    if (!job) return;

    // Check if already applied
    const exists = applications.find(a => a.job_id === jobId);
    if (exists) {
      showToast('Job is already in your application pipeline.');
      return;
    }

    const newApp: Application = {
      id: `app-${Date.now()}`,
      user_id: masterCV.user_id,
      job_id: jobId,
      master_cv_id: masterCV.id,
      status: 'applied',
      applied_at: new Date().toISOString(),
      notes: `Applied with Master CV v${masterCV.version}.`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    setApplications(prev => [newApp, ...prev]);
    // Also update job status to applied
    handleUpdateJobStatus(jobId, 'applied');
    showToast(`Created application for ${job.company}!`);
  };

  const handleResetJobs = () => {
    setJobs(INITIAL_JOBS);
    showToast('Restored default curated Lahore software house jobs.');
  };

  // Application Handlers
  const handleUpdateApplication = (appId: string, status: ApplicationStatus, notes?: string, interview_date?: string) => {
    setApplications(prev =>
      prev.map(app => {
        if (app.id === appId) {
          return {
            ...app,
            status,
            notes: notes !== undefined ? notes : app.notes,
            interview_date: interview_date !== undefined ? interview_date : app.interview_date,
            updated_at: new Date().toISOString()
          };
        }
        return app;
      })
    );
    showToast(`Application transitioned to ${status.toUpperCase()}`);
  };

  const handleDeleteApplication = (appId: string) => {
    setApplications(prev => prev.filter(a => a.id !== appId));
    showToast('Application record removed.');
  };

  // Global Actions
  const handleExportData = () => {
    const data = {
      app: 'Lahore AI Job Application Agent',
      phase: 2,
      exported_at: new Date().toISOString(),
      master_cv: masterCV,
      jobs,
      applications
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lahore_job_agent_phase2_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Database snapshot exported successfully.');
  };

  const handleResetData = () => {
    if (window.confirm('Reset all Master CV, jobs, and applications to default sample data?')) {
      setMasterCV(INITIAL_MASTER_CV);
      setJobs(INITIAL_JOBS);
      setApplications(INITIAL_APPLICATIONS);
      localStorage.clear();
      showToast('Reset to default sample data.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-emerald-500 selection:text-slate-950">
      {/* Toast alert */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 bg-emerald-500 text-slate-950 font-bold px-4 py-2.5 rounded-xl shadow-2xl animate-fade-in text-xs">
          <CheckCircle2 className="w-4 h-4 text-slate-950" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenGuide={() => setGuideOpen(true)}
        onExportData={handleExportData}
        onResetData={handleResetData}
        stats={{
          skillsCount: masterCV.skills.length,
          jobsCount: jobs.length,
          appsCount: applications.length,
          cvVersion: masterCV.version
        }}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'cv' && (
          <MasterCVView cv={masterCV} onUpdateCV={handleUpdateCV} />
        )}

        {activeTab === 'jobs' && (
          <JobBoardView
            jobs={jobs}
            applications={applications}
            onAddJob={handleAddJob}
            onUpdateJobStatus={handleUpdateJobStatus}
            onDeleteJob={handleDeleteJob}
            onApplyJob={handleApplyJob}
            onResetJobs={handleResetJobs}
            onRefreshJob={handleRefreshJob}
            onRunDiscovery={handleRunDiscovery}
          />
        )}

        {activeTab === 'applications' && (
          <ApplicationsView
            applications={applications}
            jobs={jobs}
            onUpdateApplication={handleUpdateApplication}
            onDeleteApplication={handleDeleteApplication}
          />
        )}

        {activeTab === 'architecture' && (
          <DatabaseSchemaView
            cv={masterCV}
            jobs={jobs}
            applications={applications}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-4 text-center text-xs text-slate-500">
        <p>
          Lahore AI Job Application Agent • Phase 2: Automated Job Discovery & Collection (Lahore Software Houses)
        </p>
      </footer>

      {/* Local Run Guide Modal */}
      <LocalRunGuideModal isOpen={guideOpen} onClose={() => setGuideOpen(false)} />
    </div>
  );
}
