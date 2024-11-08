preselected_genres = [
    'Pop', 'Rock', 'Hip Hop', 'Country', 'Jazz', 'Classical', 
    'Electronic', 'Metal', 'R&B', 'Reggae', 'Indie', 'Soul', 'Other'
]

def map_genre(genres):
    # If genres is 'Unknown' or empty, return 'Other'
    if genres == ['Unknown'] or not genres:
        return 'Other'
    # Initialize an empty set to avoid duplicates
    mapped_genres = set()
    for genre in genres:
        genre_lower = genre.lower()
        if 'pop' in genre_lower:
            mapped_genres.add('Pop')
        if 'rock' in genre_lower:
            mapped_genres.add('Rock')
        if 'hip hop' in genre_lower or 'rap' in genre_lower:
            mapped_genres.add('Hip Hop')
        if 'country' in genre_lower:
            mapped_genres.add('Country')
        if 'jazz' in genre_lower:
            mapped_genres.add('Jazz')
        if 'classical' in genre_lower:
            mapped_genres.add('Classical')
        if 'electronic' in genre_lower or 'edm' in genre_lower:
            mapped_genres.add('Electronic')
        if 'metal' in genre_lower or 'thrash' in genre_lower:
            mapped_genres.add('Metal')
        if 'r&b' in genre_lower or 'soul' in genre_lower:
            mapped_genres.add('R&B')
        if 'reggae' in genre_lower:
            mapped_genres.add('Reggae')
        if 'indie' in genre_lower:
            mapped_genres.add('Indie')
        if 'emo' in genre_lower:
            mapped_genres.add('Rock')
        if 'singer-songwriter' in genre_lower:
            mapped_genres.add('Pop')
        # Add more conditions as needed
    # If no genres were matched, return 'Other'
    if not mapped_genres:
        return 'Other'
    else:
        # If multiple genres matched, you can decide to keep them all or select one
        return ', '.join(mapped_genres)