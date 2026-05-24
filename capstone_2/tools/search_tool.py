"""
Search tool for the Research Pipeline.

Strategy:
  1. If SERPER_API_KEY is set in the environment AND crewai_tools is installed,
     use SerperDevTool for real web searches.
  2. Otherwise, fall back to a mock search tool that returns realistic-looking
     research data for any topic — no API key required.

Export:
  get_search_tool() -> a CrewAI-compatible tool instance
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Mock search tool (always available, no API key needed)
# ---------------------------------------------------------------------------

def _mock_search(topic: str) -> dict:
    """
    Return realistic-looking (but fabricated) research data for any topic.
    Used when no Serper API key is configured.
    """
    return {
        "topic": topic,
        "key_facts": [
            f"{topic} has seen significant developments over the past decade, "
            "with researchers and practitioners making major breakthroughs.",
            f"The global market related to {topic} is projected to grow substantially, "
            "driven by increased adoption across industries.",
            f"Key challenges in {topic} include scalability, interpretability, "
            "and ensuring equitable access to advancements.",
            f"Leading institutions researching {topic} include universities, "
            "technology companies, and government-funded research labs.",
            f"Recent publications on {topic} highlight the importance of "
            "interdisciplinary collaboration between technologists, ethicists, and domain experts.",
        ],
        "sources": [
            f"https://arxiv.org/search/?query={topic.replace(' ', '+')}&searchtype=all",
            f"https://scholar.google.com/scholar?q={topic.replace(' ', '+')}",
            f"https://www.nature.com/search?q={topic.replace(' ', '+')}",
        ],
    }


def _build_mock_tool():
    """Build a CrewAI BaseTool wrapping the mock search function."""
    from typing import Type
    from crewai.tools import BaseTool
    from pydantic import BaseModel, Field

    class SearchInput(BaseModel):
        query: str = Field(description="The topic or query to research.")

    class MockSearchTool(BaseTool):
        name: str = "MockSearchTool"
        description: str = (
            "Search for information about any topic. "
            "Returns key facts and source URLs for research purposes."
        )
        args_schema: Type[BaseModel] = SearchInput

        def _run(self, query: str) -> str:
            data = _mock_search(query)
            facts = "\n".join(f"  - {f}" for f in data["key_facts"])
            sources = "\n".join(f"  - {s}" for s in data["sources"])
            return (
                f"Research results for: {data['topic']}\n\n"
                f"Key Facts:\n{facts}\n\n"
                f"Sources:\n{sources}"
            )

    return MockSearchTool()


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------

def get_search_tool():
    """
    Return the best available search tool.

    Returns SerperDevTool if SERPER_API_KEY is configured and crewai_tools
    is installed; otherwise returns the built-in MockSearchTool.
    """
    serper_key = os.getenv("SERPER_API_KEY")

    if serper_key:
        try:
            from crewai_tools import SerperDevTool
            print("[SearchTool] Using SerperDevTool (real web search).")
            return SerperDevTool()
        except ImportError:
            print(
                "[SearchTool] SERPER_API_KEY is set but crewai_tools is not installed. "
                "Falling back to MockSearchTool. "
                "Run: pip install crewai-tools"
            )

    print("[SearchTool] Using MockSearchTool (no SERPER_API_KEY configured).")
    return _build_mock_tool()
