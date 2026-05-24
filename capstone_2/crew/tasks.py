"""
CrewAI task definitions for the Autonomous Research Pipeline.

Three tasks run sequentially, each feeding its output to the next:
  1. Research Task  — gather information about the topic
  2. Writing Task   — write a structured report using the research
  3. Editing Task   — review and improve the report, save to file
"""

from crewai import Task


def create_research_task(agent, topic: str) -> Task:
    """
    Task 1: Research the given topic thoroughly.

    Args:
        agent: The Researcher agent that will execute this task.
        topic: The topic to research.

    Returns:
        A CrewAI Task configured for deep-dive research.
    """
    return Task(
        description=(
            f"Conduct thorough research on the following topic: **{topic}**\n\n"
            "Your research should cover:\n"
            "1. A clear definition and overview of the topic.\n"
            "2. Key facts, statistics, and data points.\n"
            "3. Recent developments, trends, or breakthroughs.\n"
            "4. Major challenges or open questions in the field.\n"
            "5. Notable organisations, researchers, or projects involved.\n"
            "6. Real or plausible sources that support your findings.\n\n"
            "Use the available search tool to gather information. "
            "Be thorough and prioritise accuracy over quantity."
        ),
        expected_output=(
            f"A comprehensive research summary about '{topic}' containing:\n"
            "- An overview paragraph (3-5 sentences)\n"
            "- At least 5 key facts or data points with context\n"
            "- 2-3 current trends or recent developments\n"
            "- Key challenges or limitations\n"
            "- A list of sources (URLs or publication references)"
        ),
        agent=agent,
    )


def create_writing_task(agent, research_task: Task) -> Task:
    """
    Task 2: Write a structured report from the research findings.

    Args:
        agent: The Writer agent that will execute this task.
        research_task: The preceding research task (used as context).

    Returns:
        A CrewAI Task configured to produce a structured Markdown report.
    """
    return Task(
        description=(
            "Using the research findings provided in your context, write a comprehensive "
            "and well-structured report in Markdown format.\n\n"
            "The report MUST include these sections in order:\n"
            "1. **Introduction** — Set the scene. Why does this topic matter? (2-3 paragraphs)\n"
            "2. **Key Findings** — The most important facts and data. Use bullet points where appropriate.\n"
            "3. **Analysis** — Interpret the findings. What do they mean? What are the implications?\n"
            "4. **Conclusion** — Summarise the report and suggest areas for further investigation.\n\n"
            "Write for a technical but non-specialist audience. "
            "Avoid excessive jargon. Use headings, sub-headings, and bullet points to aid readability. "
            "The report should be at least 500 words."
        ),
        expected_output=(
            "A well-structured Markdown report with the following sections:\n"
            "# [Topic Title]\n"
            "## Introduction\n"
            "## Key Findings\n"
            "## Analysis\n"
            "## Conclusion\n\n"
            "The report should be at least 500 words, use proper Markdown formatting, "
            "and read as a coherent, professional document."
        ),
        agent=agent,
        context=[research_task],
    )


def create_editing_task(agent, writing_task: Task, output_file: str) -> Task:
    """
    Task 3: Edit and polish the written report, then save it to a file.

    Args:
        agent: The Editor agent that will execute this task.
        writing_task: The preceding writing task (used as context).
        output_file: Path to the output file where the final report will be saved.

    Returns:
        A CrewAI Task configured to produce the final polished report.
    """
    return Task(
        description=(
            "Review the written report provided in your context and improve it for "
            "publication. Your editing should:\n\n"
            "1. **Fix clarity issues** — Rewrite sentences that are ambiguous, overly complex, "
            "or hard to follow.\n"
            "2. **Improve structure** — Ensure the report flows logically from section to section. "
            "Add transitional sentences where needed.\n"
            "3. **Check completeness** — Verify all required sections are present "
            "(Introduction, Key Findings, Analysis, Conclusion). "
            "Expand any section that feels underdeveloped.\n"
            "4. **Remove redundancy** — Eliminate repetitive statements or filler phrases.\n"
            "5. **Enhance headings** — Make headings specific and descriptive.\n"
            "6. **Preserve Markdown formatting** — The output must remain valid Markdown.\n\n"
            "The final output should be noticeably improved compared to the draft. "
            "Do not simply return the draft unchanged."
        ),
        expected_output=(
            "A polished, publication-ready Markdown report that:\n"
            "- Is clearly written and easy to read\n"
            "- Has all required sections (Introduction, Key Findings, Analysis, Conclusion)\n"
            "- Uses consistent Markdown formatting throughout\n"
            "- Is at least 500 words\n"
            "- Contains visible improvements over the writer's draft"
        ),
        agent=agent,
        context=[writing_task],
        output_file=output_file,
    )
