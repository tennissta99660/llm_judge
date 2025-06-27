import json
import pandas as pd

# Read the JSON Lines file
data = []
with open('results_pest_mist.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

# Convert to DataFrame
df = pd.DataFrame(data)

# Export to Excel
df.to_excel('output_pest_2_mist.xlsx', index=False)
