import json
import asyncio
import os
from typing import List, Dict, Any
import google.generativeai as genai

YOUR_PROMPT = """
Your task is to determine the correctness of an answer to a given question by assigning a label (Correct, Partially Correct,  Incorrect or Data Unavailable) based on the problem description provided. 

 A small description of the labels is given as: 

 Correct: The response contains YouTube video links that are relevant to the topic asked, such as crop tutorials, pesticide usage, fertilizer application, or farming practices. 

 Partially Correct: The response contains either some useful and relevant information or either Youtube video links only 

 Incorrect: The response contains significant inaccuracies, irrelevant content, or completely misses the main intent of the reference answer. 

Data Unavailable: Data regarding the question either could not be retrieved or was not available.  

Reply with one of the following only: 

 Correctness: Correct 

 Correctness: Data Unavailable  

 Correctness: Incorrect 

 Correctness: Data Unavailable 

 

 Example 1 

Question: Find videos on greenhouse farming in India?. 

 Reference Answer: [ --Youtube Embedding Videos --] (Means there must be youtube video links) 

Predicted Answer: Here are some YouTube videos that provide information on greenhouse farming in India:  1. [Polyhouse-Greenhouse Farming in भविष्य की खेती..??🤔 | Polyhouse-Greenhouse Farming in India | #AtoZखेती  | Indian Farmer 2. [The "Greenhouse-in-a-Box" Empowering Farmers in The "Greenhouse-in-a-Box" Empowering Farmers in India | Sathya Raghu Mokkapati | TED Countdown 3. [Polyhouse Farming / Greenhouse Farming | Protected Cultivation | Polyhouse Farming / Greenhouse Farming | Protected Cultivation | Modern Agriculture Technology 

 Correctness: Correct  

Example 2:  

Question: Show me a tutorial on drip irrigation maintenance. 

 Reference Answer: Okay, searching for videos on 'drip irrigation system maintenance'.[-- youtube video-- ] 

 Predicted Answer: Here are some tutorial videos on drip irrigation maintenance: 1. Drip irrigation maintenance - YouTube: This video demonstrates how to perform maintenance on a drip irrigation system to ensure uniformity of irrigation distribution across a vineyard. It shows how to flush your irrigation system and treat it with an oxidizing agent. 2. Drip Irrigation Repair - Poly Tubing Leak - YouTube: This video shows how to repair a leak in drip irrigation poly pipe. 3. How to: Repair Your Irrigation Drip Line - YouTube: This video explains how to repair your irrigation drip line and all of the materials you will need to complete the repair. 

Correctness: Partially Correct 
 
Example 3: 

 Question: Show me some video tutorials on organic pest control for cauliflower 

 Reference Answer: [Youtube Embedding Link] 

Predicted Answer: Use neem oil or garlic extract. These are helpful for pest control. 

Correctness: Incorrect  

Example 4:  

Question: Find a video on turmeric processing. 

 Reference Answer: Okay, searching for videos demonstrating 'turmeric processing methods after harvest'. [-- youtube video-- ] 

 Predicted Answer: Sorry, I couldn't find any videos on turmeric processing. 

Correctness: Data Unavailable 
Now evaluate the following case:

Question: {input}
Reference Answer: {reference_answer}
Predicted Answer: {predicted_answer}

Correctness:
"""

class GeminiAPI:
    def __init__(self, model_name="gemini-2.0-flash-lite"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model_name)

    async def chat(self, messages, temperature=0.0, max_tokens=20):
        prompt = messages[0]["content"]
        # For async compatibility, use asyncio.to_thread
        response = await asyncio.to_thread(self.model.generate_content, prompt)
        return response.text

class CorrectnessJudge:
    def __init__(self, model_name="gemini-2.0-flash-lite"):
        self.model_name = model_name
        self.api = GeminiAPI(model_name)

    async def get_judgment(self, input, reference_answer, predicted_answer):
        prompt = YOUR_PROMPT.format(
            input=input,
            reference_answer=reference_answer,
            predicted_answer=predicted_answer
        )
        output = await self.api.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=20
        )
        label = output.strip()
        allowed = [
            "Correctness: Correct",
            "Correctness: Partially Correct",
            "Correctness: Incorrect",
            "Correctness: Data Unavailable"
        ]
        label = label if label in allowed else "Correctness: Incorrect"
        return {
            "prompt": prompt,
            "llm_response": output,
            "decision": label
        }

def read_jsonl(file_path: str) -> List[Dict[str, Any]]:
    res = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            res.append(json.loads(line.strip()))
    return res

def write_to_jsonl(file_path: str, data: List[Any]) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

async def judge_all(data: List[Dict[str, Any]], output_path: str):
    judge = CorrectnessJudge()
    results = []
    for entry in data:
        judgment = await judge.get_judgment(
            entry["input"],
            entry["reference_answer"],
            entry["predicted_answer"]
        )
        entry.update(judgment)
        results.append(entry)
        await asyncio.sleep(5)
    write_to_jsonl(output_path, results)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input .jsonl file")
    parser.add_argument("--output", type=str, required=True, help="Output .jsonl file")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    asyncio.run(judge_all(data, args.output))