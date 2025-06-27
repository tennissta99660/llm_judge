import pandas as pd
from typing import List, Any
import json

def read_jsonl(file_path: str) -> List[Any]:
    res = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            json_obj = json.loads(line.strip())
            res.append(json_obj)
    return res

def write_to_jsonl(file_path: str, data: List[Any]) -> None:
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            json_line = json.dumps(item, ensure_ascii=False)
            f.write(json_line + '\n')

# Load Excel and convert to list of dicts
df = pd.read_excel('C:/Users/Administrator/Desktop/llm_judge_fertilizer/fertilizer_data.xlsx')
data = df.to_dict(orient='records')

# Write to JSONL
write_to_jsonl('C:/Users/Administrator/Desktop/llm_judge_fertilizer/converted_fertilizer_data.jsonl', data)
