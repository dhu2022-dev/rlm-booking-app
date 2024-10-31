import random
import csv

# List of arbitrary genres
GENRES = ['Pop', 'Rock', 'Hip-Hop', 'Jazz', 'Classical', 'Electronic', 'Country', 'Reggae', 'Blues', 'R&B']

# Function to generate a random artist name
def generate_artist_name():
    first_names = ['Luna', 'Nova', 'Aria', 'Juno', 'Zane', 'Kai', 'Ryder', 'Ava', 'Leo', 'Mila']
    last_names = ['Star', 'Wave', 'Sky', 'Moon', 'Blaze', 'Rex', 'Vale', 'Lux', 'Frost', 'Knight']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Function to generate random artist data
def generate_artist_data(num_artists=100):
    artists_data = []

    for _ in range(num_artists):
        artist_name = generate_artist_name()
        genre = random.choice(GENRES)
        popularity = random.randint(1, 100)  # Popularity score between 1 and 100
        followers = random.randint(500, 1000000) * popularity // 100  # Followers scaled by popularity
        avg_ticket_price = random.randint(20, 150)  # Random ticket price between $20 and $150
        ticket_sales = random.randint(100, 50000) * popularity // 100  # Estimate sales based on popularity
        
        artist = {
            'name': artist_name,
            'genre': genre,
            'popularity': popularity,
            'followers': followers,
            'avg_ticket_price': avg_ticket_price,
            'ticket_sales': ticket_sales
        }
        
        artists_data.append(artist)
    
    return artists_data

# Function to save artist data to CSV
def save_to_csv(artists_data, filename='synthetic_artist_data.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'genre', 'popularity', 'followers', 'avg_ticket_price', 'ticket_sales'])
        writer.writeheader()
        for artist in artists_data:
            writer.writerow(artist)

# Generate and save the artist data
num_artists = 100  # You can change the number of artists you want to generate
artists_data = generate_artist_data(num_artists)
save_to_csv(artists_data)

print(f"Synthetic artist data for {num_artists} artists has been saved to 'synthetic_artist_data.csv'.")
