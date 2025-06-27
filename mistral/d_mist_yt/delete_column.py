import pandas as pd

# Read the Excel file
df = pd.read_excel('output_yt_mist.xlsx')

# Drop the 'prompt' column if it exists
if 'prompt' in df.columns:
    df = df.drop(columns=['prompt'])
if 'decision' in df.columns:
    df = df.drop(columns=['decision'])
# Save the updated dataframe to a new Excel file
df.to_excel('output_without_prompt_yt_misy.xlsx', index=False)
