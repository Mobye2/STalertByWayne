import pandas as pd

# Create a sample DataFrame
data = {'x': [5,4,3,2,1],
        'y': [10,8,6,4,2]}
df = pd.DataFrame(data)

# Calculate the slope using the diff() function
df['slope'] = df['y'].diff()
df['60MA'] = df['y'].rolling(window=3).mean()

# Display the DataFrame with the slope column
print(df)