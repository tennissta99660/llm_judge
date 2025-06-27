import json
import pandas as pd

# Read the JSON Lines file
data = []
with open('results_demo.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

# Convert to DataFrame
df = pd.DataFrame(data)

# Export to Excel
df.to_excel('output_mistral_mndi.xlsx', index=False)
