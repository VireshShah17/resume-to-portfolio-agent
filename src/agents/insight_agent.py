import os
import json
from src.state import ResumeToPortfolioState
from src.prompts import INSIGHT_GENERATOR_PROMPT
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from loguru import logger
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


def generate_insights_node(state: ResumeToPortfolioState) -> dict:
    """
        LangGraph node: Compares extracted resume skills with GitHub data to generate actionable feedback.
    """
    logger.info("Initializing Insight Agent node...")
    extracted_skills = state.get("extracted_resume_skills", [])
    github_data = state.get("github_data", {})

    if not extracted_skills:
        logger.warning("No extracted skills found in state. Insight generation may be limited.")
        return {}
    
    if not github_data or "error" in github_data:
        logger.warning("Invalid or empty GitHub data found in state. Insight generation may be limited.")
        return {}

    try:
        logger.info("Connecting to Gemini 2.5 Flash...")
        model_name = os.getenv("GEMINI_AI_MODEL")
        api_key = os.getenv("GOOGLE_API_KEY")

        # Pre-flight check for critical credentials
        if not api_key:
            logger.error("GOOGLE_API_KEY is missing from environment variables. Aborting LLM initialization.")
            return {}
        
        if not model_name:
            logger.warning("GEMINI_AI_MODEL is missing. Defaulting to 'gemini-1.5-flash'.")
            model_name = "gemini-1.5-flash"

        # Attempt to initialize the model
        if api_key:
            try:
                llm = ChatGoogleGenerativeAI(
                    model = model_name, 
                    temperature = 0.4, 
                    google_api_key = api_key,
                    max_retries = 2
                )
                logger.success(f"Successfully initialized Gemini model: {model_name}")
                
            except Exception as e:
                logger.exception(f"Failed to initialize ChatGoogleGenerativeAI: {e}")
                return {}
        
        # 2. Format the data for the prompt
        # We convert lists/dicts to formatted strings so the LLM can easily digest them
        skills_str = ", ".join(extracted_skills) if extracted_skills else "None extracted."
        github_data_str = json.dumps(github_data, indent = 2)
        
        # 3. Format the prompt using our centralized template
        prompt = PromptTemplate.from_template(INSIGHT_GENERATOR_PROMPT)
        formatted_prompt = prompt.format(
            extracted_resume_skills = skills_str,
            github_data = github_data_str
        )
        
        logger.info("Analyzing discrepancies between Resume and GitHub data...")
        
        # 4. Invoke the model
        response = llm.invoke(formatted_prompt)
        
        logger.success("Successfully generated career coaching insights.")
        
        # 5. Return the state update
        return {"insights": response.content}
    except Exception as e:
        logger.error(f"Insight Agent failed during LLM invocation: {e}")
        return {"insights": "Error generating insights due to system failure."}
