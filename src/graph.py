from src.state import ResumeToPortfolioState
from src.agents.parser_agent import parse_resume_node
from src.agents.insight_agent import generate_insights_node
from langgraph.graph import StateGraph, START, END
from loguru import logger


def build_resume_to_portfolio_graph():
    """
        Compiles the LangGraph workflow for the Career Coach Agent.
    """
    logger.info("Building the Career Coach LangGraph workflow...")

    # Initialize the graph with our custom state schema
    workflow = StateGraph(ResumeToPortfolioState)

    # Add nodes to the agent
    workflow.add_node("parser_agent", parse_resume_node)
    workflow.add_node("insight_agent", generate_insights_node)

    # Define the flow
    workflow.add_edge(START, "parser_agent")
    workflow.add_edge("parser_agent", "insight_agent")
    workflow.add_edge("insight_agent", END)

    # Compile into a runnable graph
    graph = workflow.compile()

    logger.success("Graph compiled successfully.")
    return graph
