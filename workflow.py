import subprocess
import sys
from pathlib import Path
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

# CONFIG
PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# SHARED WORKFLOW STATE
class ArticleWorkFlowState(TypedDict):
    topic: str
    plan_file: str
    research_file: str
    draft_file: str
    final_file: str

def run_agent_module(
        module_name: str,
        topic: str,
        expected_output: Path,
        agent_label: str
)-> str:

    if expected_output.is_file() and expected_output.stat().st_size > 0:
        print(f"\nSkipping {agent_label}.")
        print("An existing result file was found:")
        print(expected_output.resolve())
        print("Reusing this result for the next workflow step.")

        return str(expected_output.resolve())

    
    print(f"\n{"#"*50}")
    print(f"Running {agent_label}...")
    print(f"{"#"*50}\n")

    result = subprocess.run(
        [sys.executable, "-m", module_name],
        input=f"{topic}\n",
        text=True,
        cwd=PROJECT_ROOT,
        check=False
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{agent_label} failed with exit code {result.returncode}. Check the error"
        )

    if (
        not expected_output.is_file()
        or expected_output.stat().st_size == 0
    ):
        raise FileNotFoundError(
            f"{agent_label} completed but its expected output file not found: {expected_output}"
        )

    print(f"\n{agent_label} completed successfully")
    print(expected_output.resolve())

    return str(expected_output.resolve())


# PLANNER NODE
def planner_node(state: ArticleWorkFlowState)-> dict:
    """ Run the Planner Agent"""
    topic = state["topic"]
    topic_slug = topic.lower().replace(" ", "_")

    plan_file = OUTPUT_DIR/ f"plan_{topic_slug}.md"

    saved_path = run_agent_module(
        module_name="agents.planner_agent",
        topic=topic,
        expected_output=plan_file,
        agent_label="Planner Agent"
    )

    return {"plan_file": saved_path}


# RESEARCH NODE
def research_node(state: ArticleWorkFlowState)-> dict:
    """ Run the Research Agent"""
    topic = state["topic"]
    topic_slug = topic.lower().replace(" ", "_")

    research_file = OUTPUT_DIR/ f"research_notes_{topic_slug}.md"

    saved_path = run_agent_module(
        module_name="agents.research_agent",
        topic=topic,
        expected_output=research_file,
        agent_label="Research Agent"
    )

    return {"research_file": saved_path}


# WRITER NODE
def writer_node(state: ArticleWorkFlowState)-> dict:
    """ Run the Writer Agent"""
    topic = state["topic"]
    topic_slug = topic.lower().replace(" ", "_")

    draft_file = OUTPUT_DIR/ f"article_{topic_slug}_draft.md"

    saved_path = run_agent_module(
        module_name="agents.writer_agent",
        topic=topic,
        expected_output=draft_file,
        agent_label="Writer Agent"
    )

    return {"draft_file": saved_path}


# EDITOR NODE
def editor_node(state: ArticleWorkFlowState)-> dict:
    """ Run the Editor Agent"""
    topic = state["topic"]
    topic_slug = topic.lower().replace(" ", "_")

    edited_file = OUTPUT_DIR/ f"edited_article_{topic_slug}.md"

    saved_path = run_agent_module(
        module_name="agents.editor_agent",
        topic=topic,
        expected_output=edited_file,
        agent_label="Editor Agent"
    )

    return {"final_file": saved_path}

##################################################################################333

# BUILD THE LANGGRAPH WORKFLOW
graph_builder = StateGraph(ArticleWorkFlowState)

# Register the four agent nodes
graph_builder.add_node("planner", planner_node)
graph_builder.add_node("researcher", research_node)
graph_builder.add_node("writer", writer_node)
graph_builder.add_node("editor", editor_node)

# Connect the agents in sequence
graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "researcher")
graph_builder.add_edge("researcher", "writer")
graph_builder.add_edge("writer", "editor")
graph_builder.add_edge("editor", END)

# Compile the graph
article_workflow = graph_builder.compile()


# RUN THE WORKFLOW
def main():
    """Ask for the topic and execute all four agents"""

    topic = input("Enter the article topic: ").strip()

    if not topic:
        print("Article topic cannot be empty")
        return

    initial_state: ArticleWorkFlowState = {
        "topic": topic,
        "plan_file": "",
        "research_file": "",
        "draft_file": "",
        "final_file": ""
    }

    print("\n Starting the multi-agent article writing workflow...")

    try:
        final_state = article_workflow.invoke(initial_state)
        print("\n\nWorkflow completed\n")
        #print(f"Final state: {final_state}\n")
        print(f"The final file is: {final_state["final_file"]}")

    except Exception as e:
        print(f"The workflow failed. Exception occurred is: {e}")


if __name__=="__main__":
    main()