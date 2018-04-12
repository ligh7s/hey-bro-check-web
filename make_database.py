#!/usr/bin/env python3

import os
import sqlite3


def create_db():
    """Create the database."""
    query("""
        CREATE TABLE LogFiles (
            ID INTEGER PRIMARY KEY NOT NULL
        )
    """)
    print('Created DB at logs.db')


def query(string):
    """Send a query to the DB."""
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        'web_checker', 'logs.db')
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute(string)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_db()
