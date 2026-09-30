
import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_db_connection():
    required_vars = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD"
    ]

    missing_vars = [
        var for var in required_vars
        if not os.getenv(var)
    ]

    if missing_vars:
        raise RuntimeError(
            f"Missing database environment variables: "
            f"{', '.join(missing_vars)}"
        )

    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    return connection
