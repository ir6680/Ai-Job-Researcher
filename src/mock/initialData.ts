import { MasterCV, Job, Application, JobDiscoveryRun, JobDiscoverySourceInfo } from '../types/job_agent';

export const SAMPLE_CV_RAW_TEXT = `MUHAMMAD IRFAN
Email: irfan.rajpoot@example.com | Phone: +92 300 9876543
Location: Lahore, Pakistan
LinkedIn: https://linkedin.com/in/irfan-rajpoot
GitHub: https://github.com/irfanrajpoot
Portfolio: https://irfanrajpoot.dev

PROFESSIONAL SUMMARY
Motivated Computer Science graduate from FAST NUCES Lahore seeking an entry-level Software Engineer / Python Backend role. Proficient in Python, FastAPI, Django, PostgreSQL, and modern REST API architectures. Dedicated to clean code, test-driven development, and algorithmic efficiency.

EDUCATION
FAST National University of Computer and Emerging Sciences, Lahore
BS in Computer Science (2020 - 2024)
CGPA: 3.52 / 4.00
Relevant Coursework: Data Structures & Algorithms, Database Systems, Object-Oriented Programming, Web Engineering, Operating Systems.

TECHNICAL SKILLS
Languages: Python, TypeScript, JavaScript, SQL, C++, HTML5, CSS3
Frameworks: FastAPI, Django, React, Express, Tailwind CSS
Databases: PostgreSQL, MySQL, Redis, SQLite
Tools & DevOps: Docker, Git, GitHub Actions, Linux, Postman, VS Code
Core Concepts: REST APIs, Microservices, System Design, Unit Testing, OOP

EXPERIENCE / INTERNSHIPS
Systems Limited, Lahore
Software Engineer Intern (June 2023 - August 2023)
- Built automated microservice endpoints using Python and FastAPI, reducing internal data query latency by 28%.
- Integrated PostgreSQL database models with SQLAlchemy ORM and conducted schema migrations.
- Authored unit test suites using PyTest, achieving over 85% code coverage.

ACADEMIC & PERSONAL PROJECTS
AI Job Application Assistant
- Engineered a full-stack job application tracker with FastAPI, PostgreSQL, and React.
- Built an extraction engine parsing PDF/DOCX resumes deterministically without factual hallucinations.
- GitHub: https://github.com/irfanrajpoot/ai-job-agent

E-Commerce Distributed Inventory API
- Developed robust REST APIs in Python/Django with PostgreSQL and Redis caching.
- Implemented JWT authentication and transactional inventory reservations.

CERTIFICATIONS
- Meta Backend Developer Professional Certificate (Coursera, 2023)
- AWS Certified Cloud Practitioner (2024)`;

export const INITIAL_MASTER_CV: MasterCV = {
  id: "mcv-001",
  user_id: "user-001",
  full_name: "Muhammad Irfan",
  email: "irfan.rajpoot@example.com",
  phone: "+92 300 9876543",
  location: "Lahore, Pakistan",
  summary: "Motivated Computer Science graduate from FAST NUCES Lahore seeking an entry-level Software Engineer / Python Backend role in Lahore software houses. Proficient in Python, FastAPI, PostgreSQL, and modern REST API architectures.",
  github_url: "https://github.com/irfanrajpoot",
  linkedin_url: "https://linkedin.com/in/irfan-rajpoot",
  portfolio_url: "https://irfanrajpoot.dev",
  website_url: "https://irfanrajpoot.dev",
  version: 1,
  is_primary: true,
  source_filename: "Irfan_Rajpoot_Resume.pdf",
  raw_text: SAMPLE_CV_RAW_TEXT,
  created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
  updated_at: new Date().toISOString(),
  skills: [
    { id: "sk-1", name: "Python", category: "Languages", proficiency: "Expert", years_of_experience: 2 },
    { id: "sk-2", name: "FastAPI", category: "Frameworks", proficiency: "Expert", years_of_experience: 1.5 },
    { id: "sk-3", name: "PostgreSQL", category: "Databases", proficiency: "Intermediate", years_of_experience: 2 },
    { id: "sk-4", name: "Django", category: "Frameworks", proficiency: "Intermediate", years_of_experience: 1 },
    { id: "sk-5", name: "TypeScript", category: "Languages", proficiency: "Intermediate", years_of_experience: 1 },
    { id: "sk-6", name: "React", category: "Frameworks", proficiency: "Intermediate", years_of_experience: 1 },
    { id: "sk-7", name: "Docker", category: "Tools & DevOps", proficiency: "Intermediate", years_of_experience: 1 },
    { id: "sk-8", name: "Git", category: "Tools & DevOps", proficiency: "Expert", years_of_experience: 3 },
    { id: "sk-9", name: "SQL", category: "Languages", proficiency: "Expert", years_of_experience: 2 },
    { id: "sk-10", name: "REST APIs", category: "Core Concepts", proficiency: "Expert", years_of_experience: 2 },
    { id: "sk-11", name: "Redis", category: "Databases", proficiency: "Beginner", years_of_experience: 0.5 },
    { id: "sk-12", name: "PyTest", category: "Tools & DevOps", proficiency: "Intermediate", years_of_experience: 1 },
    { id: "sk-13", name: "Linux", category: "Tools & DevOps", proficiency: "Intermediate", years_of_experience: 2 },
    { id: "sk-14", name: "Problem Solving", category: "Soft Skills", proficiency: "Expert" }
  ],
  education: [
    {
      id: "edu-1",
      institution: "FAST National University of Computer and Emerging Sciences",
      degree: "BS in Computer Science",
      field_of_study: "Computer Science",
      start_date: "2020",
      end_date: "2024",
      is_current: false,
      grade_or_gpa: "CGPA: 3.52 / 4.00",
      location: "Lahore, Pakistan",
      description: "Focused on Software Architecture, Distributed Systems, and Database Engines."
    }
  ],
  experience: [
    {
      id: "exp-1",
      company_name: "Systems Limited",
      role_title: "Software Engineer Intern",
      employment_type: "Internship",
      location: "Lahore, Pakistan",
      start_date: "June 2023",
      end_date: "August 2023",
      is_current: false,
      description: "Worked with the cloud backend team building asynchronous REST APIs and optimizing PostgreSQL queries.",
      highlights: [
        "Constructed automated FastAPI microservice endpoints with SQLAlchemy ORM.",
        "Authored comprehensive PyTest test suites and improved test coverage by 30%.",
        "Participated in daily agile standups and Git pull-request code reviews."
      ],
      technologies_used: ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"]
    }
  ],
  projects: [
    {
      id: "proj-1",
      title: "AI Job Application Agent (Phase 1 & 2)",
      description: "Full-stack job application foundation and automated Lahore discovery engine featuring deterministic CV parsing, 10-table PostgreSQL relational schema, and modular scraping services.",
      role: "Lead Full-Stack Developer",
      technologies: ["Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "React", "Docker"],
      repo_url: "https://github.com/irfanrajpoot/ai-job-agent",
      start_date: "2024",
      end_date: "Present",
      highlights: [
        "Architected clean multi-tier backend with separate api, models, schemas, and discovery services.",
        "Engineered zero-hallucination regex and catalog CV extraction parser.",
        "Implemented automated Lahore job collection with deduplication and entry-level filters."
      ]
    },
    {
      id: "proj-2",
      title: "High-Throughput E-Commerce Inventory Engine",
      description: "Scalable backend service handling concurrent cart checkouts and inventory locks with atomic database transactions.",
      role: "Backend Engineer",
      technologies: ["Python", "Django", "PostgreSQL", "Redis", "Docker"],
      repo_url: "https://github.com/irfanrajpoot/inventory-engine",
      start_date: "2023",
      end_date: "2024",
      highlights: [
        "Implemented Redis caching for product catalog decreasing P95 response times to 45ms.",
        "Integrated PostgreSQL row-level locking to prevent race conditions during high-volume flash sales."
      ]
    }
  ],
  certifications: [
    {
      id: "cert-1",
      name: "Meta Backend Developer Professional Certificate",
      issuing_organization: "Meta / Coursera",
      issue_date: "2023",
      credential_id: "META-BACKEND-9921",
      credential_url: "https://coursera.org/verify/professional-cert/meta-backend"
    },
    {
      id: "cert-2",
      name: "AWS Certified Cloud Practitioner",
      issuing_organization: "Amazon Web Services",
      issue_date: "2024",
      credential_id: "AWS-CCP-84729"
    }
  ]
};

export const INITIAL_JOBS: Job[] = [
  {
    id: "job-1",
    company: "Systems Limited",
    job_title: "Associate Software Engineer - Python & Cloud Services",
    location: "Lahore (DHA Phase 8 Campus)",
    job_url: "https://www.systemsltd.com/careers/associate-software-engineer-python",
    source_url: "https://www.systemsltd.com/careers/associate-software-engineer-python",
    description: "Systems Limited is seeking high-potential fresh graduates and entry-level engineers for our Cloud & Enterprise Engineering unit in Lahore. You will work on scalable microservices, backend data pipelines, and REST APIs for global enterprise clients.\n\nKey Responsibilities:\n- Design, develop, and maintain backend microservices using Python and FastAPI/Django.\n- Collaborate with database engineers on PostgreSQL query optimization, indexing, and schema design.\n- Write modular, unit-tested code following clean architectural patterns.\n- Participate in Agile sprints, peer code reviews, and CI/CD automation pipelines.",
    raw_description: "Systems Limited is seeking high-potential fresh graduates and entry-level engineers for our Cloud & Enterprise Engineering unit in Lahore. You will work on scalable microservices, backend data pipelines, and REST APIs for global enterprise clients.\n\nKey Responsibilities:\n- Design, develop, and maintain backend microservices using Python and FastAPI/Django.\n- Collaborate with database engineers on PostgreSQL query optimization, indexing, and schema design.\n- Write modular, unit-tested code following clean architectural patterns.\n- Participate in Agile sprints, peer code reviews, and CI/CD automation pipelines.",
    responsibilities: [
      "Develop backend microservices and RESTful endpoints using Python and FastAPI.",
      "Build and optimize relational database models in PostgreSQL using SQLAlchemy.",
      "Implement unit test coverage using PyTest to ensure production stability.",
      "Collaborate with cross-functional teams in daily standups and sprint planning."
    ],
    required_skills: ["Python", "FastAPI", "SQL", "Git", "OOP", "Data Structures"],
    preferred_skills: ["Docker", "PostgreSQL", "Redis", "PyTest"],
    experience_requirement: "Fresh Graduate to 1 year",
    education_requirement: "BS / MS in Computer Science or Software Engineering",
    job_type: "Full-time",
    salary: "PKR 110,000 - 145,000 / month",
    source: "Systems Limited Careers",
    status: "saved",
    job_status: "saved",
    posting_date: "2026-10-01",
    deadline: "2026-10-30",
    duplicate_status: "unique",
    dedup_hash: "hash_systems_ase_py_lhr_01",
    notes: "Top preference. Alumni from FAST and PUCIT work here.",
    discovered_at: new Date(Date.now() - 86400000 * 2).toISOString(),
    created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "job-2",
    company: "Arbisoft",
    job_title: "Junior Software Engineer (Fresh Graduates Batch)",
    location: "Lahore (Canal Road Campus)",
    job_url: "https://arbisoft.com/careers/junior-software-engineer-fresh-batch",
    source_url: "https://arbisoft.com/careers/junior-software-engineer-fresh-batch",
    description: "Arbisoft is hiring driven, algorithmic-minded problem solvers for our annual Fresh Graduates Batch in Lahore. Our engineering teams build platforms used by millions of global learners, travelers, and healthcare providers.\n\nKey Responsibilities:\n- Implement clean, scalable backend features in Python (Django/FastAPI) or Node.js.\n- Design and optimize relational schemas in PostgreSQL.\n- Write thorough unit and integration test suites.\n- Participate in architectural reviews and Agile sprint cycles.",
    raw_description: "Arbisoft is hiring driven, algorithmic-minded problem solvers for our annual Fresh Graduates Batch in Lahore. Our engineering teams build platforms used by millions of global learners, travelers, and healthcare providers.\n\nKey Responsibilities:\n- Implement clean, scalable backend features in Python (Django/FastAPI) or Node.js.\n- Design and optimize relational schemas in PostgreSQL.\n- Write thorough unit and integration test suites.\n- Participate in architectural reviews and Agile sprint cycles.",
    responsibilities: [
      "Implement scalable backend features in Python/Django with PostgreSQL.",
      "Solve algorithmic problems and optimize existing system performance.",
      "Participate in code reviews with senior principal engineers.",
      "Ensure 80%+ automated test coverage across new feature pull requests."
    ],
    required_skills: ["Python", "Django", "PostgreSQL", "REST APIs", "Git", "Problem Solving"],
    preferred_skills: ["React", "TypeScript", "AWS", "Celery"],
    experience_requirement: "0-1 years (Entry-Level)",
    education_requirement: "Bachelor's in Computer Science / Software Engineering",
    job_type: "Hybrid",
    salary: "PKR 115,000 - 155,000 / month",
    source: "Arbisoft Careers",
    status: "saved",
    job_status: "saved",
    posting_date: "2026-10-02",
    deadline: "2026-11-01",
    duplicate_status: "unique",
    dedup_hash: "hash_arbisoft_jse_lhr_02",
    notes: "Requires clearing online coding assessment (DSA).",
    discovered_at: new Date(Date.now() - 86400000 * 3).toISOString(),
    created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "job-3",
    company: "Devsinc",
    job_title: "Junior Backend Developer - Python / Django",
    location: "Lahore (Johar Town Campus)",
    job_url: "https://www.devsinc.com/careers/junior-backend-developer-python",
    source_url: "https://www.devsinc.com/careers/junior-backend-developer-python",
    description: "Devsinc is hiring Junior Backend Developers eager to work with US technology startups. You will join our agile team building scalable web applications, event-driven pipelines, and relational database services.\n\nKey Responsibilities:\n- Write clean, maintainable Python backend code using Django and FastAPI.\n- Design relational database schemas and write complex SQL queries in PostgreSQL.\n- Integrate third-party payment gateways, OAuth providers, and REST APIs.\n- Work in fast-paced sprint cycles with experienced technical leads.",
    raw_description: "Devsinc is hiring Junior Backend Developers eager to work with US technology startups. You will join our agile team building scalable web applications, event-driven pipelines, and relational database services.\n\nKey Responsibilities:\n- Write clean, maintainable Python backend code using Django and FastAPI.\n- Design relational database schemas and write complex SQL queries in PostgreSQL.\n- Integrate third-party payment gateways, OAuth providers, and REST APIs.\n- Work in fast-paced sprint cycles with experienced technical leads.",
    responsibilities: [
      "Build scalable REST APIs and services in Python/Django.",
      "Integrate PostgreSQL databases with optimized indexes and migrations.",
      "Implement unit and functional testing using PyTest.",
      "Participate in daily client standups and sprint planning."
    ],
    required_skills: ["Python", "Django", "FastAPI", "PostgreSQL", "SQL", "Git"],
    preferred_skills: ["Docker", "Redis", "Celery", "Tailwind CSS"],
    experience_requirement: "0-1 years",
    education_requirement: "BS in Computer Science or Software Engineering",
    job_type: "Full-time",
    salary: "PKR 95,000 - 135,000 / month",
    source: "Devsinc Careers",
    status: "discovered",
    job_status: "discovered",
    posting_date: "2026-10-02",
    deadline: "2026-10-31",
    duplicate_status: "unique",
    dedup_hash: "hash_devsinc_jbe_lhr_03",
    notes: "Multiple positions open for immediate joining.",
    discovered_at: new Date(Date.now() - 86400000 * 4).toISOString(),
    created_at: new Date(Date.now() - 86400000 * 4).toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "job-4",
    company: "Tintash",
    job_title: "Trainee Software Engineer - Web & AI",
    location: "Lahore (Cantt Campus)",
    job_url: "https://tintash.com/careers/trainee-software-engineer",
    source_url: "https://tintash.com/careers/trainee-software-engineer",
    description: "Tintash is looking for exceptional fresh graduates to join our product engineering teams. We build mission-critical products for US startups and innovators with emphasis on craftsmanship and clean code.\n\nKey Responsibilities:\n- Collaborate with senior architects to implement web application features.\n- Write test-driven, maintainable code using Python, TypeScript, and modern frameworks.\n- Participate in design reviews, peer code critiques, and technology sharing sessions.",
    raw_description: "Tintash is looking for exceptional fresh graduates to join our product engineering teams. We build mission-critical products for US startups and innovators with emphasis on craftsmanship and clean code.\n\nKey Responsibilities:\n- Collaborate with senior architects to implement web application features.\n- Write test-driven, maintainable code using Python, TypeScript, and modern frameworks.\n- Participate in design reviews, peer code critiques, and technology sharing sessions.",
    responsibilities: [
      "Implement features in Python and TypeScript following clean code practices.",
      "Build test coverage with automated unit test frameworks.",
      "Participate in sprint retrospectives, planning, and standups."
    ],
    required_skills: ["Python", "FastAPI", "TypeScript", "PostgreSQL", "Git", "Problem Solving"],
    preferred_skills: ["AI/ML Basics", "Docker", "Linux"],
    experience_requirement: "Fresh Graduate (0-1 years)",
    education_requirement: "BS Computer Science / Software Engineering",
    job_type: "Full-time",
    salary: "PKR 100,000 - 135,000 / month",
    source: "Tintash Careers",
    status: "saved",
    job_status: "saved",
    posting_date: "2026-10-03",
    deadline: "2026-11-02",
    duplicate_status: "unique",
    dedup_hash: "hash_tintash_tse_lhr_04",
    notes: "Great engineering culture and US startup exposure.",
    discovered_at: new Date(Date.now() - 86400000 * 5).toISOString(),
    created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "job-5",
    company: "10Pearls",
    job_title: "Associate Software Engineer - Python Backend",
    location: "Lahore (Gulberg III)",
    job_url: "https://10pearls.com/careers/associate-software-engineer-backend",
    source_url: "https://10pearls.com/careers/associate-software-engineer-backend",
    description: "10Pearls is hiring Associate Software Engineers to join our global digital transformation projects. You will develop backend services, data transformations, and cloud integration components.\n\nKey Responsibilities:\n- Implement robust backend logic using Python, FastAPI, and relational databases.\n- Write modular database scripts and optimize SQL queries.\n- Work in Agile sprints with automated continuous delivery pipelines.",
    raw_description: "10Pearls is hiring Associate Software Engineers to join our global digital transformation projects. You will develop backend services, data transformations, and cloud integration components.\n\nKey Responsibilities:\n- Implement robust backend logic using Python, FastAPI, and relational databases.\n- Write modular database scripts and optimize SQL queries.\n- Work in Agile sprints with automated continuous delivery pipelines.",
    responsibilities: [
      "Develop backend microservices with Python and FastAPI.",
      "Build relational database models in PostgreSQL.",
      "Implement automated testing and documentation."
    ],
    required_skills: ["Python", "FastAPI", "SQL", "Git", "OOP"],
    preferred_skills: ["PostgreSQL", "Docker", "CI/CD"],
    experience_requirement: "0-1 years (Entry-Level)",
    education_requirement: "BS Computer Science",
    job_type: "Hybrid",
    salary: "PKR 105,000 - 140,000 / month",
    source: "10Pearls Careers",
    status: "discovered",
    job_status: "discovered",
    posting_date: "2026-10-04",
    deadline: "2026-10-29",
    duplicate_status: "unique",
    dedup_hash: "hash_10pearls_ase_lhr_05",
    notes: "Hybrid work model: 2 days remote, 3 days on-site.",
    discovered_at: new Date(Date.now() - 86400000 * 6).toISOString(),
    created_at: new Date(Date.now() - 86400000 * 6).toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "job-6",
    company: "Netsol Technologies",
    job_title: "Graduate Trainee Engineer - Fintech Backend",
    location: "Lahore (Ring Road Campus)",
    job_url: "https://netsoltech.com/careers/graduate-trainee-engineer",
    source_url: "https://netsoltech.com/careers/graduate-trainee-engineer",
    description: "NetSol Technologies is hiring fresh engineering graduates for our global asset finance and leasing software platforms. Comprehensive 3-month paid training included with full medical and benefits.\n\nKey Responsibilities:\n- Learn enterprise fintech domain and system architecture.\n- Write reliable backend services and database procedures.\n- Execute unit tests and participate in sprint deliverables.",
    raw_description: "NetSol Technologies is hiring fresh engineering graduates for our global asset finance and leasing software platforms. Comprehensive 3-month paid training included with full medical and benefits.\n\nKey Responsibilities:\n- Learn enterprise fintech domain and system architecture.\n- Write reliable backend services and database procedures.\n- Execute unit tests and participate in sprint deliverables.",
    responsibilities: [
      "Develop backend services with clean architecture standards.",
      "Design and maintain relational tables with complex SQL transactions.",
      "Conduct unit testing and resolve assigned bug tickets."
    ],
    required_skills: ["OOP", "Data Structures", "SQL", "Python", "Git"],
    preferred_skills: ["PostgreSQL", "Linux", "Financial Systems"],
    experience_requirement: "Entry-Level (0 years / Fresh)",
    education_requirement: "BS in Computing / Software Engineering",
    job_type: "Full-time",
    salary: "PKR 90,000 - 125,000 / month",
    source: "Netsol Careers",
    status: "discovered",
    job_status: "discovered",
    posting_date: "2026-10-01",
    deadline: "2026-10-28",
    duplicate_status: "unique",
    dedup_hash: "hash_netsol_gte_lhr_06",
    notes: "Formal structured 3-month training program included.",
    discovered_at: new Date(Date.now() - 86400000 * 7).toISOString(),
    created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "job-7",
    company: "TkXel",
    job_title: "Junior Python Developer",
    location: "Lahore (Model Town & Gulberg)",
    job_url: "https://www.rozee.pk/tkxel-junior-python-developer-lahore-jobs",
    source_url: "https://www.rozee.pk/tkxel-junior-python-developer-lahore-jobs",
    description: "TkXel is looking for energetic Junior Python Developers to work on high-impact web systems. Mentorship by senior architects provided.\n\nKey Responsibilities:\n- Develop RESTful APIs and clean backend services in Python.\n- Connect PostgreSQL databases using SQLAlchemy or Django ORM.\n- Implement automated tests and participate in code reviews.",
    raw_description: "TkXel is looking for energetic Junior Python Developers to work on high-impact web systems. Mentorship by senior architects provided.\n\nKey Responsibilities:\n- Develop RESTful APIs and clean backend services in Python.\n- Connect PostgreSQL databases using SQLAlchemy or Django ORM.\n- Implement automated tests and participate in code reviews.",
    responsibilities: [
      "Implement scalable endpoints in Python and FastAPI/Django.",
      "Design and maintain relational tables with PostgreSQL.",
      "Write automated test suites using PyTest."
    ],
    required_skills: ["Python", "FastAPI", "SQL", "Git", "OOP"],
    preferred_skills: ["Docker", "PostgreSQL", "Redis"],
    experience_requirement: "0-1 years (Entry-Level)",
    education_requirement: "BS Computer Science",
    job_type: "Full-time",
    salary: "PKR 90,000 - 130,000 / month",
    source: "Rozee.pk Job Board",
    status: "discovered",
    job_status: "discovered",
    posting_date: "2026-10-02",
    deadline: "2026-10-27",
    duplicate_status: "unique",
    dedup_hash: "hash_tkxel_jpd_lhr_07",
    discovered_at: new Date(Date.now() - 86400000 * 1).toISOString(),
    created_at: new Date(Date.now() - 86400000 * 1).toISOString(),
    updated_at: new Date().toISOString()
  }
];

export const INITIAL_DISCOVERY_RUNS: JobDiscoveryRun[] = [
  {
    id: "run-001",
    triggered_at: new Date(Date.now() - 86400000 * 1).toISOString(),
    completed_at: new Date(Date.now() - 86400000 * 1 + 25000).toISOString(),
    status: "completed",
    sources_checked: ["systems_limited", "arbisoft", "devsinc", "tintash", "ten_pearls", "netsol", "rozee_pk"],
    keywords_used: ["Python Developer", "Software Engineer", "Junior Developer", "AI/ML Engineer"],
    total_discovered: 12,
    new_jobs_added: 7,
    duplicates_skipped: 2,
    rejected_non_lahore: 2,
    rejected_non_entry: 1
  }
];

export const DISCOVERY_SOURCES_LIST: JobDiscoverySourceInfo[] = [
  {
    id: "systems_limited",
    name: "Systems Limited Careers",
    type: "company_careers",
    is_active: true,
    base_url: "https://www.systemsltd.com/careers",
    description: "Official career portal of Pakistan's largest IT exporter (DHA Phase 8 & Central Lahore campuses)."
  },
  {
    id: "arbisoft",
    name: "Arbisoft Careers",
    type: "company_careers",
    is_active: true,
    base_url: "https://arbisoft.com/careers",
    description: "Annual Fresh Graduates Batch & Junior software engineer openings (Canal Road, Lahore)."
  },
  {
    id: "devsinc",
    name: "Devsinc Careers",
    type: "company_careers",
    is_active: true,
    base_url: "https://www.devsinc.com/careers",
    description: "Johar Town & Gulberg campuses hiring for junior full-stack & backend roles."
  },
  {
    id: "tintash",
    name: "Tintash Careers",
    type: "company_careers",
    is_active: true,
    base_url: "https://tintash.com/careers",
    description: "Cantt / DHA campus tech trainee & junior software craftsmanship roles."
  },
  {
    id: "ten_pearls",
    name: "10Pearls Careers",
    type: "company_careers",
    is_active: true,
    base_url: "https://10pearls.com/careers",
    description: "Gulberg III office hiring associate engineers for global cloud backends."
  },
  {
    id: "netsol",
    name: "Netsol Technologies Careers",
    type: "company_careers",
    is_active: true,
    base_url: "https://netsoltech.com/careers",
    description: "NetSol Avenue Ring Road campus Graduate Trainee Engineer programs."
  },
  {
    id: "confiz",
    name: "Confiz Careers",
    type: "company_careers",
    is_active: true,
    base_url: "https://confiz.com/careers",
    description: "Gulberg office associate engineer openings for retail & enterprise cloud systems."
  },
  {
    id: "rozee_pk",
    name: "Rozee.pk IT Board",
    type: "job_board",
    is_active: true,
    base_url: "https://www.rozee.pk/jobs-in-lahore-it",
    description: "Pakistan's primary job portal verified for Lahore tech employers (TkXel, VentureDive, etc.)."
  },
  {
    id: "search_engine",
    name: "Lahore Tech Aggregator",
    type: "search_engine",
    is_active: true,
    base_url: "https://news.google.com/search?q=lahore+software+jobs",
    description: "Aggregated discovery feeds across Lahore software house career boards."
  }
];

export const INITIAL_APPLICATIONS: Application[] = [
  {
    id: "app-1",
    user_id: "user-001",
    job_id: "job-1",
    master_cv_id: "mcv-001",
    status: "applied",
    applied_at: new Date(Date.now() - 86400000 * 2).toISOString(),
    notes: "Submitted via Systems Limited portal. Attached Master CV v1.",
    created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 2).toISOString()
  },
  {
    id: "app-2",
    user_id: "user-001",
    job_id: "job-2",
    master_cv_id: "mcv-001",
    status: "screening",
    applied_at: new Date(Date.now() - 86400000 * 4).toISOString(),
    interview_date: new Date(Date.now() + 86400000 * 3).toISOString(),
    notes: "Online technical coding assessment invitation received! Preparing DSA and Python OOP.",
    created_at: new Date(Date.now() - 86400000 * 4).toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "app-3",
    user_id: "user-001",
    job_id: "job-4",
    master_cv_id: "mcv-001",
    status: "ready",
    notes: "Job saved. Ready to tailor CV once Phase 3 tailoring module is active.",
    created_at: new Date(Date.now() - 86400000 * 1).toISOString(),
    updated_at: new Date().toISOString()
  }
];
