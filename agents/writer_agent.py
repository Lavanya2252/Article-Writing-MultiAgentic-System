
from pathlib import Path
from qwen_service import ask_qwen


def write_article(topic, article_plan, research_notes):
    """Write an article using the plan and research notes."""

    
    prompt = f"""
        You are a professional article writer.

        Write the final article about: {topic}

        ARTICLE PLAN:
        {article_plan}

        RESEARCH NOTES:
        {research_notes}

        STRICT OUTPUT RULES:
        1. Output only the finished article in Markdown.
        2. Begin with the article title.
        3. Do not include your reasoning, thoughts, planning,
        analysis, self-talk, or commentary about the task.
        4. Do not describe what the user wants.
        5. Do not explain how you intend to write the article.
        6. Do not invent facts, statistics, studies, quotations,
        or source details.
        7. Use the supplied research notes for factual claims.
        8. Preserve relevant source URLs near the claims they support.
        9. Follow the plan's section order and include its six sections.
        10. Write a complete introduction, body, and conclusion.
        11. If the research does not support a claim, qualify it
            or state that further verification is needed.
        12. Finish the article itself. Do not add a postscript
            describing the writing process.

        Return only the final article.
        """

    return ask_qwen(prompt)


if __name__ == "__main__":
    topic = input("Enter your article topic: ")

    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    output_folder = PROJECT_ROOT / "output"
    output_folder.mkdir(parents=True, exist_ok=True)
    file_name = topic.lower().replace(" ", "_")

    # Read the Planner's output.
    plan_file = output_folder / f"plan_{file_name}.md"

    # Read the Researcher's output.
    research_file = output_folder / f"research_notes_{file_name}.md"

    if not plan_file.exists():
        print("Article plan not found:", plan_file.resolve())
        print("Run planner_agent.py and save its output first.")
        raise SystemExit(1)

    if not research_file.exists():
        print("Research notes not found:", research_file.resolve())
        print("Run researcher_agent.py first.")
        raise SystemExit(1)

    # Read the input files.
    article_plan = plan_file.read_text(encoding="utf-8")
    research_notes = research_file.read_text(encoding="utf-8")

    print("Qwen is writing your article. Please wait...\n")

    # Generate the article.
    article = write_article(
        topic,
        article_plan,
        research_notes
    )

    # Save the Writer's output.
    output_file = output_folder / f"article_{file_name}_draft.md"

    output_file.write_text(
        article,
        encoding="utf-8"
    )

    print(f"\nArticle draft saved to:\n{output_file.resolve()}")