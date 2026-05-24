"""
CrewAI agent definitions for the Autonomous Research Pipeline.

Three agents collaborate in sequence:
  1. Researcher  — gathers information about a topic
  2. Writer      — produces a structured report from the research
  3. Editor      — reviews and polishes the report for publication
"""

from crewai import Agent
from tools.search_tool import get_search_tool


def create_researcher(llm) -> Agent:
    """
    Senior Research Analyst — finds comprehensive information on any topic.

    This agent is equipped with the search tool and is responsible for
    gathering facts, statistics, and credible sources before handing off
    to the Writer.
    """
    return Agent(
        role="Senior Research Analyst",
        goal=(
            "Find comprehensive, accurate, and up-to-date information about the given topic. "
            "Identify key facts, trends, statistics, and credible sources."
        ),
        backstory=(
            "You are an experienced research analyst with over 15 years of expertise in "
            "gathering and evaluating information across diverse domains — from technology "
            "and science to business and social sciences. You have a talent for cutting "
            "through noise to find the most relevant and reliable data. You cross-reference "
            "multiple sources before drawing conclusions, and you always note where information "
            "is uncertain or contested. You communicate your findings clearly and concisely so "
            "that writers and editors can build on your work effectively."
        ),
        tools=[get_search_tool()],
        allow_delegation=False,
        verbose=True,
        llm=llm,
    )


def create_writer(llm) -> Agent:
    """
    Technical Content Writer — transforms research findings into a clear report.

    This agent receives the researcher's output as context and produces a
    well-structured Markdown report with defined sections.
    """
    return Agent(
        role="Technical Content Writer",
        goal=(
            "Write a clear, well-structured, and engaging report based on the research findings. "
            "The report should be accessible to a general technical audience."
        ),
        backstory=(
            "You are a skilled technical content writer with a background in journalism and "
            "software engineering. You have spent a decade writing whitepapers, blog posts, "
            "and research summaries for leading technology organisations. You excel at taking "
            "complex, data-heavy research and turning it into readable, well-organised prose "
            "that informs without overwhelming the reader. You structure every report with a "
            "clear Introduction, Key Findings, Analysis, and Conclusion, and you always "
            "attribute information to its source where possible."
        ),
        tools=[],
        allow_delegation=False,
        verbose=True,
        llm=llm,
    )


def create_editor(llm) -> Agent:
    """
    Senior Editor — reviews and improves the written report.

    This agent receives the writer's draft as context and produces the final,
    publication-ready version of the report.
    """
    return Agent(
        role="Senior Editor",
        goal=(
            "Review and improve the written report for clarity, accuracy, structure, and completeness. "
            "Ensure the final output is polished and publication-ready."
        ),
        backstory=(
            "You are a meticulous senior editor who has worked at major publishing houses "
            "and technology media outlets for over 20 years. You have a sharp eye for "
            "ambiguous language, logical gaps, and structural weaknesses. You improve "
            "readability by varying sentence structure, removing jargon where simpler words "
            "work better, and ensuring that headings and sub-sections flow logically. "
            "You also verify that the report's claims are grounded in the research provided "
            "and flag any statements that seem speculative or unsupported. Your edits are "
            "constructive — you preserve the writer's voice while elevating the overall quality."
        ),
        tools=[],
        allow_delegation=False,
        verbose=True,
        llm=llm,
    )
