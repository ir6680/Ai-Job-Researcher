import React, { useState } from 'react';
import { 
  Job, 
  Application, 
  JobDiscoveryRun, 
  JobDiscoverySourceInfo,
  JobStatus 
} from '../types/job_agent';
import { 
  Briefcase, 
  Search, 
  Plus, 
  MapPin, 
  ExternalLink, 
  DollarSign, 
  Building2, 
  Check, 
  Calendar, 
  Clock, 
  RotateCw, 
  ShieldCheck, 
  Sparkles, 
  Bookmark, 
  Eye, 
  EyeOff, 
  Trash2, 
  Send, 
  Filter, 
  Activity, 
  CheckCircle2, 
  X, 
  Layers, 
  FileText,
  AlertTriangle
} from 'lucide-react';
import { DISCOVERY_SOURCES_LIST, INITIAL_DISCOVERY_RUNS } from '../mock/initialData';
import { evaluateJobFit } from '../utils/matching';

interface JobBoardViewProps {
  jobs: Job[];
  applications: Application[];
  onAddJob: (job: Job) => void;
  onUpdateJobStatus: (jobId: string, status: JobStatus) => void;
  onDeleteJob: (jobId: string) => void;
  onApplyJob: (jobId: string) => void;
  onResetJobs: () => void;
  onRefreshJob: (jobId: string) => void;
  onRunDiscovery: (run: JobDiscoveryRun, newJobs: Job[]) => void;
}

export const JobBoardView: React.FC<JobBoardViewProps> = ({
  jobs,
  applications,
  onAddJob,
  onUpdateJobStatus,
  onDeleteJob,
  onApplyJob,
  onResetJobs,
  onRefreshJob,
  onRunDiscovery
}) => {
  // State
  const [search, setSearch] = useState('');
  const [companyFilter, setCompanyFilter] = useState('All');
  const [sourceFilter, setSourceFilter] = useState('All');
  const [typeFilter, setTypeFilter] = useState('All');
  const [statusTab, setStatusTab] = useState<'all' | 'discovered' | 'saved' | 'ignored' | 'applied'>('all');

  // Modals
  const [selectedJobForDetails, setSelectedJobForDetails] = useState<Job | null>(null);
  const [showRawDesc, setShowRawDesc] = useState(false);
  const [showDiscoveryModal, setShowDiscoveryModal] = useState(false);
  const [showRunsHistoryModal, setShowRunsHistoryModal] = useState(false);
  const [showAddJobModal, setShowAddJobModal] = useState(false);

  // Discovery Run State
  const [discoveryKeywords, setDiscoveryKeywords] = useState<string[]>([
    "Python Developer",
    "Backend Developer",
    "Software Engineer",
    "Junior Developer",
    "AI/ML Engineer",
    "QA Engineer",
    "Software Intern"
  ]);
  const [customKeywordInput, setCustomKeywordInput] = useState('');
  const [selectedSources, setSelectedSources] = useState<string[]>([
    "systems_limited",
    "arbisoft",
    "devsinc",
    "tintash",
    "ten_pearls",
    "netsol",
    "confiz",
    "rozee_pk"
  ]);
  const [isRunningDiscovery, setIsRunningDiscovery] = useState(false);
  const [discoveryResult, setDiscoveryResult] = useState<JobDiscoveryRun | null>(null);
  const [discoveryRunsHistory, setDiscoveryRunsHistory] = useState<JobDiscoveryRun[]>(INITIAL_DISCOVERY_RUNS);

  // Manual Add Job Form
  const [newJobForm, setNewJobForm] = useState({
    company: '',
    job_title: '',
    location: 'Lahore, Pakistan',
    job_url: '',
    description: '',
    required_skills: '',
    preferred_skills: '',
    experience_requirement: 'Entry-level (0-1 years)',
    education_requirement: 'BS Computer Science / Software Engineering',
    job_type: 'Full-time' as const,
    salary: 'PKR 100,000 - 140,000 / month',
    source: 'Company Careers Portal'
  });

  const appliedJobIds = new Set(applications.map(a => a.job_id));

  // Companies & Sources Facets
  const companiesList = ['All', ...Array.from(new Set(jobs.map(j => j.company)))];
  const sourcesList = ['All', ...Array.from(new Set(jobs.map(j => j.source)))];

  // Filter Logic
  const filteredJobs = jobs.filter(job => {
    const query = search.toLowerCase();
    const matchesSearch = 
      job.job_title.toLowerCase().includes(query) ||
      job.company.toLowerCase().includes(query) ||
      job.description.toLowerCase().includes(query) ||
      job.required_skills.some(s => s.toLowerCase().includes(query));

    const matchesCompany = companyFilter === 'All' || job.company === companyFilter;
    const matchesSource = sourceFilter === 'All' || job.source === sourceFilter;
    const matchesType = typeFilter === 'All' || job.job_type === typeFilter;

    let matchesStatus = true;
    if (statusTab === 'discovered') matchesStatus = (job.status === 'discovered' || !job.status);
    else if (statusTab === 'saved') matchesStatus = job.status === 'saved';
    else if (statusTab === 'ignored') matchesStatus = job.status === 'ignored';
    else if (statusTab === 'applied') matchesStatus = appliedJobIds.has(job.id) || job.status === 'applied';

    return matchesSearch && matchesCompany && matchesSource && matchesType && matchesStatus;
  });

  // Discovery Run Simulation
  const handleExecuteDiscovery = async () => {
    setIsRunningDiscovery(true);
    setDiscoveryResult(null);

    // Simulate multi-source network crawling & cleaning delay
    await new Promise(res => setTimeout(res, 1800));

    const newDiscoveredBatch: Job[] = [
      {
        id: `job-disc-${Date.now()}-1`,
        company: "Confiz",
        job_title: "Associate Software Engineer - Cloud & Web",
        location: "Lahore (Gulberg Campus)",
        job_url: "https://confiz.com/careers/associate-software-engineer",
        source_url: "https://confiz.com/careers/associate-software-engineer",
        description: "Confiz is hiring fresh Computer Science graduates for our Cloud Engineering team in Lahore. We deliver global retail, supply-chain, and enterprise cloud solutions.\n\nKey Responsibilities:\n- Build clean RESTful services with Python/FastAPI or Node.js.\n- Participate in database design and automated testing.\n- Work in Agile squads with CI/CD deployment pipelines.",
        raw_description: "Confiz is hiring fresh Computer Science graduates for our Cloud Engineering team in Lahore. We deliver global retail, supply-chain, and enterprise cloud solutions.\n\nKey Responsibilities:\n- Build clean RESTful services with Python/FastAPI or Node.js.\n- Participate in database design and automated testing.\n- Work in Agile squads with CI/CD deployment pipelines.",
        responsibilities: [
          "Implement backend APIs in Python with PostgreSQL.",
          "Write automated test cases using PyTest.",
          "Review code with team leads and participate in sprint planning."
        ],
        required_skills: ["Python", "SQL", "Git", "REST APIs", "Problem Solving"],
        preferred_skills: ["FastAPI", "PostgreSQL", "Docker", "Azure"],
        experience_requirement: "0-1 years (Entry-Level)",
        education_requirement: "BS Computer Science",
        job_type: "Hybrid",
        salary: "PKR 100,000 - 135,000 / month",
        source: "Confiz Careers",
        status: "discovered",
        job_status: "discovered",
        posting_date: new Date().toISOString().split('T')[0],
        deadline: "2026-11-15",
        duplicate_status: "unique",
        dedup_hash: `hash_confiz_${Date.now()}`,
        discovered_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: `job-disc-${Date.now()}-2`,
        company: "VentureDive",
        job_title: "Associate Software Engineer - Full Stack",
        location: "Lahore (DHA Phase 5)",
        job_url: "https://www.rozee.pk/venturedive-associate-software-engineer-lahore-jobs",
        source_url: "https://www.rozee.pk/venturedive-associate-software-engineer-lahore-jobs",
        description: "VentureDive is hiring fresh graduates with strong problem-solving fundamentals to build digital mobility and fintech products.\n\nKey Responsibilities:\n- Build web features using Python backend and React frontend.\n- Write reliable unit tests and debug issues across environments.\n- Learn and adopt cloud technologies under experienced tech leads.",
        raw_description: "VentureDive is hiring fresh graduates with strong problem-solving fundamentals to build digital mobility and fintech products.\n\nKey Responsibilities:\n- Build web features using Python backend and React frontend.\n- Write reliable unit tests and debug issues across environments.\n- Learn and adopt cloud technologies under experienced tech leads.",
        responsibilities: [
          "Build modern web application features using Python and React.",
          "Ensure code quality with thorough automated testing.",
          "Participate in agile sprint ceremonies."
        ],
        required_skills: ["Python", "JavaScript", "React", "SQL", "Git"],
        preferred_skills: ["FastAPI", "PostgreSQL", "Docker"],
        experience_requirement: "Fresh Graduate",
        education_requirement: "BS in Computing / Software Engineering",
        job_type: "Hybrid",
        salary: "PKR 100,000 - 135,000 / month",
        source: "Rozee.pk Job Board",
        status: "discovered",
        job_status: "discovered",
        posting_date: new Date().toISOString().split('T')[0],
        deadline: "2026-11-10",
        duplicate_status: "unique",
        dedup_hash: `hash_venturedive_${Date.now()}`,
        discovered_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ];

    const runRecord: JobDiscoveryRun = {
      id: `run-${Date.now()}`,
      triggered_at: new Date(Date.now() - 2000).toISOString(),
      completed_at: new Date().toISOString(),
      status: "completed",
      sources_checked: selectedSources,
      keywords_used: discoveryKeywords,
      total_discovered: 8,
      new_jobs_added: 2,
      duplicates_skipped: 3,
      rejected_non_lahore: 2,
      rejected_non_entry: 1
    };

    setDiscoveryResult(runRecord);
    setDiscoveryRunsHistory(prev => [runRecord, ...prev]);
    setIsRunningDiscovery(false);

    // Call parent to append jobs to state
    onRunDiscovery(runRecord, newDiscoveredBatch);
  };

  const handleAddKeyword = () => {
    if (!customKeywordInput.trim()) return;
    if (!discoveryKeywords.includes(customKeywordInput.trim())) {
      setDiscoveryKeywords([...discoveryKeywords, customKeywordInput.trim()]);
    }
    setCustomKeywordInput('');
  };

  const handleRemoveKeyword = (kw: string) => {
    setDiscoveryKeywords(discoveryKeywords.filter(k => k !== kw));
  };

  const toggleSourceSelection = (sourceId: string) => {
    if (selectedSources.includes(sourceId)) {
      setSelectedSources(selectedSources.filter(s => s !== sourceId));
    } else {
      setSelectedSources([...selectedSources, sourceId]);
    }
  };

  const handleManualAddJob = () => {
    if (!newJobForm.company.trim() || !newJobForm.job_title.trim() || !newJobForm.description.trim()) return;

    const reqSkills = newJobForm.required_skills.split(',').map(s => s.trim()).filter(Boolean);
    const prefSkills = newJobForm.preferred_skills.split(',').map(s => s.trim()).filter(Boolean);

    const job: Job = {
      id: `job-${Date.now()}`,
      company: newJobForm.company.trim(),
      job_title: newJobForm.job_title.trim(),
      location: newJobForm.location.trim(),
      job_url: newJobForm.job_url.trim() || undefined,
      source_url: newJobForm.job_url.trim() || undefined,
      description: newJobForm.description.trim(),
      raw_description: newJobForm.description.trim(),
      responsibilities: [newJobForm.description.trim().slice(0, 150)],
      required_skills: reqSkills.length ? reqSkills : ['Python', 'SQL'],
      preferred_skills: prefSkills,
      experience_requirement: newJobForm.experience_requirement,
      education_requirement: newJobForm.education_requirement,
      job_type: newJobForm.job_type,
      salary: newJobForm.salary.trim() || undefined,
      source: newJobForm.source,
      status: 'saved',
      job_status: 'saved',
      duplicate_status: 'unique',
      discovered_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    onAddJob(job);
    setNewJobForm({
      company: '',
      job_title: '',
      location: 'Lahore, Pakistan',
      job_url: '',
      description: '',
      required_skills: '',
      preferred_skills: '',
      experience_requirement: 'Entry-level (0-1 years)',
      education_requirement: 'BS Computer Science / Software Engineering',
      job_type: 'Full-time',
      salary: 'PKR 100,000 - 140,000 / month',
      source: 'Company Careers Portal'
    });
    setShowAddJobModal(false);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Discovery Actions Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl relative overflow-hidden">
        <div className="absolute -top-12 -right-12 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
                <Briefcase className="w-5 h-5" />
              </span>
              <h2 className="text-xl font-bold text-white tracking-tight">Phase 2: Job Discovery & Collection</h2>
              <span className="text-xs bg-emerald-950/80 text-emerald-300 border border-emerald-800 px-2.5 py-0.5 rounded-full font-semibold">
                Lahore Tech Engine
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
              Automated multi-source collector targeting entry-level roles at premier Lahore software houses.
              Extracts complete descriptions, cleans data, filters non-Lahore/senior roles, and eliminates duplicates.
            </p>
          </div>

          {/* Primary Action Buttons */}
          <div className="flex flex-wrap items-center gap-2 self-start md:self-auto">
            <button
              onClick={() => setShowDiscoveryModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-emerald-500/20 transition"
            >
              <Sparkles className="w-4 h-4 text-slate-950" />
              <span>Run Job Discovery</span>
            </button>

            <button
              onClick={() => setShowRunsHistoryModal(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium text-xs rounded-xl transition"
              title="View past discovery run logs and metrics"
            >
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <span>Run Metrics ({discoveryRunsHistory.length})</span>
            </button>

            <button
              onClick={() => setShowAddJobModal(true)}
              className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-xl border border-slate-700 transition"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Job</span>
            </button>
          </div>
        </div>

        {/* Quick Stats Bar */}
        <div className="pt-4 mt-4 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3 bg-slate-950/70 border border-slate-800/80 rounded-xl">
            <span className="text-slate-400 block text-[11px]">Total Tracked Jobs</span>
            <span className="text-lg font-bold text-white font-mono">{jobs.length}</span>
          </div>
          <div className="p-3 bg-slate-950/70 border border-slate-800/80 rounded-xl">
            <span className="text-slate-400 block text-[11px]">Discovered & New</span>
            <span className="text-lg font-bold text-sky-400 font-mono">
              {jobs.filter(j => j.status === 'discovered').length}
            </span>
          </div>
          <div className="p-3 bg-slate-950/70 border border-slate-800/80 rounded-xl">
            <span className="text-slate-400 block text-[11px]">Saved Candidates</span>
            <span className="text-lg font-bold text-emerald-400 font-mono">
              {jobs.filter(j => j.status === 'saved').length}
            </span>
          </div>
          <div className="p-3 bg-slate-950/70 border border-slate-800/80 rounded-xl">
            <span className="text-slate-400 block text-[11px]">In Applications Pipeline</span>
            <span className="text-lg font-bold text-indigo-400 font-mono">
              {applications.length}
            </span>
          </div>
        </div>
      </div>

      {/* Filter and Status Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-5 shadow-lg space-y-3">
        {/* Status Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto pb-1 text-xs border-b border-slate-800">
          {(['all', 'discovered', 'saved', 'ignored', 'applied'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setStatusTab(tab)}
              className={`px-3.5 py-1.5 rounded-lg font-semibold uppercase tracking-wider text-[11px] transition whitespace-nowrap ${
                statusTab === tab
                  ? 'bg-emerald-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Faceted Filter Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 text-xs pt-1">
          <div className="sm:col-span-5 relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by title, company, skill (Python, SQL), or JD text..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="sm:col-span-3">
            <select
              value={companyFilter}
              onChange={e => setCompanyFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-300 focus:outline-none focus:border-emerald-500"
            >
              {companiesList.map(c => (
                <option key={c} value={c}>{c === 'All' ? 'All Companies' : c}</option>
              ))}
            </select>
          </div>

          <div className="sm:col-span-2">
            <select
              value={sourceFilter}
              onChange={e => setSourceFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-300 focus:outline-none focus:border-emerald-500"
            >
              {sourcesList.map(s => (
                <option key={s} value={s}>{s === 'All' ? 'All Sources' : s}</option>
              ))}
            </select>
          </div>

          <div className="sm:col-span-2">
            <select
              value={typeFilter}
              onChange={e => setTypeFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-300 focus:outline-none focus:border-emerald-500"
            >
              <option value="All">All Types</option>
              <option value="Full-time">Full-time</option>
              <option value="Hybrid">Hybrid</option>
              <option value="Internship">Internship</option>
            </select>
          </div>
        </div>
      </div>

      {/* Jobs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filteredJobs.length === 0 ? (
          <div className="col-span-2 text-center py-16 bg-slate-900 border border-slate-800 rounded-2xl space-y-3">
            <Briefcase className="w-10 h-10 text-slate-600 mx-auto" />
            <h3 className="text-base font-semibold text-white">No jobs match your filter</h3>
            <p className="text-xs text-slate-400">
              Try adjusting your search, changing the status tab, or run automated discovery.
            </p>
          </div>
        ) : (
          filteredJobs.map(job => {
            const isApplied = appliedJobIds.has(job.id);

            return (
              <div
                key={job.id}
                className="bg-slate-900 border border-slate-800 hover:border-slate-700/80 rounded-2xl p-5 shadow-lg flex flex-col justify-between space-y-4 transition"
              >
                <div className="space-y-3">
                  {/* Top Bar: Company, Source Badge & Status */}
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                          <Building2 className="w-3.5 h-3.5" />
                          {job.company}
                        </span>
                        <span className="text-[10px] bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded-md font-medium">
                          {job.source}
                        </span>
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md uppercase tracking-wider ${
                          job.status === 'saved'
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                            : job.status === 'ignored'
                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                            : 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                        }`}>
                          {job.status}
                        </span>
                        {(() => {
                          const fit = evaluateJobFit(job);
                          return (
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md flex items-center gap-1 font-mono ${
                              fit.match_score >= 80 
                                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' 
                                : 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                            }`}>
                              <Sparkles className="w-2.5 h-2.5" />
                              {fit.match_score}% Match
                            </span>
                          );
                        })()}
                      </div>
                      <h3 className="text-base font-bold text-white mt-1 leading-snug">
                        {job.job_title}
                      </h3>
                    </div>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => onRefreshJob(job.id)}
                        className="p-1.5 text-slate-500 hover:text-slate-300 transition rounded-md"
                        title="Re-clean and normalize job description"
                      >
                        <RotateCw className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => onDeleteJob(job.id)}
                        className="p-1.5 text-slate-600 hover:text-rose-400 transition rounded-md"
                        title="Delete job"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Metadata Row */}
                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span>{job.location}</span>
                    </div>
                    {job.salary && (
                      <div className="flex items-center gap-1 font-mono text-emerald-300">
                        <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                        <span>{job.salary}</span>
                      </div>
                    )}
                    {job.posting_date && (
                      <div className="flex items-center gap-1 text-[11px] font-mono text-slate-400">
                        <Calendar className="w-3.5 h-3.5 text-slate-500" />
                        <span>Posted: {job.posting_date}</span>
                      </div>
                    )}
                  </div>

                  {/* Description Preview */}
                  <p className="text-xs text-slate-300 leading-relaxed line-clamp-3">
                    {job.description}
                  </p>

                  {/* Responsibilities count if parsed */}
                  {job.responsibilities && job.responsibilities.length > 0 && (
                    <div className="text-[11px] text-slate-400 font-medium">
                      <span className="text-emerald-400 font-semibold">• </span>
                      {job.responsibilities[0]}
                      {job.responsibilities.length > 1 && (
                        <span className="text-slate-500 italic"> (+{job.responsibilities.length - 1} more)</span>
                      )}
                    </div>
                  )}

                  {/* Skills badges */}
                  <div className="space-y-1.5 pt-1">
                    <div className="flex flex-wrap gap-1.5">
                      {job.required_skills.slice(0, 5).map((skill, i) => (
                        <span
                          key={i}
                          className="text-[10px] bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 px-2 py-0.5 rounded-md font-mono"
                        >
                          {skill}
                        </span>
                      ))}
                      {job.required_skills.length > 5 && (
                        <span className="text-[10px] text-slate-500 px-1 py-0.5 font-mono">
                          +{job.required_skills.length - 5}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Bottom Actions Row */}
                <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setSelectedJobForDetails(job)}
                      className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-xl border border-slate-700 font-medium transition"
                    >
                      <Eye className="w-3.5 h-3.5 text-emerald-400" />
                      <span>View Details</span>
                    </button>

                    {job.status === 'saved' ? (
                      <button
                        onClick={() => onUpdateJobStatus(job.id, 'discovered')}
                        className="text-xs text-emerald-400 hover:text-emerald-300 px-2 py-1 rounded-lg transition"
                        title="Unsave"
                      >
                        <Bookmark className="w-4 h-4 fill-emerald-400" />
                      </button>
                    ) : (
                      <button
                        onClick={() => onUpdateJobStatus(job.id, 'saved')}
                        className="text-xs text-slate-400 hover:text-white px-2 py-1 rounded-lg transition"
                        title="Save Job"
                      >
                        <Bookmark className="w-4 h-4" />
                      </button>
                    )}

                    {job.status === 'ignored' ? (
                      <button
                        onClick={() => onUpdateJobStatus(job.id, 'discovered')}
                        className="text-[11px] text-slate-400 hover:text-white underline"
                      >
                        Restore
                      </button>
                    ) : (
                      <button
                        onClick={() => onUpdateJobStatus(job.id, 'ignored')}
                        className="text-[11px] text-slate-500 hover:text-rose-400"
                        title="Ignore Job"
                      >
                        Ignore
                      </button>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {job.source_url && (
                      <a
                        href={job.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-slate-400 hover:text-emerald-400 flex items-center gap-1 font-medium transition"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span className="hidden sm:inline">Posting</span>
                      </a>
                    )}

                    {isApplied ? (
                      <div className="flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-950/40 border border-emerald-800 px-2.5 py-1 rounded-lg">
                        <Check className="w-3 h-3" />
                        <span>Applied</span>
                      </div>
                    ) : (
                      <button
                        onClick={() => onApplyJob(job.id)}
                        className="flex items-center gap-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs px-3 py-1.5 rounded-xl shadow transition"
                      >
                        <Send className="w-3 h-3" />
                        <span>Track</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* MODAL 1: COMPLETE JOB DETAILS (Shows Complete Collected Job Description) */}
      {selectedJobForDetails && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-3xl w-full shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-3 pb-3 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                    {selectedJobForDetails.company}
                  </span>
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-md font-mono">
                    {selectedJobForDetails.source}
                  </span>
                  <span className="text-[10px] bg-emerald-950/60 text-emerald-300 border border-emerald-800/80 px-2 py-0.5 rounded-md font-mono">
                    {selectedJobForDetails.job_type}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-white mt-1">
                  {selectedJobForDetails.job_title}
                </h3>
              </div>
              <button
                onClick={() => {
                  setSelectedJobForDetails(null);
                  setShowRawDesc(false);
                }}
                className="text-slate-400 hover:text-white p-1 rounded-lg transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Meta Attributes Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 font-mono">
              <div>
                <span className="text-slate-500 block text-[10px] uppercase">Location</span>
                <span className="text-slate-200">{selectedJobForDetails.location}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase">Salary</span>
                <span className="text-emerald-400">{selectedJobForDetails.salary || 'Competitive'}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase">Posted On</span>
                <span className="text-slate-200">{selectedJobForDetails.posting_date || 'Recent'}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase">Dedup Status</span>
                <span className="text-teal-400">{selectedJobForDetails.duplicate_status || 'unique'}</span>
              </div>
            </div>

            {/* Complete Collected Job Description */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Complete Collected Job Description</span>
                </span>
                <button
                  onClick={() => setShowRawDesc(!showRawDesc)}
                  className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 underline"
                >
                  {showRawDesc ? 'Show Formatted JD' : 'Show Unedited Raw Text'}
                </button>
              </div>

              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-200 leading-relaxed max-h-[300px] overflow-y-auto whitespace-pre-line font-sans">
                {showRawDesc 
                  ? (selectedJobForDetails.raw_description || selectedJobForDetails.description)
                  : selectedJobForDetails.description}
              </div>
            </div>

            {/* Responsibilities List */}
            {selectedJobForDetails.responsibilities && selectedJobForDetails.responsibilities.length > 0 && (
              <div className="space-y-2">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
                  Extracted Responsibilities
                </span>
                <ul className="list-disc list-inside space-y-1 text-xs text-slate-300 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                  {selectedJobForDetails.responsibilities.map((resp, i) => (
                    <li key={i}>{resp}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Requirements & Skills */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="space-y-1.5 p-3.5 bg-slate-950/60 rounded-xl border border-slate-800">
                <span className="font-bold text-slate-400 uppercase tracking-wider text-[11px]">Required Skills</span>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {selectedJobForDetails.required_skills.map((s, i) => (
                    <span key={i} className="text-[10px] bg-emerald-950/80 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-md font-mono">
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              <div className="space-y-1.5 p-3.5 bg-slate-950/60 rounded-xl border border-slate-800">
                <span className="font-bold text-slate-400 uppercase tracking-wider text-[11px]">Experience & Education</span>
                <p className="text-slate-300 pt-1">{selectedJobForDetails.experience_requirement}</p>
                <p className="text-slate-400 text-[11px]">{selectedJobForDetails.education_requirement}</p>
              </div>
            </div>

            {/* Phase 3: Fit Evaluation & Matching Breakdown */}
            {(() => {
              const fit = evaluateJobFit(selectedJobForDetails);
              return (
                <div className="p-4 bg-slate-950 rounded-xl border border-emerald-900/40 space-y-3 font-mono text-xs">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-emerald-400" />
                      <span className="font-bold text-white text-sm">
                        Match Score: <span className="text-emerald-400 font-extrabold">{fit.match_score}%</span>
                      </span>
                    </div>
                    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                      fit.recommendation === 'STRONG MATCH'
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                        : fit.recommendation === 'GOOD MATCH'
                        ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                        : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    }`}>
                      {fit.recommendation}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                    {/* Required Skills */}
                    <div className="space-y-1">
                      <span className="text-[11px] font-bold text-slate-400 block">Required Skills</span>
                      <div className="space-y-0.5">
                        {fit.required_skills.map((s, idx) => (
                          <div key={idx} className="flex items-center gap-1.5 text-emerald-300">
                            <span className="text-emerald-400 font-bold">✓</span>
                            <span>{s}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Relevant Experience */}
                    <div className="space-y-1">
                      <span className="text-[11px] font-bold text-slate-400 block">Relevant Experience</span>
                      <div className="space-y-0.5">
                        {fit.relevant_experience.map((e, idx) => (
                          <div key={idx} className="flex items-center gap-1.5 text-emerald-300">
                            <span className="text-emerald-400 font-bold">✓</span>
                            <span>{e}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800/80">
                    {/* Partial Matches */}
                    <div className="space-y-1">
                      <span className="text-[11px] font-bold text-slate-400 block">Partial</span>
                      <div className="space-y-0.5">
                        {fit.partial.map((p, idx) => (
                          <div key={idx} className="flex items-center gap-1.5 text-amber-300">
                            <span className="text-amber-400 font-bold">△</span>
                            <span>{p}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Missing Requirements */}
                    <div className="space-y-1">
                      <span className="text-[11px] font-bold text-slate-400 block">Missing</span>
                      <div className="space-y-0.5">
                        {fit.missing.map((m, idx) => (
                          <div key={idx} className="flex items-center gap-1.5 text-rose-300">
                            <span className="text-rose-400 font-bold">✗</span>
                            <span>{m}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-400">
                    <span className="text-slate-500 font-semibold uppercase">Recommendation: </span>
                    <span className="text-emerald-300 font-bold">{fit.recommendation}</span>
                  </div>
                </div>
              );
            })()}

            {/* Modal Bottom Actions */}
            <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                {selectedJobForDetails.source_url && (
                  <a
                    href={selectedJobForDetails.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition"
                  >
                    <ExternalLink className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Open Original Source</span>
                  </a>
                )}
                {selectedJobForDetails.status !== 'saved' ? (
                  <button
                    onClick={() => {
                      onUpdateJobStatus(selectedJobForDetails.id, 'saved');
                      setSelectedJobForDetails({ ...selectedJobForDetails, status: 'saved' });
                    }}
                    className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition"
                  >
                    Save Job
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      onUpdateJobStatus(selectedJobForDetails.id, 'discovered');
                      setSelectedJobForDetails({ ...selectedJobForDetails, status: 'discovered' });
                    }}
                    className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl border border-slate-700 transition"
                  >
                    Unsave
                  </button>
                )}
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setSelectedJobForDetails(null);
                    setShowRawDesc(false);
                  }}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl transition"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    onApplyJob(selectedJobForDetails.id);
                    setSelectedJobForDetails(null);
                  }}
                  className="flex items-center gap-1.5 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-xl shadow transition"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Track Application</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: TRIGGER JOB DISCOVERY RUN */}
      {showDiscoveryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-xl w-full shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
                  <Sparkles className="w-4 h-4" />
                </span>
                <h3 className="text-base font-bold text-white">Execute Job Discovery Run</h3>
              </div>
              <button
                onClick={() => setShowDiscoveryModal(false)}
                className="text-slate-400 hover:text-white p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Keywords Section */}
            <div className="space-y-2 text-xs">
              <label className="text-slate-300 font-semibold block">Target Role Keywords (Entry-Level)</label>
              <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto p-2 bg-slate-950 rounded-xl border border-slate-800">
                {discoveryKeywords.map((kw, idx) => (
                  <span
                    key={idx}
                    className="flex items-center gap-1 text-[11px] bg-slate-800 text-slate-200 px-2.5 py-1 rounded-lg"
                  >
                    <span>{kw}</span>
                    <button
                      onClick={() => handleRemoveKeyword(kw)}
                      className="text-slate-400 hover:text-rose-400 font-bold"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>

              {/* Add custom keyword */}
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="text"
                  placeholder="Add custom keyword (e.g. Django Developer)..."
                  value={customKeywordInput}
                  onChange={e => setCustomKeywordInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleAddKeyword()}
                  className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
                <button
                  onClick={handleAddKeyword}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg font-semibold text-xs border border-slate-700"
                >
                  Add
                </button>
              </div>
            </div>

            {/* Sources selection */}
            <div className="space-y-2 text-xs">
              <label className="text-slate-300 font-semibold block">Select Job Sources</label>
              <div className="grid grid-cols-2 gap-2">
                {DISCOVERY_SOURCES_LIST.map(src => {
                  const isSelected = selectedSources.includes(src.id);
                  return (
                    <button
                      key={src.id}
                      onClick={() => toggleSourceSelection(src.id)}
                      className={`flex items-center justify-between p-2.5 rounded-xl border text-left transition ${
                        isSelected
                          ? 'bg-emerald-950/40 border-emerald-600/60 text-white'
                          : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <div className="truncate">
                        <p className="font-semibold text-xs truncate">{src.name}</p>
                        <p className="text-[10px] text-slate-500 capitalize">{src.type.replace('_', ' ')}</p>
                      </div>
                      {isSelected && <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 ml-1" />}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Run Progress or Result display */}
            {isRunningDiscovery ? (
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2 text-center">
                <div className="flex items-center justify-center gap-2 text-xs text-emerald-400 font-semibold">
                  <RotateCw className="w-4 h-4 animate-spin text-emerald-400" />
                  <span>Crawling Lahore portals & running deduplication filters...</span>
                </div>
                <p className="text-[11px] text-slate-400">
                  Normalizing titles, extracting complete descriptions, and rejecting non-Lahore roles.
                </p>
              </div>
            ) : discoveryResult ? (
              <div className="p-4 bg-emerald-950/40 border border-emerald-800/80 rounded-xl space-y-2 text-xs">
                <div className="flex items-center gap-2 text-emerald-300 font-bold">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Discovery Run Complete!</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 font-mono text-[11px]">
                  <div className="p-2 bg-slate-950/80 rounded-lg">
                    <span className="text-slate-500 block">Total Raw</span>
                    <span className="text-white font-bold">{discoveryResult.total_discovered}</span>
                  </div>
                  <div className="p-2 bg-slate-950/80 rounded-lg">
                    <span className="text-slate-500 block">New Added</span>
                    <span className="text-emerald-400 font-bold">{discoveryResult.new_jobs_added}</span>
                  </div>
                  <div className="p-2 bg-slate-950/80 rounded-lg">
                    <span className="text-slate-500 block">Dupes Skipped</span>
                    <span className="text-amber-400 font-bold">{discoveryResult.duplicates_skipped}</span>
                  </div>
                  <div className="p-2 bg-slate-950/80 rounded-lg">
                    <span className="text-slate-500 block">Filtered</span>
                    <span className="text-slate-400 font-bold">
                      {discoveryResult.rejected_non_lahore + discoveryResult.rejected_non_entry}
                    </span>
                  </div>
                </div>
              </div>
            ) : null}

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
              <button
                onClick={() => setShowDiscoveryModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl transition"
              >
                Close
              </button>
              <button
                disabled={isRunningDiscovery || selectedSources.length === 0}
                onClick={handleExecuteDiscovery}
                className="flex items-center gap-1.5 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 text-xs font-bold rounded-xl shadow transition"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Start Discovery Run</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: DISCOVERY RUNS HISTORY & AUDIT METRICS */}
      {showRunsHistoryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-2xl w-full shadow-2xl space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
                  <Activity className="w-4 h-4" />
                </span>
                <h3 className="text-base font-bold text-white">Discovery Runs Audit History</h3>
              </div>
              <button onClick={() => setShowRunsHistoryModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              {discoveryRunsHistory.map(run => (
                <div key={run.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-emerald-400 font-bold">{run.id}</span>
                    <span className="text-[11px] text-slate-400">
                      {new Date(run.triggered_at).toLocaleString()}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-[11px]">
                    <div className="p-2 bg-slate-900 rounded-lg">
                      <span className="text-slate-500 block">Total Discovered</span>
                      <span className="text-white font-bold">{run.total_discovered}</span>
                    </div>
                    <div className="p-2 bg-slate-900 rounded-lg">
                      <span className="text-slate-500 block">New Added</span>
                      <span className="text-emerald-400 font-bold">{run.new_jobs_added}</span>
                    </div>
                    <div className="p-2 bg-slate-900 rounded-lg">
                      <span className="text-slate-500 block">Duplicates Filtered</span>
                      <span className="text-amber-400 font-bold">{run.duplicates_skipped}</span>
                    </div>
                    <div className="p-2 bg-slate-900 rounded-lg">
                      <span className="text-slate-500 block">Non-Lahore / Non-Entry</span>
                      <span className="text-rose-400 font-bold">
                        {run.rejected_non_lahore + run.rejected_non_entry}
                      </span>
                    </div>
                  </div>

                  <div className="text-[11px] text-slate-400 pt-1">
                    <span className="text-slate-500">Sources Checked: </span>
                    {run.sources_checked.join(', ')}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowRunsHistoryModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 4: MANUAL ADD JOB OPENING */}
      {showAddJobModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white">Add Job Opening (Lahore)</h3>
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Company Name *</label>
                  <input
                    type="text"
                    placeholder="e.g. Systems Limited, Arbisoft"
                    value={newJobForm.company}
                    onChange={e => setNewJobForm({ ...newJobForm, company: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Job Title *</label>
                  <input
                    type="text"
                    placeholder="e.g. Associate Software Engineer"
                    value={newJobForm.job_title}
                    onChange={e => setNewJobForm({ ...newJobForm, job_title: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Location</label>
                  <input
                    type="text"
                    value={newJobForm.location}
                    onChange={e => setNewJobForm({ ...newJobForm, location: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Job Type</label>
                  <select
                    value={newJobForm.job_type}
                    onChange={e => setNewJobForm({ ...newJobForm, job_type: e.target.value as any })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="Full-time">Full-time</option>
                    <option value="Hybrid">Hybrid</option>
                    <option value="Internship">Internship</option>
                    <option value="Remote">Remote</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Original Source URL</label>
                <input
                  type="url"
                  placeholder="https://..."
                  value={newJobForm.job_url}
                  onChange={e => setNewJobForm({ ...newJobForm, job_url: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Complete Job Description *</label>
                <textarea
                  rows={4}
                  placeholder="Paste complete collected job description..."
                  value={newJobForm.description}
                  onChange={e => setNewJobForm({ ...newJobForm, description: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Required Skills (comma separated)</label>
                  <input
                    type="text"
                    placeholder="Python, SQL, FastAPI, Git"
                    value={newJobForm.required_skills}
                    onChange={e => setNewJobForm({ ...newJobForm, required_skills: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Salary Range</label>
                  <input
                    type="text"
                    placeholder="PKR 100,000 - 140,000 / month"
                    value={newJobForm.salary}
                    onChange={e => setNewJobForm({ ...newJobForm, salary: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
              <button
                onClick={() => setShowAddJobModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleManualAddJob}
                className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg transition"
              >
                Save Job
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
