from flask import Flask, request, jsonify, render_template
import subprocess
import os
import threading
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class StockfishEngine:
    def __init__(self, path="./Stockfish/src/stockfish"):
        self.default_path = os.path.abspath(path)
        self.path = self.default_path
        self.process = None
        self.lock = threading.Lock()
        self.init_error = None
        self._start_process()

    def _start_process(self):
        self.init_error = None

        # Try local path first
        if not os.path.exists(self.path):
            logger.warning(f"Stockfish not found at {self.path}. Searching in system PATH.")
            system_path = shutil.which("stockfish")
            if system_path:
                self.path = system_path
                logger.info(f"Using system stockfish at {self.path}")
            else:
                self.init_error = f"Stockfish binary not found. Please run ./setup.sh to build it, or install stockfish on your system."
                logger.error(self.init_error)
                self.process = None
                return

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
            if not self._wait_for("uciok"):
                raise Exception("Engine did not respond to 'uci' command.")

            self.send_command("setoption name Skill Level value 20")
            self.send_command("isready")
            if not self._wait_for("readyok"):
                raise Exception("Engine did not respond to 'isready' command.")

            logger.info(f"Stockfish engine initialized from {self.path}")
        except Exception as e:
            self.init_error = f"Failed to start Stockfish at {self.path}: {e}"
            logger.error(self.init_error)
            self.process = None

    def _wait_for(self, target, timeout=10):
        if not self.process:
            return False
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            line = self.process.stdout.readline().strip()
            if target in line:
                return True
        return False

    def send_command(self, command):
        if command and self.process and self.process.stdin:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

    def get_best_move(self, fen, depth=20, timeout=15):
        with self.lock:
            if not self.process or self.process.poll() is not None:
                self._start_process()
                if not self.process:
                    return None, self.init_error

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
                error_msg = f"Failed to get best move within {timeout}s for FEN: {fen}"
                logger.error(error_msg)
                return None, error_msg

            return best_move, None

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
    best_move, error = engine.get_best_move(fen)
    
    if error:
        return jsonify({"error": error, "move": None}), 500

    return jsonify({"move": best_move})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
