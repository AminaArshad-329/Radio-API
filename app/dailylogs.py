import csv
import io
from zipfile import ZipFile
import zipfile


# Define category to star rating mapping
category_to_stars = {
    "Hot": 5,
    "A-List": 4,
    "B-List": 3,
    "Recurrent": 2,
    "Gold": 1,
}

sequence = [
    "Top Of Hour Sequence",
    "5 Star",
    "ID - Short",
    "1 Star",
    "ID - Position",
    "3 Star",
    "Chruch & Roll Link",
    "2 Star",
    "Donut ID",
    "Break",
    "Out Of Break Sequence",
    "4 Star",
    "1 Star",
    "5 Star",
    "Chruch & Roll Link",
    "2 Star",
    "ID - Position",
    "4 Star",
    "ID - Short",
    "3 Star",
    "Donut ID",
    "Break",
    "Out Of Break Sequence",
    "2 Star",
    "ID - New Music Spotlight",
    "3 Star",
    "ID - Short",
    "1 Star",
]


# Open the song data file
with open("app/data/spotify_songs.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)

    # Initialize empty lists for different categories
    hot_songs = []
    alist_songs = []
    blist_songs = []
    recurrent_songs = []
    gold_songs = []

    for row in reader:
        artist = row["Artist"]
        title = row["Title"]
        category = row["Category"]

        # Append the song to the appropriate list based on category
        if category == "Hot" and len(hot_songs) < 20:
            hot_songs.append((artist, title, category))
        elif category == "A-List" and len(alist_songs) < 20:
            alist_songs.append((artist, title, category))
        elif category == "B-List" and len(blist_songs) < 20:
            blist_songs.append((artist, title, category))
        elif category == "Recurrent" and len(recurrent_songs) < 50:
            recurrent_songs.append((artist, title, category))
        elif category == "Gold" and len(gold_songs) < 100:
            gold_songs.append((artist, title, category))


# Define functions to format and print song entries
def format_entry(artist, title, category):
    stars = "*" * category_to_stars[category]
    return f"{artist} {stars} - {title}"


# position is used to track position during the day but counter is used to track the
# position across weeks
position = 0
counter = 0


def print_sequence():
    global position
    global counter
    log_entries = []

    for item in sequence:
        if item == "Top Of Hour Sequence":
            log_entries.append("Top Of Hour Sequence")
        if item == "5 Star":
            position += 1
            counter += 1
            if hot_songs:
                artist, title, category = hot_songs[counter % len(hot_songs)]
                log_entries.append(f"{position}: {format_entry(artist, title, category)}")
            else:
                log_entries.append(
                    f"{position}: ARTIST ✭✭✭✭✭ Song 1	Title ✭✭✭✭✭ Song 1	AudioFileName ✭✭✭✭✭ Song 1"
                )
        elif item == "ID - Short":
            log_entries.append("ID - Short")
        elif item == "1 Star":
            position += 1
            counter += 1
            if gold_songs:
                artist, title, category = gold_songs[counter % len(gold_songs)]
                log_entries.append(f"{position}: {format_entry(artist, title, category)}")
            else:
                log_entries.append(
                    f"{position}: ARTIST ✭ Song 1	Title ✭ Song 1	AudioFileName ✭ Song 1"
                )
        elif item == "ID - Position":
            log_entries.append("ID - Position")
        elif item == "3 Star":
            position += 1
            counter += 1
            if blist_songs:
                artist, title, category = blist_songs[counter % len(blist_songs)]
                log_entries.append(f"{position}: {format_entry(artist, title, category)}")
            else:
                log_entries.append(
                    f"{position}: ARTIST ✭✭✭ Song 1	Title ✭✭✭ Song 1	AudioFileName ✭✭✭ Song 1"
                )
        elif item == "Chruch & Roll Link":
            log_entries.append("Chruch & Roll Link")
        elif item == "2 Star":
            position += 1
            counter += 1
            if recurrent_songs:
                artist, title, category = recurrent_songs[counter % len(recurrent_songs)]
                log_entries.append(f"{position}: {format_entry(artist, title, category)}")
            else:
                log_entries.append(
                    f"{position}: ARTIST ✭✭ Song 1	Title ✭✭ Song 1	AudioFileName ✭✭ Song 1"
                )
        elif item == "Donut ID":
            log_entries.append("Donut ID")
        elif item == "Break":
            log_entries.append("Break")
        elif item == "Out Of Break Sequence":
            log_entries.append("Out Of Break Sequence")
        elif item == "4 Star":
            position += 1
            counter += 1
            if alist_songs:
                artist, title, category = alist_songs[counter % len(alist_songs)]
                log_entries.append(f"{position}: {format_entry(artist, title, category)}")
            else:
                log_entries.append(
                    f"{position}: ARTIST ✭✭✭✭ Song 1	Title ✭✭✭✭ Song 1	AudioFileName ✭✭✭✭ Song 1"
                )
        elif item == "ID - New Music Spotlight":
            log_entries.append("ID - New Music Spotlight")

    return log_entries


# Iterate over each day of the week and write the logs
days_of_week = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def write_daily_log(sequences):
    output = io.StringIO()
    writer = csv.writer(output)
    for sequence in sequences:
        for entry in sequence:
            writer.writerow([entry])
        separator = ["-" * 100]  # Separator after each sequence
        writer.writerow(separator)
    output.seek(0)  # Rewind to the beginning of the StringIO object
    return output


def generate_daily_logs():
    global position
    global counter
    zip_buffer = io.BytesIO()

    with ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for day in days_of_week:
            position = 0
            daily_sequence = [print_sequence() for _ in range(24)]
            csv_content = write_daily_log(daily_sequence)
            zip_file.writestr(f"{day}_log.csv", csv_content.getvalue())

    zip_buffer.seek(0)
    print("Generated daily logs")
    return zip_buffer
