import pandas as pd
#rom sklearn.preprocessing import MultiLabelBinarizer

#define mapping rules as (simplified_category, [list of keywords])
mapping_rules = [
    ('rock',        ['rock', 'post-punk', 'grunge', 'garage rock', 'indie rock', 'album rock', 'classic rock', 'modern rock', 'progressive rock', 'art rock', 'new wave']),
    ('pop',         ['pop', 'art pop', 'baroque pop', 'synthpop']),
    ('country',     ['americana', 'alt country', 'roots rock', 'red dirt', 'country', 'bluegrass', 'newgrass', 'acoustic country', 'singer-songwriter']),
    ('hiphop',      ['rap', 'hip hop', 'g-funk', 'underground hip hop', 'country hip hop', 'gangsta rap']),
    ('electronic',  ['electronic', 'dance', 'edm', 'dubstep', 'glitch', 'drum and bass', 'techno', 'house', 'chillstep', 'trip hop']),
    ('jazz',        ['jazz', 'bebop', 'fusion', 'acid jazz', 'nu jazz', 'vocal jazz', 'jazz funk']),
    ('blues',       ['blues', 'modern blues', 'blues rock', 'soul blues']),
    ('reggae',      ['reggae', 'rocksteady', 'roots reggae', 'dub']),
    ('metal',       ['metal', 'heavy metal', 'metalcore', 'gothic metal', 'nu metal', 'alternative metal', 'thrash metal', 'stoner rock', 'doom metal', 'sludge metal', 'progressive metal']),
    ('punk',        ['punk', 'hardcore punk', 'pop punk', 'emo', 'skate punk']),
    ('folk',        ['folk', 'indie folk', 'folk pop', 'acoustic folk']),
    ('world',       ['k-pop', 'j-pop', 'soca', 'calypso', 'latin jazz', 'riddim']),
    ('other',       ['childrens music', 'comedy', 'spoken word', 'opera', 'classical', 'christmas', 'musicals', 'exotica'])
]

def simplify_genres(genre_string):
    """
    Given a detailed genre string (with genres separated by commas),
    return a list of simplified genres based on the mapping_rules.
    """
    if pd.isnull(genre_string):
        return []
    
    #split the string by commas and strip whitespace; make lowercase for matching.
    tokens = [token.strip().lower() for token in genre_string.split(',')]
    simplified_set = set()  # use a set to avoid duplicates
    
    #for each token check against each mapping rule.
    for token in tokens:
        for category, keywords in mapping_rules:
            #if any keyword appears in the token, assign that simplified category.
            if any(keyword in token for keyword in keywords):
                simplified_set.add(category)
                break
    return list(simplified_set)

df = pd.read_csv('artist_shows.csv')

#apply the function to create a new column 'simplified_genres'
df['simplified_genres'] = df['combined_genres'].apply(simplify_genres)


print(df.head())