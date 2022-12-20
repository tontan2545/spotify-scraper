import pandas as pd


def remove_duplicates():
    playlist_metadata = pd.read_csv("data/playlist_metadata.csv")
    track_metadata = pd.read_csv("data/track_metadata.csv")
    album_metadata = pd.read_csv("data/album_metadata.csv")
    artist_metadata = pd.read_csv("data/artists_metadata.csv")
    print("Shape before dropping")
    print(playlist_metadata.shape)
    print(track_metadata.shape)
    print(album_metadata.shape)
    print(artist_metadata.shape)

    playlist_metadata = playlist_metadata.drop_duplicates(subset="track_id")
    track_metadata = track_metadata.drop_duplicates(subset="id")
    album_metadata = album_metadata.drop_duplicates(subset="id")
    artist_metadata = artist_metadata.drop_duplicates(subset="id")

    print("Shape after dropping")
    print(playlist_metadata.shape)
    print(track_metadata.shape)
    print(album_metadata.shape)
    print(artist_metadata.shape)

    playlist_metadata.to_csv("data/playlist_metadata.csv", index=False)
    track_metadata.to_csv("data/track_metadata.csv", index=False)
    album_metadata.to_csv("data/album_metadata.csv", index=False)
    artist_metadata.to_csv("data/artists_metadata.csv", index=False)

