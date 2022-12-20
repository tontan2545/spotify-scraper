import os

import dotenv
import spotipy
import operator
import pandas as pd
from typing import Dict, List
from spotipy.oauth2 import SpotifyClientCredentials
from functools import reduce
from remove_duplicates import remove_duplicates


def get_artist_id(artist_metadata: List[Dict]):
    return get_artist_id_helper(artist_metadata.copy(), [])


def get_artist_id_helper(artist_metadata: List[Dict], acc: List):
    if len(artist_metadata) == 0:
        return acc
    data = artist_metadata.pop()
    acc.append(data["id"])
    return get_artist_id_helper(artist_metadata, acc)


def get_artist_top_tracks(artist_id: str) -> List[str]:
    tracks = pd.DataFrame(spotify.artist_top_tracks(artist_id, country="TH"))["tracks"].apply(lambda x: pd.Series(x))
    if "id" in tracks:
        return pd.DataFrame(spotify.artist_top_tracks(artist_id, country="TH"))["tracks"].apply(lambda x: pd.Series(x))[
            "id"].tolist()
    return []


def flatten(l: List[List]):
    return [item for sublist in l for item in sublist]


dotenv.load_dotenv()

artist_top_tracks = {}

playlists = ["37i9dQZF1EpewXaL07z711", "37i9dQZF1EplgY7EA1hven", "37i9dQZF1EpPdF7wiPKlU8", "37i9dQZF1EpnyO6bstPQYK", "37i9dQZF1Eplz3YAdlO0sf"]

if __name__ == "__main__":
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    for pl in playlists:
        playlist: Dict = spotify.playlist(pl)

        track_df = pd.DataFrame(playlist["tracks"]["items"])["track"].apply(lambda x: pd.Series(x))

        playlist_metadata = pd.DataFrame()
        playlist_metadata["track_id"] = track_df["id"]
        playlist_metadata["album_id"] = track_df["album"].apply(lambda x: x["id"])
        playlist_metadata["artist_id"] = track_df["artists"].apply(get_artist_id)

        track_metadata = track_df[["id", "duration_ms", "popularity", "track_number", "explicit", "name"]]
        track_metadata["url"] = track_df["external_urls"].apply(lambda x: x["spotify"])

        audio_features_df = pd.DataFrame(spotify.audio_features(track_metadata["id"].tolist()))[
            ["id", "danceability", "energy", "key", "loudness", "speechiness", "acousticness", "instrumentalness",
             "liveness", "valence", "tempo"]]

        track_metadata = track_metadata.merge(audio_features_df, on="id")

        album_metadata = track_df["album"] \
            .drop_duplicates() \
            .apply(lambda x: pd.Series(x))[["id", "release_date", "total_tracks", "album_type"]]

        artist_list = set(reduce(operator.concat, playlist_metadata["artist_id"].tolist()))
        artists_df = pd.DataFrame(spotify.artists(artist_list))["artists"].apply(lambda x: pd.Series(x))

        artist_metadata = artists_df[["id", "name", "popularity", "type", "genres"]]
        artist_metadata["followers"] = artists_df["followers"].apply(lambda x: x["total"])

        for a_id in artist_list:
            artist_top_tracks[a_id] = get_artist_top_tracks(a_id)

        top_tracks_df = playlist_metadata[["track_id", "artist_id"]]
        top_tracks_df["artist_top_tracks"] = top_tracks_df["artist_id"].apply(
            lambda x: flatten(list(map(lambda y: artist_top_tracks.get(y), x))))
        top_tracks_df["is_in_top_tracks"] = top_tracks_df.apply(lambda r: r["track_id"] in r["artist_top_tracks"],
                                                                          axis=1)

        track_metadata = track_metadata.merge(top_tracks_df, left_on="id", right_on="track_id")

        playlist_metadata.to_csv("data/playlist_metadata.csv", index=False, mode='a',
                                 header=not os.path.exists("data/playlist_metadata.csv"))
        track_metadata.to_csv("data/track_metadata.csv", index=False, mode='a',
                              header=not os.path.exists("data/track_metadata.csv"))
        album_metadata.to_csv("data/album_metadata.csv", index=False, mode='a',
                              header=not os.path.exists("data/album_metadata.csv"))
        artist_metadata.to_csv("data/artists_metadata.csv", index=False, mode='a',
                               header=not os.path.exists("data/artists_metadata.csv"))

        remove_duplicates()
