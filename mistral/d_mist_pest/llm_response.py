import pandas as pd
import re

allowed = [
    "Correct",
    "Partially Correct",
    "Incorrect",
    "Data Unavailable"
]

def extract_label(output):
    if not isinstance(output, str):
        return ""
    output = output.strip()
    for a in allowed:
        if re.match(rf"^{re.escape(a)}\b", output, re.IGNORECASE):
            return a
    return ""

# Load your Excel file
df = pd.read_excel("output_without_prompt_pest_2_mist.xlsx")

# Overwrite 'llm_response' with just the extracted label
df["llm_response"] = df["llm_response"].apply(extract_label)

# Save to a new Excel file
df.to_excel("output_labels_only.xlsx", index=False)
