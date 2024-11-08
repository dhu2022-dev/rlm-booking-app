import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from map_genres import map_genre

df = pd.read_csv(('old_flask_app/Data/combined_output.csv'))

print("Initial DataFrame:")
print(df.head())

print("\nData Cleaning:")

#replace 'No events', 'No price', and 'Unknown' with NaN
df['ticket_sales'] = df['ticket_sales'].replace(['No events', 'Unknown'], np.nan)
df['ticket_price'] = df['ticket_price'].replace(['No price', 'Unknown'], np.nan)
df['followers'] = df['followers'].replace('Unknown', np.nan)  # Add this line

#remove commas from 'followers' and convert to numeric
df['followers'] = df['followers'].astype(str).str.replace(',', '')
df['followers'] = pd.to_numeric(df['followers'], errors='coerce')
print("Converted 'followers' to numeric.")

#convert 'ticket_price' to float
df['ticket_price'] = pd.to_numeric(df['ticket_price'], errors='coerce')
print("Converted 'ticket_price' to float.")

#handle missing values in 'genre' by filling with 'Unknown'
df['genre'] = df['genre'].fillna('Unknown')
print("Filled missing 'genre' values with 'Unknown'.")

#split 'genre' into a list
df['genre_list'] = df['genre'].str.split(', ')
print("Split 'genre' into lists.")

#apply the mapping function
df['mapped_genre'] = df['genre_list'].apply(map_genre)

#display the DataFrame with the new 'mapped_genre' column
print(df[['artist_name', 'genre', 'mapped_genre']])
#display the cleaned DataFrame
print("\nCleaned DataFrame:")
print(df.head())

print("\nDescriptive Statistics:")
print(df.describe(include='all'))

sns.set_theme(style="whitegrid")


# Plotting Popularity Distribution
plt.figure(figsize=(8, 6))
sns.histplot(df['popularity'], color='blue')
plt.title('Popularity Distribution')
plt.xlabel('Popularity')
plt.ylabel('Frequency')
plt.show()

plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='popularity', y='followers', hue='artist_name', s=100)
plt.title('Followers vs. Popularity')
plt.xlabel('Popularity')
plt.ylabel('Followers')
plt.legend(title='Artist')
plt.show()

plt.figure(figsize=(6, 4))
corr = df[['popularity', 'followers', 'ticket_price']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.show()


from collections import Counter
genre_counts = Counter()
for genres in df['genre_list']:
    genre_counts.update(genres)
genre_df = pd.DataFrame.from_dict(genre_counts, orient='index', columns=['count']).reset_index()
genre_df = genre_df.rename(columns={'index': 'genre'})

plt.figure(figsize=(12, 6))
sns.barplot(data=genre_df.sort_values(by='count', ascending=False), x='genre', y='count', palette='viridis')
plt.title('Genre Frequency')
plt.xlabel('Genre')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.show()