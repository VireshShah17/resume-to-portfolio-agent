import os
from src.state import ResumeToPortfolioState
from src.prompts import RESUME_PARSER_PROMPT
from pydantic import BaseModel, Field
from typing import List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from loguru import logger
from dotenv import load_dotenv


# Load the envionment variables
load_dotenv()


class ResumeSkills(BaseModel):
    """
        Pydantic schema to strictly enforce the Gemini output format.
    """
    skills: List[str] = Field(description = "A list of technical skills extracted from the raw resume text.")


def parse_resume_node(state: ResumeToPortfolioState):
    """
        LangGraph node: Parses the raw resume text and extracts technical skills.
    """

    logger.info("Initializing Parser Agent node...")   
    raw_text = state.get("resume_text", "")

    if not raw_text:
        logger.error("No resume text found in state. Skipping extraction.")
        return {"extracted_resume_skills": []}

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
                    temperature = 0, 
                    google_api_key = api_key,
                    max_tokens = 550,
                    max_output_tokens = 500,
                    max_retries = 2
                )
                logger.success(f"Successfully initialized Gemini model: {model_name}")
                
            except Exception as e:
                logger.exception(f"Failed to initialize ChatGoogleGenerativeAI: {e}")
                return {}
        
        # 2. Bind the Pydantic schema for structured output
        structured_llm = llm.with_structured_output(ResumeSkills)
        
        # 3. Format the prompt
        prompt = PromptTemplate.from_template(RESUME_PARSER_PROMPT)
        formatted_prompt = prompt.format(resume_text = raw_text)
        
        logger.info("Sending resume text to Gemini for skill extraction...")
        
        # 4. Invoke the model
        response: Any = structured_llm.invoke(formatted_prompt)
        
        logger.success(f"Successfully extracted {len(response.skills)} skills.")
        logger.debug(f"Extracted skills: {response.skills}")
        
        # 5. Return the state update (LangGraph automatically merges this into the global state)
        return {"extracted_resume_skills": response.skills}
        
    except Exception as e:
        logger.error(f"Parser Agent failed during LLM invocation: {e}")
        return {"extracted_resume_skills": []}
