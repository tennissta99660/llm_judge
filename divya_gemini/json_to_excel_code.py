import json
import pandas as pd

# Read the JSON Lines file
data = []
with open('results_fertilizer.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

# Convert to DataFrame
df = pd.DataFrame(data)

# Export to Excel
df.to_excel('output_fertilizer.xlsx', index=False)
