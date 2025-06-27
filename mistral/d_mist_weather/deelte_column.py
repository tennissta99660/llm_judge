import pandas as pd

df = pd.read_excel('output_weather_mist.xlsx')

if 'prompt' in df.columns:
    df = df.drop(columns=['prompt'])
if 'decision' in df.columns:
    df = df.drop(columns=['decision'])
df.to_excel('output_without_prompt_w_mist.xlsx', index=False)
