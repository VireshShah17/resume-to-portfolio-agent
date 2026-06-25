from typing import TypedDict, Dict, List, Any


class ResumeToPortfolioState(TypedDict):
    """
        The state schema for the Resume to Portfolio Agent LangGraph workflow.
    """
    
    resume_text: str
    github_data: Dict[str, Any]
    extracted_resume_skills: List[str]
    insights: str
