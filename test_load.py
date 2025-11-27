import pandas as pd

df = pd.read_csv("data/sales_data.csv")

print("----- HEAD -----")
print(df.head())

print("\n----- INFO -----")
print(df.info())

print("\n----- SAMPLE ROWS -----")
print(df.sample(5))
