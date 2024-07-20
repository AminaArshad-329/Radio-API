import csv
import json
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter


def build_documents(filename):
    documents = []
    # Load playlist.csv
    with open(filename, "r", newline="") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            else:
                document = Document(
                    page_content=json.dumps(
                        {
                            "Artist": row[0],
                            "Title": row[1],
                            "Rel. Date": row[2],
                            "GRC": row[3],
                            "Category": row[4],
                        }
                    ),
                    metadata={},
                )
                documents.append(document)
                line_count += 1
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    return docs


def build_playlist(db: FAISS, example_file, dest, playlist_len):
    query = []
    with open(example_file, "r", newline="") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            else:
                query.append(
                    json.dumps(
                        {
                            "Artist": row[0],
                            "Title": row[1],
                            "Rel. Date": row[2],
                            "GRC": row[3],
                        }
                    )
                )
                line_count += 1
    query = ",".join(item for item in query)
    docs = db.similarity_search(query=query, k=playlist_len)

    with open(dest, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Artist", "Title", "Rel. Date", "GRC", "Category"])
        for item in docs:
            item = json.loads(item.page_content)
            writer.writerow(
                [
                    item["Artist"],
                    item["Title"],
                    item["Rel. Date"],
                    item["GRC"],
                    item["Category"],
                ]
            )

    print(f"Exported playlist to {dest}.")
