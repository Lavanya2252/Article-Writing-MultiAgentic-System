import json
import urllib.request
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:4b"

def ask_qwen(prompt):
    payload =  {
        "model":MODEL_NAME,
        "messages":[
            {
            "role":"user",
            "content":prompt
        }],
        "stream": False,
        "think": False
    }

    print("Accessing Qwen..")
    start = datetime.now()
    print(start)
    request = urllib.request.Request(
        url=OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type":"application/json"}
    )

    with urllib.request.urlopen(request) as response:
        print("Performing the task..")
        result = json.loads(response.read().decode("utf-8"))

    end = datetime.now()
    print(f"Time taken: {end-start}")
    #print(result)
    return result["message"]["content"]

if __name__=="__main__":
    print(ask_qwen("When is India's Independence Day?"))