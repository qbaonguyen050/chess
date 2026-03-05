from flask import Flask, request, jsonify, render_template
import subprocess
import os
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class StockfishEngine:
    def __init__(self, path="./Stockfish/src/stockfish"):
        self.path = path
        self.process = None
        self.lock = threading.Lock()
        self._start_process()

    def _start_process(self):
        if not os.path.exists(self.path):
            logger.warning(f"Stockfish not found at {self.path}. Attempting to use system 'stockfish'.")
            self.path = "stockfish"

        try:
            self.process = subprocess.Popen(
                self.path,
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1
            )
            self.send_command("uci")
            self._wait_for("uciok")
            self.send_command("setoption name Skill Level value 20")
            self.send_command("isready")
            self._wait_for("readyok")
            logger.info("Stockfish engine initialized.")
        except Exception as e:
            logger.error(f"Failed to start Stockfish: {e}")
            self.process = None

    def _wait_for(self, target, timeout=10):
        if not self.process:
            return
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            line = self.process.stdout.readline().strip()
            if target in line:
                return True
        logger.error(f"Timeout waiting for {target}")
        return False

    def send_command(self, command):
        if self.process and self.process.stdin:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

    def get_best_move(self, fen, depth=20, timeout=15):
        with self.lock:
            if not self.process or self.process.poll() is not None:
                self._start_process()
                if not self.process:
                    return None

            self.send_command(f"position fen {fen}")
            self.send_command(f"go depth {depth}")
            
            best_move = None
            import time
            start_time = time.time()
            while time.time() - start_time < timeout:
                line = self.process.stdout.readline().strip()
                if line.startswith("bestmove"):
                    parts = line.split()
                    if len(parts) >= 2:
                        best_move = parts[1]
                    break
            if best_move is None:
                logger.error(f"Failed to get best move within {timeout}s for FEN: {fen}")
            return best_move

# Initialize engine
engine = StockfishEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    fen = data.get('fen')
    if not fen:
        return jsonify({"error": "No FEN provided"}), 400
    
    logger.info(f"Requesting move for FEN: {fen}")
    best_move = engine.get_best_move(fen)
    
    if best_move is None:
        return jsonify({"error": "Engine failed to produce a move"}), 500

    return jsonify({"move": best_move})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
