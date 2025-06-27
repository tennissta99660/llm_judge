import json
import asyncio
import aiohttp
import os
from typing import List, Dict, Any

YOUR_PROMPT = """
Your task is to determine the correctness of an answer to a given question
by assigning a label (Correct, Partially Correct, Incorrect or Data
unavailable) based on the problem description provided.
A small description of the labels is given as:
Correct: The response contextually closely matches the reference answer,
with accurate recommendations. Includes specific product names,
dosages, and practices.

Partially Correct: The response contains some relevant information, such
as general advice or cultural practices, but lacks key details or specificity
like recommending videos when asked or the reference_answer is empty.

Incorrect: The response contains significant inaccuracies, irrelevant
content, or completely misses the context of the reference answer

Data Unavailable: Data regarding the question could not be retrieved or
was not available or couldnt provide specific data but some general
information or if prdicted_answer is empty.

Reply with one of the following only:

Correct

Data Unavailable

Incorrect

Data Unavailable

Examples
Example 1:
input: How to control collar rot disease in groundnut?
reference_answer: Collar rot in groundnut is best managed through seed
treatment with fungicides like Thiram or Carbendazim before sowing. Good
field drainage and crop rotation also help reduce incidence.
predicted_answer: Collar rot in groundnut is primarily caused by the fungus
Aspergillus niger. Here are some key points to help you identify, prevent,
and control collar rot in groundnut: ### Identification - Symptoms: -
Yellowing of leaves. - Wilting of the plant. - Dark brown or black lesions at
the soil line on the stem. - Stunted growth. - Eventual death of the plant.
### Prevention - Soil Management: - Avoid planting in poorly drained or
waterlogged soils. - Ensure proper soil drainage. - Crop Rotation: - Rotate
crops to avoid continuous planting of susceptible crops in the same field. -
Sanitation: - Remove and destroy infected plant debris from the field. -
Clean and disinfect farm equipment. ### Control - Chemical Control: -
Fungicides can be effective in managing collar rot. Commonly used
fungicides include: - Thiram - Captan - Carbendazim - Apply fungicides as
a soil drench or as a foliar spray, following the manufacturer&#39;s instructions. -
Biological Control: - Use of biological agents like Trichoderma spp. can
help suppress the fungus. - Cultural Practices: - Maintain optimal plant
spacing to improve air circulation. - Avoid overwatering and ensure proper
irrigation practices. ### Additional Tips - Resistant Varieties: - Choose
groundnut varieties that are resistant to collar rot if available. - Monitoring:
- Regularly inspect your crops for early signs of collar rot and take prompt

action. By following these guidelines, you can effectively manage and
control collar rot in groundnut, ensuring healthier crops and better yields.
Correctness: Correct

Example 2:
input: How to manage anthracnose disease in mango?
reference_answer: Managing anthracnose in mango involves pruning to
improve air circulation, field sanitation, and timely application of fungicides
like Carbendazim or Thiophanate-methyl, especially before and during
flowering
predicted_answer: Managing anthracnose disease in mango involves a
combination of preventive measures and treatment strategies. Here are
some steps you can take: 1. Preventive Measures: - Sanitation: Remove
and destroy infected plant material to reduce the source of inoculum. -
Pruning: Prune trees to improve air circulation and reduce humidity. -
Irrigation Management: Avoid overhead irrigation, especially in the
evening, to keep the leaves dry. 2. Chemical Control: - Fungicides: Use
fungicidal sprays containing copper-based compounds. These should be
applied at the first sign of disease and repeated at intervals recommended
by the manufacturer. 3. Biological Control: - Biological Agents: Some
biological control agents like Bacillus subtilis and Trichoderma species can
help in managing the disease. 4. Cultural Practices: - Resistant
Varieties: Plant mango varieties that are resistant to anthracnose. - Proper
Spacing: Ensure proper spacing between plants to reduce humidity and
improve air circulation. By combining these strategies, you can effectively
manage anthracnose disease in mango.

Correctness: Partially Correct
Example 3:

input: How to manage pink bollworm in cotton?
reference_answer: Managing pink bollworm in cotton involves using
pheromone traps for monitoring, destroying crop residues after harvest,
adhering to sowing windows, and need-based spraying of recommended
insecticides during the susceptible stage
predicted_answer: The pink bollworm is a worm in ball shaped which
causes plants to degrade.
Correctness: Incorrect
Example 4:
input: What is the dose for &#39;Plaring&#39; insecticide for my tomato plants in
Golaghat West?
reference_answer: Could you please confirm the exact name or active
ingredient of the insecticide? &#39;Plaring&#39; is not a standard recognized name.
Knowing the correct product name or chemical composition is necessary to
provide the accurate dosage information.
predicted_answer: I cannot find &#39;Plaring&#39; in my database of pesticides.
Could you please provide the active ingredient or a more common name for
the insecticide you&#39;re referring to so I can assist you better?

Correctness: Data Unavailable
Example 5:
input: How to manage Downey Mildew in my cucumber crop near
Sheoraphuly, Hooghly? What fungicide works? Check weather. Are there
schemes for protected cultivation (like polyhouses) for cucumbers?
reference_answer: To manage Downey Mildew in your cucumber crop near
Sheoraphuly, Hooghly, consider applying a fungicide like [Simulated
Fungicide Name]. Before application, please check the current weather

forecast for Sheoraphuly. Regarding protected cultivation like polyhouses
for cucumbers, there are [Simulated Info about Government Schemes]
available that you might be eligible for
predicted_answer: Okay, I can help you with managing Downey Mildew in
your cucumber crop, checking the weather in Sheoraphuly, and finding
government schemes for polyhouse cultivation. **Downy Mildew
Management in Cucumbers:** Based on the search results, downy mildew
can be managed through a combination of cultural practices and chemical
treatments. * **Cultural Practices:** Ensure good air circulation, avoid
overhead watering, and remove infected leaves promptly. Do not compost
diseased plants. * **Chemical Control:** Copper fungicides are often used
to control downy mildew. Systemic fungicides are also available, but should
be used after diagnosis. Oxathiapiprolin is approved for use against downy
mildew in the United States. In Canada, a mixture of zoxamide and
mancozeb is registered for control of the mildew. **Weather in
Sheoraphuly:** I am sorry, I am unable to retrieve weather data for
Sheoraphuly at this moment. Please check a reliable weather app or
website for the current conditions and forecast. **Government Schemes
for Polyhouse Cultivation:** There are government schemes to promote
protected cultivation like polyhouses for cucumbers. Please check the
official government websites for detailed information on eligibility criteria,
application procedures, and available subsidies. Since cucumber prices
can influence your decisions, I attempted to fetch the current mandi rates
for cucumbers in Hooghly, West Bengal, but unfortunately, no data was
found in the database. I recommend checking local market sources for the
most up-to-date pricing. To further assist you, I have also provided some
relevant tutorial videos on cucumber farming in polyhouses.
Correctness: Partially Correct.
Example 6:
input: What is the method for controlling insects in Lemon in Rangapara?
reference_answer: For insect control in lemon trees, spray Profenofos 50%
EC insecticide, mixing 1.5 ml of the chemical per litre of water

predicted_answer: I am sorry, I am unable to fetch the pesticide information
for Lemon. I can help you with tutorial videos for controlling insects in
Lemon. Do you want to search for tutorial videos?

Correctness: Data Unavailable

Now evaluate the following case:

Question: {input}
Reference Answer: {reference_answer}
Predicted Answer: {predicted_answer}

Correctness:
"""

class MistralAPI:
    def __init__(self, model_name="mistral-small"):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise EnvironmentError("MISTRAL_API_KEY environment variable not set.")
        self.model_name = model_name
        self.url = "https://api.mistral.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def chat(self, messages, temperature=0.0, max_tokens=64):
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=self.headers, json=payload) as response:
                text = await response.text()
                if response.status != 200:
                    raise Exception(f"Request failed: {response.status}\nPayload: {json.dumps(payload, indent=2)}\nResponse: {text}")
                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()

class CorrectnessJudge:
    def __init__(self, model_name="mistral-small"):
        self.api = MistralAPI(model_name)

    async def get_judgment(self, input, reference_answer, predicted_answer):
        prompt = YOUR_PROMPT.format(
            input=input,
            reference_answer=reference_answer,
            predicted_answer=predicted_answer
        )
        output = await self.api.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=32
        )
        allowed = [
            "Correct",
            "Partially Correct",
            "Incorrect",
            "Data Unavailable"
        ]
        # Extract the first allowed label found in the output
        label = next((a for a in allowed if a in output), None)
        if label is None:
            label = "Incorrect"
        return {
            "prompt": prompt,
            "llm_response": output,
            "decision": label
        }

def read_jsonl(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, "r", encoding="utf-8") as file:
        return [json.loads(line.strip()) for line in file]

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
