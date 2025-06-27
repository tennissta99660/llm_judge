import pandas as pd

# Read the input Excel file
df = pd.read_excel('Excel_format_result.xlsx')

# Drop unwanted columns
df = df.drop(columns=['prompt', 'llm_response'])

# If you want to clean up the 'decision' column (remove "Correctness: " prefix)
df['decision'] = df['decision'].str.replace('Correctness: ', '')

# Optionally, rename 'decision' to 'Correctness' to match your demo_mandi_data column name
# (demo_mandi_data does not have a 'decision' column, but for your request, you want a dedicated column for decision)
df = df.rename(columns={'decision': 'Correctness'})

# Save the result to a new Excel file
df.to_excel('updated_mandi_data.xlsx', index=False)
