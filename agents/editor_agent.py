import re
from pathlib import Path

from qwen_service import ask_qwen


def remove_thinking(text):
    """
    Remove explicit model thinking blocks and common
    reasoning prefixes from the model's response.
    """

    if not text:
        return ""

    text = text.strip()

    # Remove complete <think>...</think> blocks.
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Remove an unfinished <think> block.
    # This can occur if the model response is truncated.
    text = re.sub(
        r"<think>.*$",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    # If a closing think tag remains without an opening tag,
    # keep only the content after the last closing tag.
    if re.search(r"</think>", text, flags=re.IGNORECASE):
        text = re.split(
            r"</think>",
            text,
            flags=re.IGNORECASE
        )[-1]

    # Remove common final-answer labels.
    text = re.sub(
        r"^\s*(?:final answer|final article|"
        r"edited article|revised article)\s*:?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # If the model puts untagged reasoning before a Markdown
    # article title, start from the first heading.
    # This assumes the article title is formatted as Markdown.
    heading = re.search(
        r"(?m)^#{1,2}\s+\S.*$",
        text
    )

    if heading:
        text = text[heading.start():]

    # Remove a common introductory sentence.
    text = re.sub(
        r"^\s*(?:here is|below is)\s+"
        r"(?:the\s+)?(?:final|edited|revised)\s+"
        r"article\s*:?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


def edit_article(topic, article, research_notes):
    """Edit an article and return the final article only."""

    # Clean the original draft before sending it to the model.
    article = remove_thinking(article)

    prompt = f"""
You are a professional article editor.

Your task is to produce the final, publication-ready
article about: {topic}

ORIGINAL ARTICLE:
{article}

RESEARCH NOTES:
{research_notes}

EDITING REQUIREMENTS:

1. Preserve the article's main purpose and useful ideas.
2. Improve grammar, clarity, readability, and flow.
3. Remove repetition, irrelevant content, and unnecessary wording.
4. Keep headings logical and sections well organized.
5. Check factual claims against the supplied research notes.
6. Do not invent facts, statistics, studies, or quotations.
7. Preserve relevant source URLs and their context.
8. Qualify claims that cannot be verified from the notes.
9. Remove reasoning, self-talk, planning notes, and task commentary.
10. Never include any content from <think> blocks.
11. Do not describe the editing process or explain your changes.
12. Do not include a preface, an afterword, or a change summary.
13. Preserve important information and relevant citations.
14. Write a suitable title, introduction, organized body sections,
    and conclusion, where appropriate.

STRICT OUTPUT RULES:

- Return ONLY the complete final article in Markdown.
- Start directly with the article title.
- Format the title as a Markdown H1 heading using #.
- Do not include analysis or reasoning before the title.
- Do not include commentary after the conclusion.
- Do not write "Here is the revised article."
- Do not include labels such as "Final Answer" or "Edited Article".
- Do not include <think> tags or their contents.
- Do not invent unsupported claims.

Your entire response must be the final article and nothing else.
"""

    # Ask the local Qwen model to edit the article.
    response = ask_qwen(prompt)

    # Clean the model response.
    edited_article = remove_thinking(response)

    # Prevent an empty or unusable result from being saved.
    if not edited_article:
        raise ValueError(
            "The editor returned an empty article. "
            "Check the Qwen response and qwen_service.py."
        )

    # Remove leading and trailing whitespace.
    return edited_article.strip() + "\n"


def main():
    """Run the article editor."""

    topic = input("Enter your article topic: ").strip()

    if not topic:
        print("Error: Article topic cannot be empty.")
        return

    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    output_folder = PROJECT_ROOT / "output"
    output_folder.mkdir(parents=True, exist_ok=True)

    topic_slug = topic.lower().replace(" ", "_")

    # Read the Writer's output.
    article_file = (
        output_folder / f"article_{topic_slug}_draft.md"
    )

    # Read the Researcher's output.
    research_file = (
        output_folder / f"research_notes_{topic_slug}.md"
    )

    if not article_file.exists():
        print("\nArticle draft not found:")
        print(article_file.resolve())
        print("\nRun writer_agent.py first.")
        return

    if not research_file.exists():
        print("\nResearch notes not found:")
        print(research_file.resolve())
        print("\nRun researcher_agent.py first.")
        return

    # Read source files.
    article = article_file.read_text(encoding="utf-8")
    research_notes = research_file.read_text(encoding="utf-8")

    print("\nQwen is editing the article. Please wait...\n")

    try:
        edited_article = edit_article(
            topic,
            article,
            research_notes
        )

        # Save only the final edited article.
        output_file = (
            output_folder / f"edited_article_{topic_slug}.md"
        )

        output_file.write_text(
            edited_article,
            encoding="utf-8"
        )

        print("Article editing completed successfully.")
        print(f"\nEdited article saved to:\n{output_file.resolve()}")

    except Exception as error:
        print(f"\nError while editing the article: {error}")
if __name__ == "__main__":
    main()