import json
import pandas as pd

data = []
with open('results_yt_mist.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

df = pd.DataFrame(data)
df.to_excel('output_yt_mist.xlsx', index=False)