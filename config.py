"""Configuration and search criteria for the job monitor agent."""

# === JOB SEARCH CRITERIA ===

# === TRACK 1: AI Product Manager at the intersection of finance/accounting/audit ===
SEARCH_QUERIES = [
    # AI PM — Zurich area
    "AI product manager Zurich",
    "product manager artificial intelligence Zurich Switzerland",
    "product manager AI finance accounting Zurich",
    "AI product owner fintech Zurich",
    "senior product manager AI Zurich Basel Bern Winterthur Zug",
    "product manager machine learning Zurich Switzerland",
    "product manager LLM AI Zurich",
    # AI PM — finance/audit intersection
    "product manager AI finance",
    "product manager AI accounting audit",
    "product manager AI fintech banking",
    "product manager AI regulatory compliance finance",
    "product manager AI ERP financial systems",
]

# === TRACK 2: Accounting/finance roles at big AI/tech companies ===
SECONDARY_QUERIES = [
    # Accounting at AI companies
    "accountant Anthropic",
    "accounting manager Anthropic",
    "finance manager Anthropic",
    "accountant Mistral AI",
    "finance Mistral AI",
    "accounting manager OpenAI",
    "finance manager OpenAI",
    "accountant Google DeepMind",
    "accounting Google AI Zurich",
    "finance manager Google Zurich",
    "accountant Meta AI Zurich",
    "accounting Apple Zurich",
    "finance controller Microsoft AI Zurich",
    "accountant NVIDIA Zurich Switzerland",
    "accounting manager Amazon AWS Zurich",
    # Broader AI/tech company accounting roles
    "senior accountant AI startup Switzerland",
    "finance controller AI company Europe",
    "accounting manager tech startup Zurich",
    "IFRS accountant tech company Zurich",
    "financial reporting manager AI company",
    # AI PM remote
    "AI product manager remote Europe",
    "product manager AI fintech remote",
    "product manager artificial intelligence finance remote",
]

# Domains to search on
JOB_DOMAINS = [
    "linkedin.com",
    "jobs.ch",
    "indeed.ch",
    "greenhouse.io",
    "lever.co",
    "boards.greenhouse.io",
    "jobs.lever.co",
    "myworkdayjobs.com",
    "join.com",
    "jobup.ch",
    "glassdoor.com",
    "wellfound.com",
]

# A job must match at least one of these keyword groups (OR between groups, any keyword in group matches)
# Track 1: PM roles | Track 2: accounting/finance roles
MUST_HAVE_KEYWORD_GROUPS = [
    ["product manager", "product owner", "product lead", "product management"],
    ["accountant", "accounting", "controller", "financial reporting", "finance manager",
     "finance director", "CFO", "audit", "IFRS", "GAAP"],
]

# Keywords that boost relevance score
BOOST_KEYWORDS = [
    "AI", "artificial intelligence", "machine learning", "LLM", "deep learning",
    "finance", "accounting", "fintech", "financial", "audit", "IFRS", "GAAP",
    "product manager", "product owner", "product lead",
    "Zurich", "Zürich", "Basel", "Bern", "Winterthur", "Zug", "Switzerland",
    "Anthropic", "Mistral", "OpenAI", "DeepMind", "Google", "Meta", "NVIDIA",
    "Apple", "Microsoft", "Amazon",
]

# Keywords that reduce relevance
NEGATIVE_KEYWORDS = [
    "intern", "internship", "werkstudent", "junior",
    "software engineer", "data engineer", "backend developer",
    "frontend developer", "UX designer",
]

# Minimum relevance score to show a job (filters out weak matches)
MIN_RELEVANCE_SCORE = 3

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
