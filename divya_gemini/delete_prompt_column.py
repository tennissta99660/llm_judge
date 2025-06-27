import pandas as pd

# Read the Excel file
df = pd.read_excel('output_fertilizer.xlsx')

# Drop the 'prompt' column if it exists
if 'prompt' in df.columns:
    df = df.drop(columns=['prompt'])
if 'llm_response' in df.columns:
    df = df.drop(columns=['llm_response'])
# Save the updated dataframe to a new Excel file
df.to_excel('output_without_prompt_fertilizer.xlsx', index=False)
