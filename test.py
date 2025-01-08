import pandas as pd

data = {
    'Laptop': {'2024': 7831880.88, '2023': 8756357.69, '2022': 8276895.65, '2021': 5946358.09, '2020': 4584795.97, '2019': 4789686.02, '2018': 3824776.68},
    'Cocoa beverage': {'2024': 8707539.44, '2023': 8697883.62, '2022': 7194057.11, '2021': 3633477.29, '2020': 5108264.49, '2019': 5053386.9, '2018': 4887785.05},
    # Add more items here...
}

# Convert dictionary to Pandas DataFrame
df = pd.DataFrame.from_dict(data, orient='index')  # Keys become rows (products)

# Calculate the average for each product
product_averages = df.mean(axis=1)

print("Average sales for each product:")
print(product_averages)
