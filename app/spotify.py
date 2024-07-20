import csv
import spotipy

from datetime import datetime, timedelta
from spotipy.oauth2 import SpotifyClientCredentials


def parse_date(date_string):
    formats = ["%Y-%m-%d", "%Y-%m", "%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    raise ValueError(f"Couldn't parse date string {date_string}")


def get_similar_songs(csv_file_path):
    client_credentials_manager = SpotifyClientCredentials(
        client_id="7a5a85a7ab414c0f86af6df7e9dff8c9",
        client_secret="40e648d9e84540fd8d17403ed51948c0",
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    similar_songs = []
    seen_tracks = set()  # to keep track of seen track IDs

    with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
        song_reader = csv.DictReader(csvfile)
        for row in song_reader:
            artist = row["Artist"]
            song_name = row["Title"]

            results = sp.search(
                q="artist:" + artist + " track:" + song_name, type="track"
            )
            tracks = results["tracks"]["items"]
            if tracks:
                track_id = tracks[0]["id"]
                if track_id not in seen_tracks:  # check if track is already seen
                    seen_tracks.add(track_id)

                    recommendations = sp.recommendations(seed_tracks=[track_id], limit=10)

                    for rec in recommendations["tracks"]:
                        rec_track_id = rec["id"]
                        if (
                            rec_track_id not in seen_tracks
                        ):  # check if recommendation is already seen
                            seen_tracks.add(rec_track_id)

                            track_info = sp.track(rec_track_id)
                            release_date = parse_date(track_info["album"]["release_date"])
                            popularity = track_info["popularity"]

                            if release_date >= datetime.now() - timedelta(days=90):
                                if popularity >= 60:
                                    category = "Hot"
                                elif popularity >= 40:
                                    category = "A-List"
                                else:
                                    category = "B-List"
                            elif release_date >= datetime.now() - timedelta(days=300):
                                category = "Recurrent"
                            else:
                                category = "Gold"

                            similar_songs.append(
                                {
                                    "Artist": track_info["artists"][0]["name"],
                                    "Title": track_info["name"],
                                    "Release Date": release_date,
                                    "Popularity": popularity,
                                    "Category": category,
                                }
                            )

    return similar_songs


def write_to_csv(data, csv_file_path):
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Artist", "Title", "Release Date", "Popularity", "Category"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)
        print("Similar Songs Saved To spotify_songs.csv!")
