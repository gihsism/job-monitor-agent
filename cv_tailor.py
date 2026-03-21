"""CV tailoring module using Claude API."""

import anthropic
from config import MASTER_CV


TAILOR_PROMPT = """\
You are an expert CV/resume writer. You are helping Alena Nikolskaia tailor her CV for a specific job posting.

## Alena's Master CV Data
{master_cv}

## Job Posting
Title: {job_title}
URL: {job_url}

Description:
{job_description}

## Instructions

Rewrite Alena's CV to be tailored for this specific position. Follow these rules STRICTLY:

1. **DO NOT INVENT anything.** Only use facts from the master CV data above. Never add skills, experiences, certifications, or achievements that are not in the master CV.
2. **Rewrite the Summary** to emphasize the aspects of Alena's background most relevant to this role. Highlight the AI/tech angle (ETH CAS in AI, building AI platform at KPMG) and any finance/accounting overlap with the job.
3. **Reorder and emphasize bullet points** to put the most relevant experience first.
4. **Add a "Key Skills" section** near the top, selecting only skills from the master CV that match the job requirements.
5. **Keep ALL work experience entries** but you may shorten less relevant ones.
6. **Output format:** Return a JSON object with these keys:
   - "tailored_summary": string (2-4 sentences)
   - "key_skills": list of strings (8-12 most relevant skills)
   - "experience": list of objects, each with "company", "location", "period", "title", "bullets" (list of strings)
   - "education": list of strings (reordered by relevance)
   - "certifications": list of strings
   - "languages": list of strings
   - "match_analysis": string (2-3 sentences explaining how well Alena fits this role and any gaps)
   - "match_score": integer 1-100 (how well the profile matches)

Return ONLY valid JSON, no markdown fences.
"""


def tailor_cv(anthropic_api_key: str, job: dict) -> dict | None:
    """Use Claude to tailor the CV for a specific job posting. Returns tailored CV dict."""
    client = anthropic.Anthropic(api_key=anthropic_api_key)

    import json
    master_cv_str = json.dumps(MASTER_CV, indent=2)

    prompt = TAILOR_PROMPT.format(
        master_cv=master_cv_str,
        job_title=job["title"],
        job_url=job["url"],
        job_description=job["text"][:4000],
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        # Remove markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[:-3]

        return json.loads(text)

    except Exception as e:
        print(f"[ERROR] CV tailoring failed: {e}")
        return None
