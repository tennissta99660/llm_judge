import pandas as pd
import re

allowed = [
    "Correct",
    "Partially Correct",
    "Incorrect",
    "Data Unavailable",
     "Correct",
    "Incorrect",
    "Data Unavailable",
    "Partially Correct"
]

def extract_label(output):
    if not isinstance(output, str):
        return ""
    output = output.strip()
     # Split into lines, ignore empty lines
    lines = [l.strip() for l in output.splitlines() if l.strip()]
    if not lines:
        return ""
    first_line = lines[0]
    for a in allowed:
        if re.match(rf"^{re.escape(a)}\b", output, re.IGNORECASE):
            return a
    return "Incorrect"

# Load your Excel file
df = pd.read_excel("output_without_prompt_yt_misy.xlsx")

# Overwrite 'llm_response' with just the extracted label
df["llm_response"] = df["llm_response"].apply(extract_label)

# Save to a new Excel file
df.to_excel("output_labels_only_yt.xlsx", index=False)
