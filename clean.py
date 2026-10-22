import pandas as pd

# 1. Read the Excel file
df = pd.read_excel('data/raw.xlsx')

# 2. Identify the columns that are NOT years
id_cols = ['Country Name', 'Country Code', 'Series Name', 'Series Code']
year_cols = [c for c in df.columns if c not in id_cols]

# 3. Wide to long
long = df.melt(id_vars=id_cols, value_vars=year_cols,
               var_name='year', value_name='value')

# 4. Clean the 'year' column (turns '2000 [YR2000]' into 2000)
long['year'] = long['year'].astype(str).str[:4].astype(int)

# 5. Make value numeric, drop missing values
long['value'] = pd.to_numeric(long['value'], errors='coerce')
long = long.dropna(subset=['value'])

# 6. Rename to simple columns
long = long.rename(columns={'Country Name': 'country', 'Series Name': 'indicator'})
long = long[['country', 'indicator', 'year', 'value']]

# 7. Save the clean file
long.to_csv('data/clean.csv', index=False)
print(f"Success! Saved {len(long)} rows to data/clean.csv")