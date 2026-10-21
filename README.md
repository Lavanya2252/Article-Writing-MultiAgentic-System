# Article-Writing-MultiAgentic-System
A multi-agent system that has the capability to plan, research, write and give the final edited article on a given topic

Approach A — Python + LangGraph:
LangGraph coordinates the Planner, Researcher, Writer and Editor. A good balance between learning and building a reliable workflow. 

Approach B — Custom Python orchestrator:
You write the coordination logic yourself using Python functions, conditions, loops and shared data. Fewer frameworks to install, but more orchestration code to write and maintain.

Approach C — Full stack:
Use self-hosted n8n Community Edition, LangGraph, LangChain, Ollama and Qwen together. Do not subscribe to n8n Cloud or paid AI APIs. Self-hosted n8n Community Edition is free, 
although some advanced features are paid. 

Approach A - Steps:
 
STEP 1: Download Ollama from official website which is the model runner. Helps to load and run the model in local & to communicate with Python code.
Run this cmd in powershell to download & install the latest version of Ollama: irm https://ollama.com/install.ps1 | iex
Use ollama -version to check the version.

STEP 2: Download the model eg. Qwen3:4b, Qwen3.5:4b
Run this cmd in powershell: ollama run qwen3:4b

STEP 3: Check the model if working by asking any query and if answer generated successfully. Note that, the answer can be outdated due to old training data which can be sorted
by passing the necessary resources from web using python and pass it to the context before generating the answer.

STEP 4: Connect Qwen model via Python
i. mkdir "D:\Lav\AI - Learning\Article Writing Multiagent System\article-agent" in powershell to create a new folder
ii. cd "D:\Lav\AI - Learning\Article Writing Multiagent System\article-agent" to navigate to that folder
iii. create a python venv: python -m venv venv_name
iv. choose created python interpreter by "Ctrl+Shift+P" -> Select Interpreter
v. check ollama's local API response works or not in powershell: Invoke-RestMethod http://localhost:11434/api/tags --> here 11434 is default port used by ollama
the response should contain the details about the available/downloaded models
vi. hit the /api/chat url of localhost to converse with Qwen & check if the response is received

STEP 5: CREATE THE PLANNER AGENT
i. write a prompt containing the appropriate instructions for the agent to generate the article plan and hit the ollama api to generate the article plan as response

STEP 6: CREATE THE RESEARCH AGENT
i. install ddgs package (DuckDuckGo) for the web search and retrieve the information in order to feed to the Qwen along with the question
ii. write code to access the internet via ddgs to retrieve 5 results on the given question and research based on the results

STEP 7: CREATE THE WRITER AGENT
i. write the agent to take the plan and research article as input along with topic and write a draft with the help of those inputs.

STEP 8: CREATE THE EDITOR AGENT
i. write the agent to take the research topics and the draft written earlier as input and return the finally edited revised article as output.

STEP 9: IMPLEMENT LANGGRAPH FOR ORCHESTRATION
i. install langgraph & define the article workflow state
ii. Form the node and edges to form the workflow and invoke it to get the expected results

STEP 10: 
