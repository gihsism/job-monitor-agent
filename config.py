"""Configuration and search criteria for the job monitor agent."""

# === JOB SEARCH CRITERIA ===

# === TRACK 1: AI + Finance/Accounting transformation roles ===
# Targeting roles where deep IFRS/GAAP/audit expertise + AI skills = unique advantage
SEARCH_QUERIES = [
    # AI in accounting/audit — Alena's #1 sweet spot
    "We are hiring AI accounting transformation manager. IFRS GAAP. Requirements:",
    "AI audit transformation lead. Big 4 advisory. Apply now. Qualifications:",
    "AI financial reporting manager. IFRS automation. Responsibilities:",
    "GenAI accounting advisory manager. We are looking for:",
    "AI-powered accounting platform product manager. Requirements:",
    # Finance transformation + AI/digital
    "Finance transformation manager AI digital. S4HANA. Requirements:",
    "Digital transformation lead finance accounting. AI automation. Apply:",
    "Finance systems transformation manager AI. ERP. Qualifications:",
    "IFRS conversion manager AI automation. We are hiring:",
    # AI in Big 4 / advisory / consulting
    "AI advisory senior manager accounting financial services. Requirements:",
    "AI consulting manager finance KPMG Deloitte EY PwC. Apply:",
    "Technology consulting manager finance accounting AI. Qualifications:",
    # Product / program roles — AI + finance domain
    "Product manager AI finance accounting platform. Requirements:",
    "Product owner AI fintech IFRS compliance. Apply now:",
    "Program manager AI implementation finance. Responsibilities:",
    "Project manager AI accounting ERP transformation. We are hiring:",
    # AI governance / risk / compliance in finance
    "AI governance manager financial services compliance. Requirements:",
    "AI risk manager finance banking. Qualifications:",
    "RegTech AI manager compliance accounting. Apply:",
    # Knowledge management / training — AI in finance
    "AI knowledge management lead finance accounting. Requirements:",
    "AI training program manager financial services. Apply:",
]

# === TRACK 2: Senior finance/accounting at AI/tech companies ===
SECONDARY_QUERIES = [
    "Head of accounting AI company. IFRS US GAAP consolidation. Requirements:",
    "Technical accounting manager tech company. IFRS. Apply now:",
    "Finance controller AI startup Switzerland. Qualifications:",
    "Financial reporting manager AI company. IFRS consolidation. Responsibilities:",
    "Accounting manager Google Zurich. IFRS. Apply:",
    "Finance manager Anthropic OpenAI Mistral. Requirements:",
    "Senior accounting manager fintech. IFRS GAAP M&A. We are hiring:",
    "Group accounting manager tech company. Consolidation IFRS. Apply:",
    "Controller AI company Europe. Financial reporting. Requirements:",
]

# Primary domains: actual job boards where Exa finds real postings
# These are searched first; then a second open search catches company career pages
JOB_BOARD_DOMAINS = [
    "greenhouse.io", "boards.greenhouse.io", "job-boards.greenhouse.io",
    "lever.co", "jobs.lever.co",
    "myworkdayjobs.com",
    "jobs.ch", "jobup.ch", "indeed.ch", "indeed.com",
    "wellfound.com",
    "glassdoor.com",
    "join.com",
    "talantix.io",
    "euremotejobs.com",
    "flexionis.wuaze.com",
    "thesaraslist.com",
    "hiredock.com",
    "hubmub.com",
    "ceruleanjobs.com",
    "bulldogjob.com",
    "fintechcareers.com",
    "rocken.jobs",
]

# Domains to exclude (blogs, news, courses — not job postings)
EXCLUDE_DOMAINS = [
    "medium.com", "substack.com", "arxiv.org",
    "youtube.com", "reddit.com", "twitter.com",
    "wikipedia.org", "coursera.org", "udemy.com",
    "linkedin.com",  # Exa can't index LinkedIn job pages
]

# Legacy — kept for backward compatibility
JOB_DOMAINS = []

# A job must match at least one of these keyword groups (OR between groups)
# Track 1: Business-side AI roles | Track 2: Accounting/finance roles
MUST_HAVE_KEYWORD_GROUPS = [
    # Business-side AI management roles
    [
        "product manager", "product owner", "product lead", "product management",
        "program manager", "project manager",
        "transformation manager", "transformation lead",
        "innovation manager", "innovation lead",
        "strategy manager", "strategy lead", "head of strategy",
        "AI lead", "AI manager", "head of AI",
        "solutions manager", "solutions lead",
        "business analyst", "business lead", "business manager",
        "advisory manager", "consultant", "consulting",
        "implementation lead", "implementation manager",
        "operations manager", "governance manager",
        "regtech", "suptech",
    ],
    # Accounting/finance roles
    [
        "accountant", "accounting", "controller", "financial reporting",
        "finance manager", "finance director", "head of finance",
        "CFO", "audit", "IFRS", "GAAP", "consolidation",
    ],
]

# Keywords that boost relevance score
BOOST_KEYWORDS = [
    # AI/tech
    "AI", "artificial intelligence", "machine learning", "LLM", "deep learning",
    "generative AI", "NLP", "automation", "digital transformation",
    # Finance domain
    "finance", "accounting", "fintech", "financial", "audit", "IFRS", "GAAP",
    "banking", "compliance", "regulatory", "ERP",
    # Role types
    "product manager", "product owner", "program manager", "transformation",
    "innovation", "strategy", "advisory", "consulting",
    # Location
    "Zurich", "Zürich", "Basel", "Bern", "Winterthur", "Zug", "Switzerland",
    "remote",
    # Top AI/tech companies
    "Anthropic", "Mistral", "OpenAI", "DeepMind", "Google", "Meta", "NVIDIA",
    "Apple", "Microsoft", "Amazon",
]

# Keywords that reduce relevance — roles requiring deep CS/engineering background
NEGATIVE_KEYWORDS = [
    "intern", "internship", "werkstudent",
    "software engineer", "data engineer", "backend developer",
    "frontend developer", "UX designer", "ML engineer",
    "machine learning engineer", "research scientist",
    "PhD required", "computer science degree required",
]

# URL patterns that indicate a profile/CV page rather than a job posting
PROFILE_URL_PATTERNS = [
    "/in/",            # LinkedIn profiles (linkedin.com/in/someone)
    "/pub/",           # LinkedIn public profiles
    "/profile/",
    "/people/",
    "/user/",
    "/resume/",
    "/cv/",
]

# Title patterns that indicate non-job content (articles, profiles, courses, news)
PROFILE_TITLE_KEYWORDS = [
    # Profiles/CVs
    "profile", "resume", "curriculum vitae",
    " CV ", " - CV", "CV -",
    # News articles
    "joins ", "joined ", "appoints ", "appointed ",
    "launches ", "launched ",
    "announces ", "announced ",
    # Listicles / guides
    "top 10 ", "top 20 ", "best companies",
    "how to ", "introduction to ", "guide to ",
    "interview with", "interview questions",
    # Blog/thought leadership
    "why ", "what businesses need",
    "framework for ", "new framework",
    # Academic / courses
    "(PDF)", "university of",
    # Non-English content (unlikely to be relevant job postings)
    "schluss mit", "neuer finanzchef",
]

# Minimum relevance score to show a job (filters out weak matches)
# Minimum keyword relevance score (basic filter before AI screening)
MIN_RELEVANCE_SCORE = 2

# Minimum AI match score (0-100) — only jobs scoring this or higher get sent to Telegram
MIN_MATCH_SCORE = 60

# === MASTER CV CONTENT ===

MASTER_CV = {
    "name": "Alena Nikolskaia",
    "title": "ACCA, Swiss Audit License",
    "phone": "+41 (0) 79 375 13 30",
    "linkedin": "https://www.linkedin.com/in/alena-n-80966153",
    "summary": (
        "Finance leader with 13+ years of experience delivering strategic accounting solutions "
        "across Big-4 advisory (KPMG) and a Fortune 500 multinational (Hitachi). Expertise spans "
        "IFRS, US GAAP, Swiss CO and Swiss GAAP FER with deep specialization in post-M&A accounting, "
        "carve-outs, GAAP conversions, complex consolidations, revenue recognition, provisions, "
        "CGU and segments determination and disclosure, intangibles (R&D, IP, and tech assets), "
        "restructuring, lease accounting, and financial reporting. Led large-scale technical accounting "
        "transformations across multinational environments - balancing regulatory precision with business "
        "impact. Currently spearheading the development of an AI-powered Accounting Knowledge Platform "
        "at KPMG, aiming to transform how organizations access, apply, and scale technical accounting insights."
    ),
    "experience": [
        {
            "company": "KPMG AG",
            "location": "Switzerland, Zurich",
            "period": "April 2025 – present",
            "title": "Senior Manager, Technical Accounting Advisory",
            "bullets": [
                "Lead technical accounting consultations for corporate clients on complex transactions",
                "Lead the preparation of technical accounting memos and white papers on complex accounting matters",
                "Advise CFOs, controllers, and audit committees on accounting implications of transactions",
                "Provide technical guidance and interpretations on new and emerging accounting standards, including impact assessments and implementation roadmaps",
            ],
        },
        {
            "company": "Hitachi Energy",
            "location": "Global",
            "period": "May 2020 – March 2025",
            "title": "Consolidation and Reporting Manager (Technical Accounting Expert)",
            "description": (
                "Managed and executed a global US GAAP to IFRS Conversion for 120+ entities spanning "
                "62 countries. Co-managed the technical accounting agenda. Provided key technical accounting "
                "expertise for S4H and Tagetik implementations. Drove knowledge scale by designing and "
                "delivering 40+ webinars training 300+ financial controllers globally."
            ),
            "bullets": [
                "Developed accounting interpretations for complex transactions and prepared position papers for audit review",
                "Prepared stand-alone sub-consolidated financial statements",
                "Supported S/4HANA and Tagetik implementation by providing technical accounting specifications and IFRS requirements",
                "Established and maintained group-wide IFRS accounting policies across 120+ subsidiaries",
                "Led cross-functional collaboration with business units, IT, internal controls, and external auditors",
            ],
        },
        {
            "company": "KPMG AG",
            "location": "Switzerland, Zurich",
            "period": "February 2018 – May 2020",
            "title": "Assistant Manager",
            "bullets": [
                "Led 100+ external audits of US GAAP and IFRS financial statements across technology, natural resources, pharma",
                "Designed audit of consolidated financial statements and SOX controls for first-year multinational client (ABB)",
                "Coordinated 80+ multinational component audit teams",
                "Decreased audit hours by 10-30% through automation and process optimization",
            ],
        },
        {
            "company": "KPMG LLP",
            "location": "United Kingdom, Bristol",
            "period": "August 2016 – February 2018",
            "title": "Assistant Manager",
            "bullets": [
                "Managed 9 engagements simultaneously with acknowledged high quality",
            ],
        },
        {
            "company": "KPMG CJSC",
            "location": "Russian Federation, Moscow",
            "period": "September 2012 – August 2016",
            "title": "Auditor / Senior Auditor",
            "bullets": [
                "External audit of IFRS and local GAAP financial statements across energy, oil & gas, mining, pharma industries",
            ],
        },
    ],
    "education": [
        "MAS in Management, Technology and Economics, ETH Zurich (expected June 2027)",
        "CAS in Artificial Intelligence and Software Development, ETH Zurich (June 2024)",
        "Business Information Technology courses, ZHAW (2022)",
        "BSc in Finance, Higher School of Economics (2016)",
        "MSc in Sociology, Moscow State University M.V. Lomonosov (2011)",
    ],
    "certifications": [
        "ACCA (Association of Chartered Certified Accountants), since 2016",
        "Swiss Audit License, 2020",
    ],
    "skills": {
        "accounting": ["IFRS", "US GAAP", "PCAOB", "SOX", "Swiss GAAP FER", "Swiss CO"],
        "technical": [
            "Post-M&A accounting", "Carve-outs", "GAAP conversions",
            "Revenue recognition", "Consolidation", "Financial reporting",
            "Restructuring", "Lease accounting", "Intangibles (R&D, IP, tech assets)",
        ],
        "technology": [
            "AI/ML (ETH CAS)", "Python", "Java", "S/4HANA", "Tagetik",
            "Hyperion", "MS Excel (advanced)", "Data & Analytics",
        ],
        "soft": [
            "Project management", "Cross-functional leadership",
            "Training & knowledge scaling (300+ people trained)",
            "Multinational team coordination (80+ teams)",
            "Stakeholder management (CFOs, audit committees)",
        ],
    },
    "languages": [
        "English (fluent, C1)",
        "German (basic, A1-A2)",
        "Russian (native)",
    ],
    "other": [
        "Founder of non-profit political organization in Switzerland (Russland der Zukunft)",
        "Built AI-powered Accounting Knowledge Platform at KPMG",
    ],
}
