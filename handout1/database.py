import sqlite3
from dataclasses import dataclass


@dataclass
class Note:
    id: int = None
    title: str = None
    content: str = ''
    favorite: bool = False


class Database:
    def __init__(self, nome_banco):
        self.conn = sqlite3.connect(nome_banco + '.db')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS note (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT NOT NULL
            );
        ''')

        columns = self.conn.execute(
            'PRAGMA table_info(note)'
        ).fetchall()

        column_names = [column[1] for column in columns]

        if 'favorite' not in column_names:
            self.conn.execute(
                'ALTER TABLE note ADD COLUMN favorite INTEGER NOT NULL DEFAULT 0'
            )
            self.conn.commit()

    def add(self, note):
        self.conn.execute(
            'INSERT INTO note (title, content) VALUES (?, ?)',
            (note.title, note.content)
        )
        self.conn.commit()

    def get_all(self):
        cursor = self.conn.execute(
            '''
            SELECT id, title, content, favorite
            FROM note
            ORDER BY favorite DESC
            '''
        )

        notes = []

        for row in cursor:
            note = Note(
                id=row[0],
                title=row[1],
                content=row[2],
                favorite=bool(row[3])
            )

            notes.append(note)

        return notes

    def update(self, entry):
        self.conn.execute(
            'UPDATE note SET title = ?, content = ? WHERE id = ?',
            (entry.title, entry.content, entry.id)
        )
        self.conn.commit()

    def delete(self, id):
        self.conn.execute("DELETE FROM note WHERE id = ?", (id,))
        self.conn.commit()

    def get(self, note_id):
        cursor = self.conn.execute(
            '''
            SELECT id, title, content, favorite
            FROM note
            WHERE id = ?
            ''',
            (note_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return Note(
            id=row[0],
            title=row[1],
            content=row[2],
            favorite=bool(row[3])
        )

    def toggle_favorite(self, note_id):
        self.conn.execute(
            '''
            UPDATE note
            SET favorite = CASE
                WHEN favorite = 0 THEN 1
                ELSE 0
            END
            WHERE id = ?
            ''',
            (note_id,)
        )

        self.conn.commit()