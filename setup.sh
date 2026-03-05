#!/bin/bash
set -e

# Clone Stockfish if it doesn't exist or is empty
if [ ! -d "Stockfish/src" ]; then
    echo "Cloning Stockfish..."
    git clone https://github.com/official-stockfish/Stockfish.git temp_stockfish
    mkdir -p Stockfish
    mv temp_stockfish/* Stockfish/
    rm -rf temp_stockfish
fi

# Build Stockfish
echo "Building Stockfish..."
cd Stockfish/src
make -j$(nproc) build ARCH=x86-64-sse41-popcnt

echo "Stockfish built successfully at Stockfish/src/stockfish"
