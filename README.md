# God Mode Chess v18 (Offline Standalone)

A fully portable, air-gapped chess application that runs as a single `.html` file.

## Features
- **Stockfish 18 Lite NNUE:** Embedded WASM engine (7.0MB) for high-performance analysis without a backend.
- **God Mode:** Bypasses standard chess rules. Drag and drop any piece anywhere. Trash pieces off-board. Switch sides (White/Black) at any time.
- **Standalone:** No external dependencies. jQuery, Chessboard.js, and Wikipedia pieces are all embedded as Base64.
- **Offline First:** Designed to be opened directly via the `file://` protocol. Uses a `Blob` Worker bridge to bypass browser security restrictions.

## Usage
Simply open `index.html` in any modern web browser (Chrome, Firefox, Edge). No server or installation required.
