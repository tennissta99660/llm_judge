import json
import asyncio
import os
from typing import List, Dict, Any
import google.generativeai as genai

YOUR_PROMPT = """
Your task is to determine the correctness of an answer to a given question by assigning a label (Correct, Partially Correct, Incorrect or Data Unavailable) based on the problem description provided. 

 A small description of the labels is given as: 

Correct: The response contains accurate and relevant weather or climate information that directly addresses all aspects of the question, including specific variables (such as temperature, precipitation, AQI, wind speed, etc.), for the requested location and time frame. 

Partially Correct: The response contains either some correct information to the question, or it contains information about only a part of the question. 
 
 Incorrect: The response contains significant inaccuracies, irrelevant content, or completely misses the main context of the reference answer. 

Data Unavailable: Data regarding the question either could not be retrieved or was not available.  

Reply with one of the following only: 

 Correctness: Correct 

 Correctness: Data Unavailable  

 Correctness: Incorrect 

 Correctness: Data Unavailable 

 

 Example 1 

Question: What is the chance of rain in Guwahati today? 

 Reference Answer: The weather forecast for Guwahati today indicates [ light rain expected at 6:00 PM with 40% chance of precipitation]. 

Predicted Answer: chances of rain in Guwahati: There is light rain expected at 6:00 PM today with a 40% chance of precipitation. Moderate rain is expected at 9:00 PM today with a 100% chance of precipitation. There is light rain expected at 12:00 AM tomorrow with a 100% chance of precipitation. 

 Correctness: Correct  

Example 2:  

Question: How hot will it be in Delhi today and tomorrow? 

 Reference Answer: The forecast for Delhi today predicts a high temperature of around [34.44°C and 37.58°C] and around [34.98°C and 38.29°C]. 

 Predicted Answer: The temperature in Delhi today will be between 34.44 and 37.58 degrees Celsius. There is also a chance of light rain. 

Correctness: Partially Correct 
 
Example 3: 

 Question: Is it sunny in Chandigarh now? 

 Reference Answer: Checking the weather for Chandigarh: [is sunny in Chandigarh with a temperature of 37.4 degrees Celsius]. 

Predicted Answer: No, Chandigarh is expected to go through a hailstorm in the next hour 

Correctness: Incorrect  

Example 4:  

Question: What's the weather forecast for Kaliapani block in Jorhat? 

 Reference Answer: The weather report for Kaliapani block in Jorhat district predicts light rain 

 Predicted Answer: I cannot fulfill this request. The weather tool requires a city name, and "Kaliapani block in Jorhat" does not fit that format. I need a specific city to provide a weather forecast. 

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