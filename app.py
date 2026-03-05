from flask import Flask, request, jsonify, render_template_string
import subprocess
import os

app = Flask(__name__)

# Path to our freshly built Stockfish 18 binary
STOCKFISH_PATH = "./Stockfish/src/stockfish"

# Spawn the Stockfish 18 background process
engine = subprocess.Popen(
    STOCKFISH_PATH,
    universal_newlines=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

def send_command(command):
    engine.stdin.write(command + "\n")
    engine.stdin.flush()

# Initialize Stockfish at Maximum ELO
send_command("uci")
send_command("setoption name Skill Level value 20")
send_command("isready")

# --- HTML/JS FRONTEND ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Stockfish 18 - Sandbox God Mode</title>
    <!-- jQuery & Chessboard.js -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
    <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
    <style>
        body { font-family: sans-serif; margin: 20px; background-color: #1e1e1e; color: #fff; }
        .controls { margin-bottom: 20px; padding: 15px; background: #2d2d2d; border-radius: 8px; display: inline-block; }
        button, select { padding: 8px 12px; margin-right: 10px; font-size: 14px; cursor: pointer; }
        .warning { color: #ffb86c; font-size: 14px; margin-top: 10px; max-width: 600px; line-height: 1.5; }
    </style>
</head>
<body>
    <h2>Play against Stockfish 18 (Max ELO / God Mode)</h2>
    <div class="controls">
        <label><b>Stockfish is calculating for:</b></label>
        <select id="sf-color">
            <option value="b">Black</option>
            <option value="w">White</option>
        </select>
        <br><br>
        <button onclick="requestStockfishMove()" style="font-weight: bold; background: #4caf50; border: none; color: white;">Force Stockfish Move</button>
        <button onclick="board.start()">Reset Board</button>
        <button onclick="board.clear()">Clear Board</button>
        <button onclick="board.flip()">Flip Board</button>
        <div class="warning">
            <b>Sandbox Mode:</b> You can drag pieces freely! Place 5 extra queens, steal Stockfish's pieces by throwing them off the board, or move completely out of turn. Whenever you are ready for the AI to react to your chaos, click <b>"Force Stockfish Move"</b>.
        </div>
    </div>
    
    <!-- Spare pieces allows adding new pieces infinitely -->
    <div id="board" style="width: 600px"></div>

    <script>
        // Initialize customizable chess board
        var board = Chessboard('board', {
            draggable: true,
            dropOffBoard: 'trash',
            sparePieces: true,
            position: 'start',
            pieceTheme: 'https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/img/chesspieces/wikipedia/{piece}.png'
        });

        function requestStockfishMove() {
            var sfColor = document.getElementById('sf-color').value;
            // Get the current visual arrangement
            var partialFen = board.fen();
            
            // Construct a raw FEN so Stockfish accepts it regardless of sequence.
            // We force the active turn to be Stockfish's designated color.
            var fullFen = partialFen + " " + sfColor + " - - 0 1";

            fetch('/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fen: fullFen })
            })
            .then(res => res.json())
            .then(data => {
                if (!data.move || data.move === '(none)') {
                    alert("Stockfish refused to move! Ensure each side has exactly 1 King and no pawns are trapped on the 1st/8th ranks.");
                    return;
                }
                
                // Parse standard UCI move (e.g., e2e4 or e7e8q)
                let move = data.move;
                let from = move.substring(0, 2);
                let to = move.substring(2, 4);
                let promo = move.length > 4 ? move.substring(4, 5) : null;

                // Animate move visually
                board.move(from + '-' + to);

                // Handle visual pawn promotions logic
                if (promo) {
                    let pos = board.position();
                    pos[to] = (sfColor === 'w' ? 'w' : 'b') + promo.toUpperCase();
                    board.position(pos);
                }
            })
            .catch(err => console.error(err));
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    fen = data.get('fen')
    
    # Send the user's arbitrary board state to the engine
    send_command(f"position fen {fen}")
    # Search at depth 20 for absolute Max Elo simulation
    send_command("go depth 20")
    
    best_move = None
    while True:
        line = engine.stdout.readline().strip()
        if line.startswith("bestmove"):
            parts = line.split()
            if len(parts) >= 2:
                best_move = parts[1]
            break
            
    return jsonify({"move": best_move})

if __name__ == '__main__':
    # Hosted locally inside Codespace port environment
    app.run(host='0.0.0.0', port=5000)