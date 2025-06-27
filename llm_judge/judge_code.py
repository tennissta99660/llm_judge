import json
import asyncio
import os
from typing import List, Dict, Any
import google.generativeai as genai

YOUR_PROMPT = """
Your task is to determine the correctness of an answer to a given question by assigning a label (Correct, Partially Correct,  Incorrect or Data Unavailable) based on the problem description provided.

A small description of the labels is given as:

Correct: The response contains the correct values for either or all of the modal, minimum, or maximum prices of commodities

Partially Correct: The response contains correct values of either of the modal, minimum or maximum prices of commodities.

Incorrect: The response contains all the wrong values of the modal, minimum and maximum prices of commodities.

Data Unavailable: Data regarding the question either could not be retrieved or was not available.

Reply with one of the following only:

Correctness: Correct

Correctness: Partially Correct

Correctness: Incorrect

Correctness: Data Unavailable

Examples

Example 1:
Question: Get the price for Beetroot in Cherthala market, Kerala.
Reference Answer: The modal price for Beetroot in Cherthala market is [Rs. 4100] per quintal. The minimum price is [Rs. 4000] and the maximum price is [rs. 4200]
Predicted Answer: The modal price for Beetroot in Cherthala market, Kerala is Rs 4100 per quintal.
Correctness: Correct

Example 2:
Question: Current Ginger(Dry) price in Gurdaspur, Punjab?
Reference Answer: The modal price for Ginger(Dry) in Gurdaspur market is [Rs. 3200] per quintal. The price range is between [Rs.3000] (minimum) and [Rs. 3500] (maximum)
Predicted Answer: The modal price for Ginger(Dry) in Gurdaspur market is [Rs 3200] per quintal. The price range is between [Rs 1000(minimum) and [Rs 4500] (maximum)
Correctness: Partially Correct

Example 3:
Question: Get the price for Capsicum in Gurdaspur market, Gurdaspur district.
Reference Answer: The modal price for Capsicum in Gurdaspur market is [Rs. 2300] per quintal. The minimum price is [Rs. 2000] and the maximum price is [Rs. 2500]
Predicted Answer: The price of Capsicum (Other variety, FAQ grade) in Gurdaspur market, Gurdaspur district, Punjab is Rs 4300 per quintal on 20/02/2025. The price range was between Rs 4000 to Rs 5500 per quintal.
Correctness: Incorrect

Example 4:
Question: What's the Elephant Yam (Suran) rate in Parassala mandi?
Reference Answer: Elephant Yam (Suran) in Parassala mandi is priced with a modal value of [Rs. 3800] per quintal. The minimum is [Rs. 3800] and the maximum is [Rs. 4000]
Predicted Answer: My apologies, I couldn't find the data about Elephant Yam in Parassala mandi. Would you like me to check the price in another market or for a different commodity?
Correctness: Data Unavailable

Example 5:
Question: What is the price of Coconut in the Pampady market, Kottayam?
Reference Answer: In Pampady market, Kottayam (Kerala), the modal price for Coconut (Other variety, FAQ grade) stands at [Rs. 7500] per quintal. The minimum price is [Rs. 7000] and the maximum is [Rs. 8000]
Predicted Answer: In Pampady market, Kottayam (Kerala), the modal price for Coconut (Other variety, FAQ grade) stands at [Rs. 9500] per quintal. The minimum price is [Rs. 7000] and the maximum is [Rs. 8000]
Correctness: Partially Correct

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
