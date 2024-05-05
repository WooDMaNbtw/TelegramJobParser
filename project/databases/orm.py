import json
import sqlite3 as sq
import datetime

temp_vacancies = {}


class ORM:

    links_attributes = {
        "Barona": 'https://barona.fi/tyopaikat/',
        "Eezy": 'https://tyopaikat.eezy.fi',
        "Oikotie": 'https://tyopaikat.oikotie.fi'
    }

    def __init__(self, path):
        self.conn = sq.connect(path, check_same_thread=False, timeout=20)
        self.cursor = self.conn.cursor()

    def show_data(self, table):
        self.cursor.execute(f'SELECT * FROM {table}')

    def create_tables(self):
        tables_name = ('Barona', 'Eezy', 'Oikotie')
        fields = (
            '''
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            barona_id INTEGER DEFAULT 0,
            eezy_id INTEGER DEFAULT 0,
            oikotie_id INTEGER DEFAULT 0,
            language TEXT DEFAULT 'en'
            )'''
        )

        return 1

    def save_vacancy(self, table: str,
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
            #  return False if vacancy already exists in database
            return False

        if locations is not None:
            try:
                locations = ", ".join([location["city"] for location in locations])
            except TypeError:
                locations = ", ".join(location for key, location in locations.items() if location is not None)

        employment_types = json.dumps(employment_types)
        description = description.replace('\n', '')
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

        return None

    def save_user(self, user_id):
        rows = self.cursor.execute("SELECT * FROM users WHERE user_id = (?)", (user_id, )).fetchall()

        if len(rows) != 0:
            return

        self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id, ))
        self.conn.commit()

    def update_user(self, user_id, barona_id=None, eezy_id=None, oikotie_id=None):
        query = "UPDATE users SET "
        sets = []

        if barona_id is not None:
            sets.append(f"barona_id = {barona_id}")

        if eezy_id is not None:
            sets.append(f"eezy_id = {eezy_id}")

        if oikotie_id is not None:
            sets.append(f"oikotie_id = {oikotie_id}")

        if sets:
            query += ", ".join(sets) + f" WHERE user_id = {user_id}"
            self.cursor.execute(query)
            self.conn.commit()
            return True
        else:
            print("No fields to update provided.")
            return False

    def clear_old_records(self, table):
        self.cursor.execute(f'DELETE FROM {table} WHERE deadline < (?)', (datetime.date.today(), ))
        self.conn.commit()

    def set_user_language(self, user_id, language):
        self.cursor.execute('UPDATE users SET language = (?) WHERE user_id = (?)', (language, user_id))
        self.conn.commit()

    def get_user_language(self, user_id):
        option = self.cursor.execute('SELECT language FROM users WHERE user_id = (?)', (user_id, )).fetchone()
        return option[0]

    def get_relevant_records(self, user_id):

        query = "SELECT barona_id, eezy_id, oikotie_id FROM users WHERE user_id = (?)"
        last_viewed_records = self.cursor.execute(query, (user_id,)).fetchone()

        (barona_last_viewed_record,
         eezy_last_viewed_record,
         oikotie_last_viewed_record) = last_viewed_records

        barona_rows = self.cursor.execute(
            "SELECT * FROM barona WHERE id > (?)",
            (barona_last_viewed_record,)
        ).fetchall()
        eezy_rows = self.cursor.execute(
            "SELECT * FROM eezy WHERE id > (?)",
            (eezy_last_viewed_record,)
        ).fetchall()
        oikotie_rows = self.cursor.execute(
            "SELECT * FROM oikotie WHERE id > (?)",
            (oikotie_last_viewed_record,)
        ).fetchall()

        self.update_user(
            user_id=user_id,
            barona_id=barona_rows[-1][0] if barona_rows else barona_last_viewed_record,
            eezy_id=eezy_rows[-1][0] if eezy_rows else eezy_last_viewed_record,
            oikotie_id=oikotie_rows[-1][0] if oikotie_rows else oikotie_last_viewed_record
        )

        '''
        ---Returned structure---
        id
        posted
        slug
        title
        link
        locations
        deadline
        desc
        employment type
        lang
        '''

        return barona_rows + eezy_rows + oikotie_rows

