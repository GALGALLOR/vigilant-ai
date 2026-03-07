import sqlite3
import os
from cortex import CortexClient

DB_PATH = 'vigilant.db'
VECTORDB_HOST = "localhost:50051"
COLLECTION_NAME = "vigilant_events"

print("Clearing SQLite DB...")
if os.path.exists(DB_PATH):
    try:
        os.remove(DB_PATH)
        print(f"Deleted {DB_PATH}")
    except Exception as e:
        print(f"Failed to delete {DB_PATH}: {e}")
else:
    print(f"{DB_PATH} not found.")

print("\nClearing VectorAI Collection...")
try:
    with CortexClient(VECTORDB_HOST) as client:
        if client.has_collection(COLLECTION_NAME):
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted collection '{COLLECTION_NAME}'")
        else:
            print(f"Collection '{COLLECTION_NAME}' does not exist.")
except Exception as e:
    print(f"VectorAI error: {e}")

print("\nDone! Database is clean.")
