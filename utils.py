
import psycopg2 as pg
import json
from dotenv import load_dotenv
import os

load_dotenv()

def connect_to_db() -> pg.extensions.connection:
    connection = pg.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

    return connection


def load_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)


def write_json(file_path: str, content: dict) -> None:
    with open(file_path, "w") as f:
            json.dump(content, f, indent=4)

