import unittest
import os
import shutil
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SubtitleDatabase

class TestSubtitleDatabase(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_subtitles.db'
        self.db = SubtitleDatabase(self.db_path)
        self.db.init_db()

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_and_search(self):
        self.db.add_subtitle('cam1', 100.0, 'hello world')
        self.db.add_subtitle('cam1', 105.0, 'testing subtitles')
        self.db.add_subtitle('cam2', 100.0, 'other camera')

        results = self.db.search('hello')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][3], 'hello world')

        results = self.db.search('testing')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][3], 'testing subtitles')

        results = self.db.search('camera')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][3], 'other camera')

    def test_search_by_camera(self):
        self.db.add_subtitle('cam1', 100.0, 'common text')
        self.db.add_subtitle('cam2', 100.0, 'common text')

        results = self.db.search('common', camera_id='cam1')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], 'cam1')

if __name__ == '__main__':
    unittest.main()
