"""Pre-screen jobs using Claude to assess match quality before showing to user."""

import json
import anthropic
from config import MASTER_CV

SCREEN_PROMPT = """\
You are a job matching expert. Score how well this candidate matches the job posting.

## Candidate Profile
{profile_summary}

## Job Posting
Title: {job_title}
URL: {job_url}

Description:
{job_description}

## Scoring Instructions

Score the match from 0 to 100 based on:
- Role fit: Does the job title/function align with the candidate's experience and career goals?
- Skills overlap: How many required skills does the candidate have?
- Industry match: Does the candidate's industry experience match?
- Location: Is the job in Switzerland/Zurich area or remote-friendly?
- Seniority: Does the seniority level match?

The candidate is pivoting from finance/accounting (13+ years, KPMG Senior Manager) into business-side AI roles.
She has an ETH CAS in AI, an ETH MAS in Management/Technology/Economics, and is building an AI platform at KPMG.
She does NOT have a computer science degree — she needs roles that value business/domain expertise over deep technical CS skills.

IMPORTANT: First determine if this is an ACTUAL JOB POSTING (has apply button, lists requirements/qualifications, mentions hiring).
If it is NOT a job posting (it's a blog post, news article, course, report, guide, company page, or person's profile), score 0 regardless of topic relevance.

For actual job postings, score as follows:

Score HIGH (80-100) if the role:
- Explicitly combines AI/digital transformation WITH finance, accounting, audit, or financial reporting
- Values Big 4 / advisory background + AI skills (e.g., AI advisory in accounting, finance transformation with AI)
- Involves building/managing AI tools or platforms for accounting, financial reporting, audit, or compliance
- Is a senior accounting/finance role (IFRS, consolidation, M&A) at a well-known AI or tech company
- Is based in Switzerland/Europe or is remote-friendly

Score MEDIUM (50-70) if:
- It's a general AI product/strategy/transformation role that COULD leverage finance expertise but doesn't explicitly require it
- It's a finance role at a tech company but doesn't involve AI
- It's a general finance transformation role (even without explicit AI mention — these often involve AI in practice)

Score LOW (1-40) if:
- The role requires a CS/engineering degree or hands-on ML engineering as core responsibility
- The role is unrelated to both AI and finance/accounting
- The role is too junior or too narrowly technical
- The location is outside Europe and not remote-friendly

Return ONLY a JSON object with:
- "score": integer 0-100
- "reason": string (1 sentence explaining the score)

No markdown fences.
"""

PROFILE_SUMMARY = (
    "Alena Nikolskaia — Senior Manager at KPMG (Technical Accounting Advisory), "
    "13+ years in finance/accounting across KPMG (Big 4) and Hitachi Energy (Fortune 500). "
    "ACCA, Swiss Audit License. Deep expertise: IFRS, US GAAP, SOX, consolidation, "
    "post-M&A accounting, carve-outs, GAAP conversions, revenue recognition, financial reporting. "
    "Led global US GAAP→IFRS conversion for 120+ entities across 62 countries. "
    "Currently building an AI-powered Accounting Knowledge Platform at KPMG. "
    "ETH CAS in AI & Software Development (2024). MAS in Management, Technology & Economics at ETH (2027). "
    "Skills: Python, Java, S/4HANA, Tagetik, Hyperion. "
    "Trained 300+ financial controllers globally via 40+ webinars. "
    "Based in Zurich, Switzerland. "
    "Target: roles at the intersection of AI and finance/accounting/audit — "
    "where her rare combination of deep accounting domain expertise + AI/tech skills is the differentiator. "
    "Also open to senior accounting/finance roles at AI/tech companies."
)


def screen_job(anthropic_api_key: str, job: dict) -> dict:
    """Screen a job and return score + reason. Returns {'score': int, 'reason': str}."""
    client = anthropic.Anthropic(api_key=anthropic_api_key)

    prompt = SCREEN_PROMPT.format(
        profile_summary=PROFILE_SUMMARY,
        job_title=job["title"],
        job_url=job["url"],
        job_description=job["text"][:3000],
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[:-3]

        result = json.loads(text)
        return {"score": int(result["score"]), "reason": result.get("reason", "")}

    except Exception as e:
        print(f"[WARN] Screening failed for '{job['title']}': {e}")
        # On failure, let it through with a neutral score
        return {"score": 50, "reason": "Screening failed, showing for manual review"}
