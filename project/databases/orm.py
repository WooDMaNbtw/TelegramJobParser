import json
import sqlite3 as sq
import datetime
import time


class ORM:

    links_attributes = {
        "Barona": 'https://barona.fi/tyopaikat/',
        "Eezy": 'https://tyopaikat.eezy.fi',
        "Oikotie": 'https://tyopaikat.oikotie.fi'
    }

    def __init__(self, path):
        self.conn = sq.connect(path)
        self.cursor = self.conn.cursor()

    async def show_data(self, table):
        self.cursor.execute(f'SELECT * FROM {table}')

    async def create_tables(self):
        tables_name = ('Barona', 'Eezy', 'Oikotie')
        fields = (
            '''
            id INTEGER PRIMARY KEY,
            posted_at DATE,
            slug TEXT,
            title TEXT NOT NULL,
            link TEXT,
            locations JSON,
            deadline DATE,
            description TEXT,
            employment_types JSON,
            language TEXT
            '''
        )

        for table in tables_name:
            self.cursor.execute(
                f'''CREATE TABLE IF NOT EXISTS {table} ({fields})'''
            )

        return 1

    async def save_vacancy(self, table: str,
                     title: str,
                     posted_at: datetime.date = None,
                     slug: str = None,
                     locations: dict = None,
                     deadline: datetime.date = None,
                     description: str = None,
                     employment_types: str = None,
                     language: str = 'fi') -> object:

        rows = self.cursor.execute(f'SELECT * FROM {table} WHERE slug=(?)', (slug, )).fetchall()

        if len(rows) != 0:
            #  return False if vacacancy already exists in database
            return False

        locations = json.dumps(locations)
        employment_types = json.dumps(employment_types)

        link = self.links_attributes.get(table, None) + slug
        self.cursor.execute(
            f'INSERT INTO \
            {table} '
            f'(posted_at, slug, title, link, locations, deadline, description, employment_types, language)'
            f' VALUES '
            f'(?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                posted_at, slug, title, link,
                locations, deadline, description,
                employment_types, language)
        )
        self.conn.commit()

        #  sending to the telegram new vacancy
        #  ...

        print(table + ": " + title + ' - ' + link)
        time.sleep(0.1)

    async def clear_old_records(self, table):
        self.cursor.execute(f'DELETE FROM {table} WHERE deadline < (?)', (datetime.date.today(), ))
        self.conn.commit()
