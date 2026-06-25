import json
import docx
from loguru import logger


def read_resume_docx(file_path: str) -> str:
    """
        Extracts raw text from a Microsoft Word (.docx) resume.
    """

    logger.info(f"Attempting to parse resume document at: {file_path}")
    try:
        doc = docx.Document(file_path)
        full_text = [para.text for para in doc.paragraphs if para.text.strip()]
        logger.success(f"Successfully extracted {len(full_text)} non-empty paragraphs from the resume.")

        return "\n".join(full_text)
    except Exception as e:
        logger.error(f"Error to read the resume documet from file path: {file_path}")
        return ""


def read_github_json(file_path: str) -> dict:
    """
        Loads the structured JSON payload representing GitHub repository data.
    """

    logger.info(f"Attempting to load GitHub JSON data from: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            logger.success("Successfully loaded and parsed GitHub JSON payload.")

            return data
    except Exception as e:
        logger.error(f"Failed to read GitHub JSON. Error: {e}")
        return {}
    

# Quick local test
if __name__ == '__main__':
    resume_path = 'data/raw/John Doe - Resume.docx'
    github_path = 'data/raw/GitHub REST API (Deep JSON Payload).json'

    # 1. Test Resume Parsing
    try:
        resume_text = read_resume_docx(resume_path)
        if resume_text:
            logger.success(f"Successfully parsed the resume: {resume_path}")
            # Logging a snippet instead of the entire text keeps the console clean
            logger.info(f"Preview: {resume_text[:200]}...") 
        else:
            logger.error(f"Failed to parse the resume: '{resume_path}' returned empty or None.")
    except Exception as e:
        logger.exception(f"An error occurred while reading the resume: {e}")

    # 2. Test GitHub JSON Parsing
    try:
        github_json_data = read_github_json(github_path)
        if github_json_data:
            logger.success(f"Successfully parsed the GitHub JSON payload: {github_path}")
            
            # Safely log information about the payload without dumping massive JSON logs
            if isinstance(github_json_data, dict):
                logger.info(f"Parsed a dictionary with {len(github_json_data)} top-level keys.")
            elif isinstance(github_json_data, list):
                logger.info(f"Parsed a list containing {len(github_json_data)} items.")
            else:
                logger.info("Successfully loaded GitHub JSON data.")
        else:
            logger.error(f"Failed to parse GitHub JSON: '{github_path}' returned empty or None.")
    except Exception as e:
        logger.exception(f"An error occurred while reading the GitHub JSON: {e}")