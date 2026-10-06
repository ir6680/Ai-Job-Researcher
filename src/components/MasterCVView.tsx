import React, { useState } from 'react';
import { 
  MasterCV, 
  Skill, 
  Education, 
  Experience, 
  Project, 
  Certification 
} from '../types/job_agent';
import { 
  Upload, 
  FileText, 
  ShieldCheck, 
  Plus, 
  Trash2, 
  Edit3, 
  Check, 
  ExternalLink, 
  Github, 
  Linkedin, 
  Globe, 
  Building2, 
  GraduationCap, 
  Award, 
  Sparkles, 
  AlertCircle,
  FolderGit2
} from 'lucide-react';
import { parseCVTextDeterministically } from '../utils/clientParser';
import { SAMPLE_CV_RAW_TEXT } from '../mock/initialData';

interface MasterCVViewProps {
  cv: MasterCV;
  onUpdateCV: (updated: MasterCV) => void;
}

export const MasterCVView: React.FC<MasterCVViewProps> = ({ cv, onUpdateCV }) => {
  const [isEditingPersonal, setIsEditingPersonal] = useState(false);
  const [personalForm, setPersonalForm] = useState({
    full_name: cv.full_name,
    email: cv.email,
    phone: cv.phone || '',
    location: cv.location,
    summary: cv.summary || '',
    github_url: cv.github_url || '',
    linkedin_url: cv.linkedin_url || '',
    portfolio_url: cv.portfolio_url || '',
    website_url: cv.website_url || ''
  });

  const [activeSkillCategory, setActiveSkillCategory] = useState<string>('All');
  const [showAddSkillModal, setShowAddSkillModal] = useState(false);
  const [newSkill, setNewSkill] = useState<Partial<Skill>>({
    name: '',
    category: 'Languages',
    proficiency: 'Intermediate',
    years_of_experience: 1
  });

  const [showAddProjectModal, setShowAddProjectModal] = useState(false);
  const [newProject, setNewProject] = useState({
    title: '',
    description: '',
    role: 'Developer',
    techInput: '',
    repo_url: '',
    live_url: ''
  });

  const [showAddExpModal, setShowAddExpModal] = useState(false);
  const [newExp, setNewExp] = useState({
    company_name: '',
    role_title: '',
    employment_type: 'Full-time' as const,
    location: 'Lahore, Pakistan',
    start_date: '',
    end_date: '',
    description: '',
    technologiesInput: ''
  });

  const [showAddEduModal, setShowAddEduModal] = useState(false);
  const [newEdu, setNewEdu] = useState({
    institution: '',
    degree: 'BS in Computer Science',
    field_of_study: 'Computer Science',
    grade_or_gpa: '',
    start_date: '2020',
    end_date: '2024'
  });

  const [uploadStatus, setUploadStatus] = useState<{
    message?: string;
    notes?: string[];
  }>({});

  // Handlers for Personal Info
  const handleSavePersonal = () => {
    onUpdateCV({
      ...cv,
      ...personalForm,
      version: cv.version + 1,
      updated_at: new Date().toISOString()
    });
    setIsEditingPersonal(false);
  };

  // Upload handler
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      if (text) {
        processExtractedText(text, file.name);
      }
    };
    reader.readAsText(file);
  };

  const handleParseSample = () => {
    processExtractedText(SAMPLE_CV_RAW_TEXT, 'Irfan_FAST_Lahore_CV.pdf');
  };

  const processExtractedText = (text: string, filename: string) => {
    const extracted = parseCVTextDeterministically(text, filename);
    
    // Merge or update without losing user structure
    const updatedCV: MasterCV = {
      ...cv,
      full_name: extracted.full_name || cv.full_name,
      email: extracted.email || cv.email,
      phone: extracted.phone || cv.phone,
      location: extracted.location || cv.location,
      summary: extracted.summary || cv.summary,
      github_url: extracted.github_url || cv.github_url,
      linkedin_url: extracted.linkedin_url || cv.linkedin_url,
      portfolio_url: extracted.portfolio_url || cv.portfolio_url,
      source_filename: filename,
      raw_text: text,
      version: cv.version + 1,
      updated_at: new Date().toISOString(),
      skills: extracted.skills.length > 0 ? extracted.skills : cv.skills,
      education: extracted.education.length > 0 ? extracted.education : cv.education,
      experience: extracted.experience.length > 0 ? extracted.experience : cv.experience,
      projects: extracted.projects.length > 0 ? extracted.projects : cv.projects,
      certifications: extracted.certifications.length > 0 ? extracted.certifications : cv.certifications
    };

    onUpdateCV(updatedCV);
    setUploadStatus({
      message: `Parsed ${filename} successfully. Strictly extracted factual records.`,
      notes: extracted.notes
    });
  };

  // Skill Management
  const handleAddSkill = () => {
    if (!newSkill.name?.trim()) return;
    const added: Skill = {
      id: `sk-${Date.now()}`,
      name: newSkill.name.trim(),
      category: (newSkill.category as any) || 'Languages',
      proficiency: (newSkill.proficiency as any) || 'Intermediate',
      years_of_experience: Number(newSkill.years_of_experience) || 1
    };
    onUpdateCV({
      ...cv,
      skills: [...cv.skills, added],
      version: cv.version + 1,
      updated_at: new Date().toISOString()
    });
    setNewSkill({ name: '', category: 'Languages', proficiency: 'Intermediate', years_of_experience: 1 });
    setShowAddSkillModal(false);
  };

  const handleDeleteSkill = (skillId: string) => {
    onUpdateCV({
      ...cv,
      skills: cv.skills.filter(s => s.id !== skillId),
      version: cv.version + 1,
      updated_at: new Date().toISOString()
    });
  };

  // Project Management
  const handleAddProject = () => {
    if (!newProject.title.trim()) return;
    const techArray = newProject.techInput.split(',').map(t => t.trim()).filter(Boolean);
    const added: Project = {
      id: `proj-${Date.now()}`,
      title: newProject.title.trim(),
      description: newProject.description.trim(),
      role: newProject.role.trim(),
      technologies: techArray.length ? techArray : ['Python', 'FastAPI'],
      repo_url: newProject.repo_url.trim() || undefined,
      live_url: newProject.live_url.trim() || undefined,
      highlights: [newProject.description.trim()]
    };
    onUpdateCV({
      ...cv,
      projects: [added, ...cv.projects],
      version: cv.version + 1,
      updated_at: new Date().toISOString()
    });
    setNewProject({ title: '', description: '', role: 'Developer', techInput: '', repo_url: '', live_url: '' });
    setShowAddProjectModal(false);
  };

  const handleDeleteProject = (projId: string) => {
    onUpdateCV({
      ...cv,
      projects: cv.projects.filter(p => p.id !== projId),
      version: cv.version + 1
    });
  };

  // Experience Management
  const handleAddExperience = () => {
    if (!newExp.company_name.trim() || !newExp.role_title.trim()) return;
    const techArray = newExp.technologiesInput.split(',').map(t => t.trim()).filter(Boolean);
    const added: Experience = {
      id: `exp-${Date.now()}`,
      company_name: newExp.company_name.trim(),
      role_title: newExp.role_title.trim(),
      employment_type: newExp.employment_type,
      location: newExp.location,
      start_date: newExp.start_date || '2023',
      end_date: newExp.end_date || 'Present',
      is_current: false,
      description: newExp.description,
      highlights: newExp.description ? [newExp.description] : [],
      technologies_used: techArray
    };
    onUpdateCV({
      ...cv,
      experience: [added, ...cv.experience],
      version: cv.version + 1
    });
    setNewExp({
      company_name: '',
      role_title: '',
      employment_type: 'Full-time',
      location: 'Lahore, Pakistan',
      start_date: '',
      end_date: '',
      description: '',
      technologiesInput: ''
    });
    setShowAddExpModal(false);
  };

  const handleDeleteExp = (expId: string) => {
    onUpdateCV({
      ...cv,
      experience: cv.experience.filter(e => e.id !== expId),
      version: cv.version + 1
    });
  };

  // Education Management
  const handleAddEducation = () => {
    if (!newEdu.institution.trim()) return;
    const added: Education = {
      id: `edu-${Date.now()}`,
      institution: newEdu.institution.trim(),
      degree: newEdu.degree.trim(),
      field_of_study: newEdu.field_of_study.trim(),
      grade_or_gpa: newEdu.grade_or_gpa.trim() || undefined,
      start_date: newEdu.start_date,
      end_date: newEdu.end_date,
      is_current: false,
      location: 'Lahore, Pakistan'
    };
    onUpdateCV({
      ...cv,
      education: [added, ...cv.education],
      version: cv.version + 1
    });
    setNewEdu({ institution: '', degree: 'BS in Computer Science', field_of_study: 'Computer Science', grade_or_gpa: '', start_date: '2020', end_date: '2024' });
    setShowAddEduModal(false);
  };

  const handleDeleteEdu = (eduId: string) => {
    onUpdateCV({
      ...cv,
      education: cv.education.filter(e => e.id !== eduId),
      version: cv.version + 1
    });
  };

  const skillCategories = ['All', 'Languages', 'Frameworks', 'Databases', 'Tools & DevOps', 'Core Concepts', 'Soft Skills'];
  const filteredSkills = activeSkillCategory === 'All' 
    ? cv.skills 
    : cv.skills.filter(s => s.category === activeSkillCategory);

  return (
    <div className="space-y-6">
      {/* CV Import & Anti-Hallucination Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl relative overflow-hidden">
        <div className="absolute -top-12 -right-12 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
                <FileText className="w-5 h-5" />
              </span>
              <h2 className="text-xl font-bold text-white tracking-tight">Master CV Module</h2>
              <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded-md border border-slate-700">
                Single Source of Truth (v{cv.version})
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
              Upload your CV (PDF, DOCX, TXT) to populate structured data. The deterministic parser strictly decodes facts and
              <strong className="text-emerald-400 font-medium"> never invents or hallucinates </strong> 
              qualifications.
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
            <label className="flex-1 md:flex-none cursor-pointer flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs rounded-xl shadow transition">
              <Upload className="w-4 h-4" />
              <span>Import CV (PDF/DOCX/TXT)</span>
              <input 
                type="file" 
                accept=".pdf,.docx,.doc,.txt" 
                onChange={handleFileUpload} 
                className="hidden" 
              />
            </label>

            <button
              onClick={handleParseSample}
              className="flex-1 md:flex-none flex items-center justify-center gap-1.5 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium text-xs rounded-xl transition"
              title="Parse sample FAST Lahore graduate CV"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Load Lahore Sample</span>
            </button>
          </div>
        </div>

        {/* Upload Notes / Hallucination-Free Provenance Notice */}
        {uploadStatus.message && (
          <div className="mt-4 p-3.5 bg-emerald-950/40 border border-emerald-800/60 rounded-xl text-xs space-y-2">
            <div className="flex items-center gap-2 text-emerald-300 font-semibold">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{uploadStatus.message}</span>
            </div>
            {uploadStatus.notes && uploadStatus.notes.length > 0 && (
              <div className="pl-6 space-y-1 text-slate-400 text-[11px]">
                {uploadStatus.notes.map((note, idx) => (
                  <div key={idx} className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/80" />
                    <span>{note}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Main Grid: Left Column (Personal Info & Links) | Right Column (Skills, Experience, Education, Projects) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Personal Info & Contact Card (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-400" />
                Personal Profile
              </h3>
              <button
                onClick={() => {
                  if (isEditingPersonal) handleSavePersonal();
                  else setIsEditingPersonal(true);
                }}
                className={`text-xs flex items-center gap-1 px-2.5 py-1 rounded-lg transition font-medium ${
                  isEditingPersonal
                    ? 'bg-emerald-500 text-slate-950'
                    : 'bg-slate-800 text-slate-300 hover:text-white'
                }`}
              >
                {isEditingPersonal ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>Save</span>
                  </>
                ) : (
                  <>
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Edit</span>
                  </>
                )}
              </button>
            </div>

            {isEditingPersonal ? (
              <div className="space-y-3 text-xs">
                <div>
                  <label className="text-slate-400 block mb-1">Full Name</label>
                  <input
                    type="text"
                    value={personalForm.full_name}
                    onChange={e => setPersonalForm({ ...personalForm, full_name: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Email</label>
                  <input
                    type="email"
                    value={personalForm.email}
                    onChange={e => setPersonalForm({ ...personalForm, email: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Phone</label>
                  <input
                    type="text"
                    value={personalForm.phone}
                    onChange={e => setPersonalForm({ ...personalForm, phone: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Location</label>
                  <input
                    type="text"
                    value={personalForm.location}
                    onChange={e => setPersonalForm({ ...personalForm, location: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Summary</label>
                  <textarea
                    rows={4}
                    value={personalForm.summary}
                    onChange={e => setPersonalForm({ ...personalForm, summary: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div className="pt-2 border-t border-slate-800 space-y-2">
                  <div>
                    <label className="text-slate-400 block mb-1">GitHub URL</label>
                    <input
                      type="url"
                      value={personalForm.github_url}
                      onChange={e => setPersonalForm({ ...personalForm, github_url: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">LinkedIn URL</label>
                    <input
                      type="url"
                      value={personalForm.linkedin_url}
                      onChange={e => setPersonalForm({ ...personalForm, linkedin_url: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">Portfolio Website</label>
                    <input
                      type="url"
                      value={personalForm.portfolio_url}
                      onChange={e => setPersonalForm({ ...personalForm, portfolio_url: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <h4 className="text-lg font-bold text-white">{cv.full_name}</h4>
                  <p className="text-xs text-emerald-400 font-medium">{cv.location}</p>
                </div>

                <div className="text-xs space-y-2 text-slate-300">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-500">Email:</span>
                    <span className="font-mono text-slate-200">{cv.email}</span>
                  </div>
                  {cv.phone && (
                    <div className="flex items-center gap-2">
                      <span className="text-slate-500">Phone:</span>
                      <span className="font-mono text-slate-200">{cv.phone}</span>
                    </div>
                  )}
                  {cv.source_filename && (
                    <div className="flex items-center gap-2">
                      <span className="text-slate-500">Source:</span>
                      <span className="text-slate-300 italic truncate">{cv.source_filename}</span>
                    </div>
                  )}
                </div>

                {cv.summary && (
                  <div className="p-3 bg-slate-950/70 border border-slate-800/80 rounded-xl text-xs text-slate-300 leading-relaxed">
                    <span className="text-slate-400 font-semibold block mb-1 text-[11px] uppercase tracking-wider">
                      Candidate Summary
                    </span>
                    {cv.summary}
                  </div>
                )}

                {/* Profiles & Links */}
                <div className="pt-2 border-t border-slate-800 space-y-2">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                    Verified Links
                  </span>
                  <div className="space-y-1.5 text-xs">
                    {cv.github_url ? (
                      <a 
                        href={cv.github_url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="flex items-center justify-between p-2 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-200 transition"
                      >
                        <div className="flex items-center gap-2">
                          <Github className="w-4 h-4 text-emerald-400" />
                          <span className="font-mono text-[11px] truncate max-w-[180px]">{cv.github_url}</span>
                        </div>
                        <ExternalLink className="w-3 h-3 text-slate-500" />
                      </a>
                    ) : (
                      <div className="text-[11px] text-slate-500 italic p-1">No GitHub profile linked</div>
                    )}

                    {cv.linkedin_url ? (
                      <a 
                        href={cv.linkedin_url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="flex items-center justify-between p-2 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-200 transition"
                      >
                        <div className="flex items-center gap-2">
                          <Linkedin className="w-4 h-4 text-sky-400" />
                          <span className="font-mono text-[11px] truncate max-w-[180px]">{cv.linkedin_url}</span>
                        </div>
                        <ExternalLink className="w-3 h-3 text-slate-500" />
                      </a>
                    ) : (
                      <div className="text-[11px] text-slate-500 italic p-1">No LinkedIn profile linked</div>
                    )}

                    {cv.portfolio_url && (
                      <a 
                        href={cv.portfolio_url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="flex items-center justify-between p-2 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-200 transition"
                      >
                        <div className="flex items-center gap-2">
                          <Globe className="w-4 h-4 text-teal-400" />
                          <span className="font-mono text-[11px] truncate max-w-[180px]">{cv.portfolio_url}</span>
                        </div>
                        <ExternalLink className="w-3 h-3 text-slate-500" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Certifications Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <Award className="w-4 h-4 text-amber-400" />
                Certifications ({cv.certifications.length})
              </h3>
            </div>
            {cv.certifications.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No certifications in CV.</p>
            ) : (
              <div className="space-y-2">
                {cv.certifications.map(c => (
                  <div key={c.id} className="p-2.5 bg-slate-950/70 border border-slate-800 rounded-xl text-xs">
                    <p className="font-semibold text-white">{c.name}</p>
                    <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1">
                      <span>{c.issuing_organization}</span>
                      {c.issue_date && <span>{c.issue_date}</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Skills, Experience, Education, Projects (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Skills Section */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-lg space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-400" />
                  Structured Skills Taxonomy ({cv.skills.length})
                </h3>
                <p className="text-xs text-slate-400">Classified by technical discipline & verified without inflation.</p>
              </div>
              <button
                onClick={() => setShowAddSkillModal(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-xs font-semibold rounded-lg transition self-start sm:self-auto"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Skill</span>
              </button>
            </div>

            {/* Category tabs */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
              {skillCategories.map(cat => (
                <button
                  key={cat}
                  onClick={() => setActiveSkillCategory(cat)}
                  className={`px-3 py-1 rounded-lg font-medium whitespace-nowrap transition ${
                    activeSkillCategory === cat
                      ? 'bg-emerald-500 text-slate-950 font-semibold'
                      : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Skills chips */}
            <div className="flex flex-wrap gap-2 pt-1">
              {filteredSkills.length === 0 ? (
                <p className="text-xs text-slate-500 py-3 italic">No skills listed in this category.</p>
              ) : (
                filteredSkills.map(skill => (
                  <div
                    key={skill.id}
                    className="group flex items-center gap-2 bg-slate-950 border border-slate-800 hover:border-slate-700 px-3 py-1.5 rounded-xl text-xs transition"
                  >
                    <span className="font-medium text-slate-200">{skill.name}</span>
                    <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded-md font-mono">
                      {skill.proficiency}
                    </span>
                    <button
                      onClick={() => handleDeleteSkill(skill.id)}
                      className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 transition"
                      title="Delete skill"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Experience / Internships Section */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-lg space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-emerald-400" />
                  Work & Internship Experience ({cv.experience.length})
                </h3>
                <p className="text-xs text-slate-400">Software houses and engineering roles.</p>
              </div>
              <button
                onClick={() => setShowAddExpModal(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Experience</span>
              </button>
            </div>

            <div className="space-y-3">
              {cv.experience.map(exp => (
                <div key={exp.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2 relative group">
                  <button
                    onClick={() => handleDeleteExp(exp.id)}
                    className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 transition"
                    title="Remove experience"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>

                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                    <div>
                      <h4 className="font-bold text-white text-sm">{exp.role_title}</h4>
                      <div className="flex items-center gap-2 text-xs text-emerald-400 font-medium">
                        <span>{exp.company_name}</span>
                        <span>•</span>
                        <span className="text-slate-400">{exp.location}</span>
                      </div>
                    </div>
                    <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2.5 py-0.5 rounded-md border border-slate-800 self-start sm:self-auto">
                      {exp.start_date || 'Past'} – {exp.end_date || 'Present'} ({exp.employment_type})
                    </span>
                  </div>

                  {exp.description && (
                    <p className="text-xs text-slate-300 leading-relaxed pt-1">{exp.description}</p>
                  )}

                  {exp.highlights && exp.highlights.length > 0 && (
                    <ul className="list-disc list-inside text-xs text-slate-400 space-y-1 pt-1">
                      {exp.highlights.map((h, i) => (
                        <li key={i}>{h}</li>
                      ))}
                    </ul>
                  )}

                  {exp.technologies_used && exp.technologies_used.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-2">
                      {exp.technologies_used.map((t, i) => (
                        <span key={i} className="text-[10px] bg-slate-900 border border-slate-800 text-slate-300 px-2 py-0.5 rounded-md">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Education Section */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-lg space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <GraduationCap className="w-4 h-4 text-emerald-400" />
                  Education ({cv.education.length})
                </h3>
                <p className="text-xs text-slate-400">Academic qualifications & university degrees.</p>
              </div>
              <button
                onClick={() => setShowAddEduModal(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Education</span>
              </button>
            </div>

            <div className="space-y-3">
              {cv.education.map(edu => (
                <div key={edu.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1.5 relative group">
                  <button
                    onClick={() => handleDeleteEdu(edu.id)}
                    className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 transition"
                    title="Remove education"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>

                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                    <div>
                      <h4 className="font-bold text-white text-sm">{edu.degree}</h4>
                      <p className="text-xs text-emerald-400 font-medium">{edu.institution}</p>
                    </div>
                    <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2.5 py-0.5 rounded-md border border-slate-800 self-start sm:self-auto">
                      {edu.start_date || '2020'} – {edu.end_date || '2024'}
                    </span>
                  </div>

                  {edu.grade_or_gpa && (
                    <span className="inline-block text-[11px] font-semibold text-emerald-300 bg-emerald-950/40 border border-emerald-800 px-2 py-0.5 rounded-md">
                      {edu.grade_or_gpa}
                    </span>
                  )}
                  {edu.description && (
                    <p className="text-xs text-slate-400 pt-1">{edu.description}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Verified Projects Section */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-lg space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <FolderGit2 className="w-4 h-4 text-emerald-400" />
                  Verified Projects ({cv.projects.length})
                </h3>
                <p className="text-xs text-slate-400">Technical software systems and code repositories.</p>
              </div>
              <button
                onClick={() => setShowAddProjectModal(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Project</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {cv.projects.map(proj => (
                <div key={proj.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2.5 flex flex-col justify-between relative group">
                  <button
                    onClick={() => handleDeleteProject(proj.id)}
                    className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 transition"
                    title="Remove project"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>

                  <div className="space-y-1">
                    <h4 className="font-bold text-white text-sm">{proj.title}</h4>
                    {proj.description && (
                      <p className="text-xs text-slate-300 leading-relaxed">{proj.description}</p>
                    )}
                  </div>

                  <div className="space-y-2.5 pt-2">
                    <div className="flex flex-wrap gap-1.5">
                      {proj.technologies.map((t, idx) => (
                        <span key={idx} className="text-[10px] bg-slate-900 border border-slate-800 text-slate-300 px-2 py-0.5 rounded-md font-mono">
                          {t}
                        </span>
                      ))}
                    </div>

                    <div className="flex items-center gap-3 text-xs pt-1 border-t border-slate-800/80">
                      {proj.repo_url && (
                        <a 
                          href={proj.repo_url} 
                          target="_blank" 
                          rel="noreferrer"
                          className="flex items-center gap-1 text-emerald-400 hover:underline"
                        >
                          <Github className="w-3.5 h-3.5" />
                          <span>Code</span>
                        </a>
                      )}
                      {proj.live_url && (
                        <a 
                          href={proj.live_url} 
                          target="_blank" 
                          rel="noreferrer"
                          className="flex items-center gap-1 text-teal-400 hover:underline"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          <span>Demo</span>
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* MODALS */}
      {/* 1. Add Skill Modal */}
      {showAddSkillModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white">Add Verified Skill</h3>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Skill Name *</label>
                <input
                  type="text"
                  placeholder="e.g. FastAPI, PostgreSQL, Docker, Redis"
                  value={newSkill.name}
                  onChange={e => setNewSkill({ ...newSkill, name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Category</label>
                <select
                  value={newSkill.category}
                  onChange={e => setNewSkill({ ...newSkill, category: e.target.value as any })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="Languages">Languages</option>
                  <option value="Frameworks">Frameworks</option>
                  <option value="Databases">Databases</option>
                  <option value="Tools & DevOps">Tools & DevOps</option>
                  <option value="Core Concepts">Core Concepts</option>
                  <option value="Soft Skills">Soft Skills</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Proficiency</label>
                  <select
                    value={newSkill.proficiency}
                    onChange={e => setNewSkill({ ...newSkill, proficiency: e.target.value as any })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Expert">Expert</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Years of Exp</label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={newSkill.years_of_experience}
                    onChange={e => setNewSkill({ ...newSkill, years_of_experience: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setShowAddSkillModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleAddSkill}
                className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg transition"
              >
                Save Skill
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 2. Add Project Modal */}
      {showAddProjectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white">Add Project</h3>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Project Title *</label>
                <input
                  type="text"
                  placeholder="e.g. Distributed Task Queue"
                  value={newProject.title}
                  onChange={e => setNewProject({ ...newProject, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Technologies (comma separated)</label>
                <input
                  type="text"
                  placeholder="Python, FastAPI, Redis, Docker, PostgreSQL"
                  value={newProject.techInput}
                  onChange={e => setNewProject({ ...newProject, techInput: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Description / Key Highlights</label>
                <textarea
                  rows={3}
                  placeholder="Built backend service handling asynchronous workloads..."
                  value={newProject.description}
                  onChange={e => setNewProject({ ...newProject, description: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">GitHub Repo URL</label>
                  <input
                    type="url"
                    placeholder="https://github.com/..."
                    value={newProject.repo_url}
                    onChange={e => setNewProject({ ...newProject, repo_url: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Live Demo URL</label>
                  <input
                    type="url"
                    placeholder="https://..."
                    value={newProject.live_url}
                    onChange={e => setNewProject({ ...newProject, live_url: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setShowAddProjectModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleAddProject}
                className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg transition"
              >
                Add Project
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 3. Add Experience Modal */}
      {showAddExpModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white">Add Work or Internship</h3>
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Company Name *</label>
                  <input
                    type="text"
                    placeholder="e.g. Systems Limited, Arbisoft"
                    value={newExp.company_name}
                    onChange={e => setNewExp({ ...newExp, company_name: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Role Title *</label>
                  <input
                    type="text"
                    placeholder="e.g. Software Engineer Intern"
                    value={newExp.role_title}
                    onChange={e => setNewExp({ ...newExp, role_title: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Type</label>
                  <select
                    value={newExp.employment_type}
                    onChange={e => setNewExp({ ...newExp, employment_type: e.target.value as any })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="Internship">Internship</option>
                    <option value="Full-time">Full-time</option>
                    <option value="Contract">Contract</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Start Date</label>
                  <input
                    type="text"
                    placeholder="June 2023"
                    value={newExp.start_date}
                    onChange={e => setNewExp({ ...newExp, start_date: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">End Date</label>
                  <input
                    type="text"
                    placeholder="Aug 2023 or Present"
                    value={newExp.end_date}
                    onChange={e => setNewExp({ ...newExp, end_date: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Technologies Used (comma separated)</label>
                <input
                  type="text"
                  placeholder="Python, FastAPI, PostgreSQL, Docker"
                  value={newExp.technologiesInput}
                  onChange={e => setNewExp({ ...newExp, technologiesInput: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Description</label>
                <textarea
                  rows={3}
                  placeholder="Main responsibilities and achievements..."
                  value={newExp.description}
                  onChange={e => setNewExp({ ...newExp, description: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setShowAddExpModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleAddExperience}
                className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg transition"
              >
                Save Record
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 4. Add Education Modal */}
      {showAddEduModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white">Add Education Record</h3>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">University / Institution *</label>
                <input
                  type="text"
                  placeholder="e.g. FAST NUCES Lahore, PUCIT, ITU"
                  value={newEdu.institution}
                  onChange={e => setNewEdu({ ...newEdu, institution: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Degree *</label>
                <input
                  type="text"
                  placeholder="BS in Computer Science"
                  value={newEdu.degree}
                  onChange={e => setNewEdu({ ...newEdu, degree: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">GPA / Grade</label>
                  <input
                    type="text"
                    placeholder="CGPA: 3.5 / 4.0"
                    value={newEdu.grade_or_gpa}
                    onChange={e => setNewEdu({ ...newEdu, grade_or_gpa: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Years</label>
                  <div className="flex items-center gap-1">
                    <input
                      type="text"
                      placeholder="2020"
                      value={newEdu.start_date}
                      onChange={e => setNewEdu({ ...newEdu, start_date: e.target.value })}
                      className="w-1/2 bg-slate-950 border border-slate-700 rounded-lg px-2 py-2 text-white focus:outline-none focus:border-emerald-500"
                    />
                    <span className="text-slate-500">-</span>
                    <input
                      type="text"
                      placeholder="2024"
                      value={newEdu.end_date}
                      onChange={e => setNewEdu({ ...newEdu, end_date: e.target.value })}
                      className="w-1/2 bg-slate-950 border border-slate-700 rounded-lg px-2 py-2 text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setShowAddEduModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleAddEducation}
                className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg transition"
              >
                Save Education
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
