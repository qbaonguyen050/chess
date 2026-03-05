import unittest
import os
from app import StockfishEngine, app

class TestStockfishApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure Stockfish is built or available
        cls.engine = StockfishEngine()
        cls.app = app.test_client()

    def test_engine_initialization(self):
        # This might be None if stockfish is not installed, which is expected in some environments
        # but the test should handle it gracefully or we should ensure it's there.
        # Given I built it, it should be there.
        self.assertIsNotNone(self.engine.process, msg=self.engine.init_error)

    def test_engine_move_generation(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        move, error = self.engine.get_best_move(fen, depth=10)
        self.assertIsNone(error)
        self.assertIsInstance(move, str)
        self.assertTrue(len(move) >= 4)

    def test_move_endpoint(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        response = self.app.post('/move', json={'fen': fen})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('move', data)
        self.assertIsInstance(data['move'], str)

    def test_invalid_fen(self):
        # Invalid FEN (no kings)
        fen = "8/8/8/8/8/8/8/8 w - - 0 1"
        response = self.app.post('/move', json={'fen': fen})
        # If Stockfish fails to move, it returns an error in our new API
        data = response.get_json()
        if response.status_code == 200:
            self.assertTrue(data['move'] is None or data['move'] == '(none)')
        else:
            self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
