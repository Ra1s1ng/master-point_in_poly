import pandas as pd

df = pd.read_csv("data/Results_Master.csv")
for method in df["Method"].unique():
    method_df = df[df["Method"] == method]
    time_growth_rate = (method_df["Time used in seconds"].iloc[-1] - method_df["Time used in seconds"].iloc[0]) / method_df["Time used in seconds"].iloc[0]
    mem_growth_rate = (method_df["Memory used in MB"].iloc[-1] - method_df["Memory used in MB"].iloc[0]) / method_df["Memory used in MB"].iloc[0]
    print(f"Method: {method}")
    print(f"Time Growth Rate: {time_growth_rate:.4f}")
    print(f"Memory Growth Rate: {mem_growth_rate:.4f}")
    print("-" * 20)

# Calculate correlation coefficient for each method
for method in df["Method"].unique():
    method_df = df[df["Method"] == method]
    correlation = method_df["Time used in seconds"].corr(method_df["Memory used in MB"], method='spearman')  # Use Spearman's rank correlation
    print(f"Method: {method}")
    print(f"Spearman Rank Correlation: {correlation:.4f}")
    print("-" * 20)