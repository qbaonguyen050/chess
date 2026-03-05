#!/bin/bash
set -e

# Repository root
ROOT_DIR=$(pwd)

# Clone Stockfish if it doesn't exist
if [ ! -d "Stockfish" ]; then
    echo "Cloning Stockfish..."
    git clone --depth 1 https://github.com/official-stockfish/Stockfish.git
fi

# Build Stockfish if binary doesn't exist
if [ ! -f "Stockfish/src/stockfish" ]; then
    echo "Building Stockfish..."
    cd Stockfish/src
    # Use ARCH=native for best performance/compatibility on the current host
    make -j$(nproc) build ARCH=native
    cd "$ROOT_DIR"
fi

if [ -f "Stockfish/src/stockfish" ]; then
    echo "Stockfish is ready at Stockfish/src/stockfish"
else
    echo "Failed to build Stockfish"
    exit 1
fi
