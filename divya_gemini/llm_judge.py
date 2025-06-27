import json
import asyncio
import os
from typing import List, Dict, Any
import google.generativeai as genai

YOUR_PROMPT = """
Your task is to determine the correctness of an answer to a given question
by assigning a label (Correct, Partially Correct, Incorrect or Data
unavailable) based on the problem description provided.
A small description of the labels is given as:

Correct: The response contextually closely matches the reference answer, with
accurate recommendations. Includes specific product names, dosages, and
practices.

Partially Correct: The response contains some relevant
information, such as general advice or cultural practices, but lacks key
details or specificity like recommending videos when asked or the reference_answer is empty.

Incorrect: The response contains significant inaccuracies, irrelevant
content, or completely misses the context of the reference answer.

Data Unavailable: Data regarding the question could not be retrieved
or was not available or couldn't provide specific data but some general information or if prdicted_answer is empty.

Reply with one of the following only:

Correctness: Correct

Correctness: Data Unavailable

Correctness: Incorrect

Correctness: Data Unavailable

Examples

Example 1:
input: What nutrients are important for flowering in mango?

reference_answer: Besides balanced NPK, micronutrients like Boron and
Zinc are important for good flowering and fruit set in mango. Plant growth
regulators can also sometimes be used.

predicted_answer: To ensure good flowering in mango trees, it is essential
to provide the right nutrients. Here are the key nutrients that play a vital role
in mango flowering: 1. Nitrogen (N): - Role: Nitrogen is crucial for
vegetative growth and overall tree health. However, excessive nitrogen can
promote vegetative growth at the expense of flowering. - Application:
Apply nitrogen fertilizers judiciously, especially during the early stages of
growth. Reduce nitrogen application as the tree approaches the flowering
stage. 2. Phosphorus (P): - Role: Phosphorus is essential for flower
initiation and development. It enhances root growth and energy transfer
within the plant. - Application: Phosphorus should be applied before the
flowering season to promote flower bud formation. 3. Potassium (K): -
Role: Potassium improves the quality of flowers and fruits. It also enhances
the plant&#39;s resistance to diseases and stress. - Application: Apply
potassium fertilizers regularly, as it is essential throughout the growth and
flowering stages. 4. Magnesium (Mg): - Role: Magnesium is a component
of chlorophyll and is vital for photosynthesis, which indirectly supports
flowering. - Application: Ensure adequate magnesium levels, especially in
soils that are deficient in this nutrient. 5. Calcium (Ca): - Role: Calcium is
important for cell wall formation and overall plant structure, which supports
healthy flowering. - Application: Maintain sufficient calcium levels in the
soil, as it is crucial for plant health and flowering. 6. Micronutrients: - Zinc
(Zn): Essential for growth hormone production and flower development. -
Iron (Fe): Important for chlorophyll formation and overall plant health. -
Manganese (Mn): Involved in photosynthesis and enzyme activation. -
Boron (B): Crucial for pollen germination and flower development.

Correctness: Correct

Example 2:
input: What flowering hormone can I use for ridge gourd in Jorhat
Central?

reference_answer: To promote flowering in ridge gourd, you can apply
plant growth regulators like Power-M at a rate of 2 ml per litre of water at 7-
10 day intervals, or alternatively use products like Sagarika.

predicted_answer: For Ridge Gourd in Jorhat Central, Assam: -
Flowering Hormone: - Gibberellic Acid (GA3): - Usage: 20-30 ppm
concentration. - Application: Spray during the vegetative stage to promote
flowering. - Additional Tips: - Ensure adequate watering and sunlight. -
Maintain soil pH between 6.0 and 7.5. - regular pest and disease
management practices.

Correctness: Partially Correct

Example 3:
input: What plant protection measures are needed for pomegranate in
Pub-Mangaldai, Darrang?

reference_answer: For insect pests in pomegranate, you can use
insecticides like Profex Super or Dragon at 2ml/litre. Emamectin Benzoate
(Emacto) at 2gm/litre can also be used at 10-day intervals. For promoting
flowering and fruit set, plant hormones like Power-M (10 ml per 16 Ltr spray
tank) can be applied during flowering

predicted_answer: Pomegranate does not require any protection measures.
Just grow it in a cold climate.
Correctness: Incorrect

Example 4:
input: What fertilizer should I use for wheat?

reference_answer: Fertilizer requirements for wheat depend on your soil
test results. Generally, a balanced application of Nitrogen (often in split
doses), Phosphorus, and Potassium is recommended.

predicted_answer: I am sorry but I am unable to fetch the information
regarding the fertilizers you need for wheat crop. Please try again.

Correctness: Data Unavailable

Example 5:
input: Suggest fertilizers for sandy loam soil for bajra cultivation near Rayadurg,
Anantapur. Show tutorial videos for bajra sowing. What is the current date?

reference_answer: For bajra cultivation in sandy loam soil near Rayadurg, Anantapur, fertilizer recommendations include [Simulated Fertilizer Recommendation for Bajra on Sandy Loam Soil].
I can help you find tutorial videos for bajra sowing. The current date is [Current Date]

predicted_answer: For sandy loam soil in the Anantapur region for Bajra cultivation, consider these fertilizer recommendations:  *   **Nitrogen fertilizers:** Urea, Ammonium Sulphate, or Calcium Ammonium Nitrate *   **Phosphorus fertilizers:** Single Super Phosphate (SSP) or Di-ammonium Phosphate (DAP) *   **Potassium fertilizers:** Muriate of Potash (MOP)  Here are some tutorial videos on how to sow Bajra crop:
*   [Grow Bajra from seeds || Grow millet in containers - YouTube](https://www.youtube.com/watch?v=DruBvjZpTtw) *   [How to grow and care bajra at home /pearl millet - YouTube](https://www.youtube.com/watch?v=uQx5J-bh-LA) *   [How to Grow Pearl Millet (Bajra): A Step-by-Step Farming Guide]
(https://www.youtube.com/watch?v=0C25VazpL7s)  Today's date is 2025-06-03. 

Correctness: Partially Correct

Example 6:
input: What nutrients are important for flowering in mango?

reference_answer: Besides balanced NPK, micronutrients like Boron and Zinc are important for 
good flowering and fruit set in mango. Plant growth regulators can also sometimes be used.

predicted_answer: While I cannot directly provide a list of nutrients for flowering in mangoes, I can suggest some helpful resources. I can search for tutorial videos on mango flowering and nutrient management using the search query "nutrients for flowering in mango" 
to provide you with visual and expert guidance. Would you like me to do that? 

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

    async def get_judgment(self, input, reference_answer,  predicted_answer):
        prompt = YOUR_PROMPT.format(
            input=input,
            reference_answer=reference_answer,
            predicted_answer= predicted_answer
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
    results_fertilizer = []
    for entry in data:
        judgment = await judge.get_judgment(
            entry["input"],
            entry["reference_answer"],
            entry["predicted_answer"]
        )
        entry.update(judgment)
        results_fertilizer.append(entry)
        await asyncio.sleep(5)
    write_to_jsonl(output_path, results_fertilizer)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input .jsonl file")
    parser.add_argument("--output", type=str, required=True, help="Output .jsonl file")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    asyncio.run(judge_all(data, args.output))
