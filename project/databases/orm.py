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
        self.conn = sq.connect(path, check_same_thread=False)
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
            #  return False if vacacancy already exists in database
            return False
        print(locations)
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

        #  sending to the telegram new vacancy
        #  ...
        displayed_data = {
            'service': table,
            'title': title,
            'link': link,
            'locations': locations,
            'description': description,
            'language': language
        }

        temp_vacancies.update({slug: displayed_data})
        return None

    def save_user(self, user_id):
        rows = self.cursor.execute("SELECT * FROM users WHERE user_id = (?)", (user_id, )).fetchall()

        if len(rows) != 0:
            return

        self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id, ))

    def update_user(self, user_id, barona_id=None, eezy_id=None, oikoie_id=None):
        query = "UPDATE users SET "
        sets = []

        if barona_id is not None:
            sets.append(f"barona_id = {barona_id}")

        if eezy_id is not None:
            sets.append(f"eezy_id = {eezy_id}")

        if oikoie_id is not None:
            sets.append(f"oikoie_id = {oikoie_id}")

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

    @staticmethod
    def save_temp_vacancies():
        with open('new_temp_vacancies.json', 'w') as file:
            json.dump(temp_vacancies, fp=file, indent=4, ensure_ascii=False)

    def get_relevant_records(self, user_id):
        barona_last_viewed_record = self.cursor.execute("SELECT barona_id FROM users WHERE user_id = (?)", (user_id, )).fetchone()
        eezy_last_viewed_record = self.cursor.execute("SELECT eezy_id FROM users WHERE user_id = (?)", (user_id, )).fetchone()
        oikotie_last_viewed_record = self.cursor.execute("SELECT oikotie FROM users WHERE user_id = (?)", (user_id, )).fetchone()

        barona_rows = self.cursor.execute("SELECT * FROM barona WHERE id >= (?)", (barona_last_viewed_record, )).fetchall()
        eezy_rows = self.cursor.execute("SELECT * FROM eezy WHERE id >= (?)", (eezy_last_viewed_record, )).fetchall()
        oikotie_rows = self.cursor.execute("SELECT * FROM oikotie WHERE id >= (?)", (oikotie_last_viewed_record, )).fetchall()

        self.update_user(
            user_id=user_id,
            barona_id=barona_rows[-1][-1],
            eezy_id=eezy_rows[-1][-1],
            oikoie_id=oikotie_rows[-1][-1]
        )

        return barona_rows + eezy_rows + oikotie_rows
