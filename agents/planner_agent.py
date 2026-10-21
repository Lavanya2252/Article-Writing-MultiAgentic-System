'''
FOR ARTICLE WRITING, THE EXPECTED OUTPUT FROM PLANNER AGENT IS:
1. ARTICLE TITLE
2. INTRODUCTION AND SECTION HEADINGS
3. KEY POINTS FOR EACH SECTION
4. QUESTIONS THE RESEARCHER NEED TO INVESTIGATE
'''

from qwen_service import ask_qwen
from pathlib import Path


def create_article_plan(topic):
    """Create a structured article plan for the given topic"""
    prompt = f"""
        You are an experienced article planning assistant.

        Create a practical plan for an informative article about:
        {topic}

        Include the following:

        1. A clear, engaging article title.
        2. The intended audience.
        3. The main purpose of the article.
        4. An introduction plan.
        5. Six main sections with headings and key points.
        6. A conclusion plan.
        7. Five research questions that need reliable answers.

        Important rules:
        - Keep the outline logical and easy to follow.
        - Avoid repeating the same ideas in different sections.
        - Do not invent statistics, facts, or research findings.
        - List research questions separately so another agent
        can investigate them later.
        - Return the plan in readable Markdown.
    """
    plan = ask_qwen(prompt=prompt)
    return plan

if __name__=="__main__":
    article_topic = input("Enter your article topic...")
    print("Creating the plan....")
    article_plan = create_article_plan(article_topic)
    #print(article_plan)

    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    output_path = PROJECT_ROOT / "output"
    output_path.mkdir(parents=True, exist_ok=True)

    file_name = article_topic.lower().replace(" ", "_")
    plan_result_file = output_path/f"plan_{file_name}.md"

    with plan_result_file.open("w", encoding="utf-8") as f:
        print("Writing into the plan file..")
        f.write(f"PLAN TOPIC: {article_topic}\n\n")
        f.write(article_plan)

    print("Plan written to the file")
    