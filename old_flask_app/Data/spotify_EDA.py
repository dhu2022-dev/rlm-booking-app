import pandas as pd

### INITIAL DATA INSPECTION ###

# Load the data
df = pd.read_csv(('old_flask_app/Data/spotify_data.csv'))

# Preview the data
print(df.head())

# Check data types and non-null counts
print(df.info())

# Check for missing values
print(df.isnull().sum())

### DATA CLEANING ###

# Handling missing values. Current approach: fill w/ median for numerical columns
df.fillna(df.median(), inplace=True)

# Standardize text data (e.g., lowercasing artist names)
df['artist'] = df['artist'].str.lower()

# Outlier Detection (describe to see ranges)
print(df.describe())

### Descriptive Statistics ###

# Summary statistics for numerical columns
print(df.describe())

# Distribution of categories (example for 'genre' columns)
print(df['genre'].value_counts())