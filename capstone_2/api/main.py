"""
FastAPI server for the Autonomous Research Pipeline.

Endpoints:
  POST  /research        — Start a research job for a given topic
  GET   /report/{job_id} — Retrieve the finished report
  GET   /jobs            — List all jobs with their status
  GET   /health          — Health check

NOTE: crew.kickoff() runs synchronously in the request handler for simplicity.
This means POST /research will block until the entire crew finishes (which can
take 1-3 minutes depending on the topic and model). In production, move
crew.kickoff() to a FastAPI BackgroundTask or a Celery/ARQ worker queue, and
poll GET /report/{job_id} for status.
"""

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Crew, Process
from langchain_openai import ChatOpenAI

from crew.agents import create_researcher, create_writer, create_editor
from crew.tasks import create_research_task, create_writing_task, create_editing_task

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Autonomous Research Pipeline API",
    description=(
        "Submit a topic and an AI crew of Researcher, Writer, and Editor "
        "agents will collaboratively produce a polished research report."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory job store
# jobs maps job_id -> {"topic": str, "status": str, "output_file": str | None}
# In production, replace with a database or Redis.
# ---------------------------------------------------------------------------

jobs: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ResearchRequest(BaseModel):
    topic: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "topic": "the impact of large language models on software engineering"
            }
        }
    }


class ResearchResponse(BaseModel):
    job_id: str
    status: str
    message: str


class ReportResponse(BaseModel):
    job_id: str
    topic: str
    content: str


# ---------------------------------------------------------------------------
# LLM factory
# ---------------------------------------------------------------------------

def _get_llm():
    """Create a ChatOpenAI instance from environment config."""
    return ChatOpenAI(
        model=os.getenv("MODEL", "gpt-4o-mini"),
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Utility"])
def health_check():
    """Returns a simple health check response."""
    return {"status": "ok"}


@app.get("/jobs", tags=["Jobs"])
def list_jobs():
    """List all research jobs and their current status."""
    return {
        "jobs": [
            {
                "job_id": job_id,
                "topic": info["topic"],
                "status": info["status"],
            }
            for job_id, info in jobs.items()
        ]
    }


@app.get("/report/{job_id}", response_model=ReportResponse, tags=["Reports"])
def get_report(job_id: str):
    """
    Retrieve the finished research report for a given job ID.
    Returns 404 if the job does not exist, 202 if still processing.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    job = jobs[job_id]

    if job["status"] == "processing":
        raise HTTPException(
            status_code=202,
            detail="Report is still being generated. Please try again shortly.",
        )

    if job["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail=f"Job failed: {job.get('error', 'Unknown error')}",
        )

    output_file = Path(job["output_file"])
    if not output_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Report file not found on disk. The job may have failed silently.",
        )

    content = output_file.read_text(encoding="utf-8")
    return ReportResponse(job_id=job_id, topic=job["topic"], content=content)


@app.post("/research", response_model=ResearchResponse, tags=["Research"])
def start_research(request: ResearchRequest):
    """
    Start a research job for the given topic.

    The crew runs synchronously — this request will block until all three
    agents (Researcher, Writer, Editor) have completed their tasks.
    Typical duration: 60-180 seconds depending on model and topic complexity.

    In production, use a BackgroundTask or task queue to run asynchronously.
    """
    job_id = uuid.uuid4().hex[:8]
    output_file = str(OUTPUT_DIR / f"{job_id}.md")

    # Register job as processing
    jobs[job_id] = {
        "topic": request.topic,
        "status": "processing",
        "output_file": output_file,
    }

    try:
        llm = _get_llm()

        # Build agents
        researcher = create_researcher(llm)
        writer = create_writer(llm)
        editor = create_editor(llm)

        # Build tasks (sequential: each feeds into the next via context)
        research_task = create_research_task(researcher, request.topic)
        writing_task = create_writing_task(writer, research_task)
        editing_task = create_editing_task(editor, writing_task, output_file)

        # Assemble crew
        crew = Crew(
            agents=[researcher, writer, editor],
            tasks=[research_task, writing_task, editing_task],
            process=Process.sequential,
            verbose=True,
        )

        # Run the crew (blocking)
        crew.kickoff()

        # Mark job as completed
        jobs[job_id]["status"] = "completed"

        return ResearchResponse(
            job_id=job_id,
            status="completed",
            message=f"Research completed. Retrieve your report at GET /report/{job_id}",
        )

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Research pipeline failed: {str(e)}",
        )
