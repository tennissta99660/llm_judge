import re
import pandas as pd
allowed = [
    "Correctness: Correct",
    "Correctness: Partially Correct",
    "Correctness: Incorrect",
    "Correctness: Data Unavailable",
    "Correct",
    "Incorrect",
    "Data Unavailable",
    "Partially Correct"
]

def extract_label(output):
    if not isinstance(output, str):
        return ""
    # Split into lines, ignore empty lines
    lines = [l.strip() for l in output.splitlines() if l.strip()]
    if not lines:
        return ""
    first_line = lines[0]
    for a in allowed:
        if re.match(rf"^{re.escape(a)}\b", first_line, re.IGNORECASE):
            return a
    return "Incorrect"
df = pd.read_excel("output_without_prompt_w_mist.xlsx")  # or pd.read_json("your_output.jsonl", lines=True)
df["extracted_label"] = df["llm_response"].apply(extract_label)
df.to_excel("output_with_labels_w.xlsx", index=False)
