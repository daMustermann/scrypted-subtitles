import sqlite3
import time

class SubtitleDatabase:
    def __init__(self, path):
        self.path = path
        self.conn = None

    def init_db(self):
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subtitles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                text TEXT NOT NULL
            )
        ''')
        # Create FTS5 table for full-text search if supported, otherwise standard index
        try:
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS subtitles_fts USING fts5(text, content='subtitles', content_rowid='id')
            ''')
            # Triggers to keep FTS in sync
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS subtitles_ai AFTER INSERT ON subtitles BEGIN
                  INSERT INTO subtitles_fts(rowid, text) VALUES (new.id, new.text);
                END;
            ''')
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS subtitles_ad AFTER DELETE ON subtitles BEGIN
                  INSERT INTO subtitles_fts(subtitles_fts, rowid, text) VALUES('delete', old.id, old.text);
                END;
            ''')
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS subtitles_au AFTER UPDATE ON subtitles BEGIN
                  INSERT INTO subtitles_fts(subtitles_fts, rowid, text) VALUES('delete', old.id, old.text);
                  INSERT INTO subtitles_fts(rowid, text) VALUES (new.id, new.text);
                END;
            ''')
        except sqlite3.OperationalError:
            # FTS5 might not be enabled, fallback to simple LIKE search
            print("FTS5 not supported, falling back to standard search")
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_text ON subtitles(text)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_camera_timestamp ON subtitles(camera_id, timestamp)')
        self.conn.commit()

    def add_subtitle(self, camera_id, timestamp, text):
        if not self.conn:
            self.init_db()
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO subtitles (camera_id, timestamp, text) VALUES (?, ?, ?)', (camera_id, timestamp, text))
        self.conn.commit()

    def search(self, query, camera_id=None):
        if not self.conn:
            self.init_db()
        cursor = self.conn.cursor()
        
        # Check if FTS table exists
        fts_enabled = False
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subtitles_fts'")
            if cursor.fetchone():
                fts_enabled = True
        except:
            pass

        results = []
        if fts_enabled:
            sql = "SELECT id, camera_id, timestamp, text FROM subtitles WHERE id IN (SELECT rowid FROM subtitles_fts WHERE text MATCH ?)"
            params = [query]
            if camera_id:
                sql += " AND camera_id = ?"
                params.append(camera_id)
            sql += " ORDER BY timestamp DESC LIMIT 50"
            cursor.execute(sql, params)
        else:
            sql = "SELECT id, camera_id, timestamp, text FROM subtitles WHERE text LIKE ?"
            params = [f"%{query}%"]
            if camera_id:
                sql += " AND camera_id = ?"
                params.append(camera_id)
            sql += " ORDER BY timestamp DESC LIMIT 50"
            cursor.execute(sql, params)
            
        return cursor.fetchall()
    
    def close(self):
        if self.conn:
            self.conn.close()
