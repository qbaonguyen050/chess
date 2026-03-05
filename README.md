# Chess with Stockfish 18

A simple Flask application that allows playing against Stockfish 18 in a sandbox "God Mode".

## Prerequisites

- Python 3.12+
- Flask
- g++ (for building Stockfish)

## Setup

1.  **Build Stockfish**: Run the setup script to clone and build Stockfish.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
    This will create the Stockfish binary at `Stockfish/src/stockfish`.

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Start the Flask server:
```bash
python app.py
```
The application will be available at `http://localhost:5000`.

## Testing

Run the test suite:
```bash
python3 tests.py
```

## Features

- **Sandbox God Mode**: Drag pieces freely, add/remove pieces, and set custom positions.
- **Stockfish 18 Integration**: Get the best move for any position at depth 20.
- **Castling Rights**: Manually toggle castling rights for your custom setups.
