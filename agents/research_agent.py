'''
FOR ARTICLE WRITING, THE EXPECTED OUTPUT FROM RESEARCH AGENT IS:
1. EVIDENCE AND KEY FINDINGS
2. SOURCE TITLE AND URLS
3. NOTES LINKED TO RESEARCH QUESTIONS
4. INFORMATION THAT STILL NEEDS VERIFICATION
'''

from qwen_service import ask_qwen
from ddgs import DDGS
from pathlib import Path


def search_web(qn, max_results=5):
    """ Search the web and return a list of search results"""
    web_search_results = []

    with DDGS() as ddgs:
        curr_search_result = ddgs.text(qn, max_results=max_results)

        for i in curr_search_result:
            web_search_results.append({
                "title": i.get("title", ""),
                "url": i.get("href", ""),
                "snippet": i.get("body", ""),
                "question": qn
            })
    return web_search_results


def get_research_results(topic, research_questions):
    """Find web search results and asks Qwen to organize the evidence"""
    all_results = []

    for qn in research_questions:
        print(f"Searching: {qn}")

        try:
            curr_qn_research = search_web(qn)

            for res in curr_qn_research:
                res["research_question"] = qn
                all_results.append(res)

        except Exception as e:
            print(f"Web search failed for the question: {qn}")
            print(f"{e}\n")

    print(len(all_results))
    if not all_results:
        return (
            "No results were retrieved"
            "Check your internet and try again"
        )

    """Prepare the search results to pass to Qwen"""
    research_material = ""

    for index, material in enumerate(all_results, start=1):
        research_material += (
            f"\nSource {index}\n"
            f"Question {material["question"]}\n"
            f"Title {material["title"]}\n"
            f"Url {material["url"]}\n"
            f"Snippet {material["snippet"]}\n"
        )

    prompt = f"""
        You are a careful research assistant preparing notes for an article.

        Article topic: {topic}

        Below are web search results. They are preliminary leads,
        not independently verified evidence.

        {research_material}

        Your tasks:
        1. Organize the useful findings by research question.
        2. Distinguish what the snippets actually say from assumptions.
        3. Highlight claims that require further verification.
        4. Do not invent facts, statistics, quotations, or source details.
        5. Do not claim to have read a full page when only a search
        snippet is available.
        6. Preserve the supplied source titles and URLs.
        7. Flag conflicting or insufficient information.

        Return your notes in readable Markdown.
    """

    research_result = ask_qwen(prompt=prompt)
    source_data = ""
    for i, res in enumerate(all_results):
        source_data += (
            f"\nSource {i},\n" 
            f"Title: {res["title"]},\n" 
            f"Question: {res["question"]}\n"
        )

    return research_result + source_data


if __name__ == "__main__":
    topic = input("Enter the research topic...")
    questions = [
        f"What are the main benefits of the {topic}?",
        f"What are the main challenges and risks of the {topic}?",
        f"What recent evidence or studies discuss the {topic}?"
    ]

    print("Researching the topic....")
    research_points = get_research_results(topic, questions)
    #print(research_points)
    print("Research Completed")

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    
    output_path = PROJECT_ROOT / "output"
    output_path.mkdir(parents=True, exist_ok=True)

    file_name = topic.lower().replace(" ", "_")
    research_result_file = output_path/f"research_notes_{file_name}.md"

    with research_result_file.open("w", encoding="utf-8") as f:
        print("Writing into the research file..")
        f.write(f"RESEARCH TOPIC: {topic}\n\n")
        f.write(research_points)

    print("Research written to file")
