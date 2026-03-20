#!/bin/bash
set -e

echo "Setting up Ollama for JobExtractor AI Assistant..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  echo "Installing Ollama on Linux..."
  curl -fsSL https://ollama.com/install.sh | sh
elif [[ "$OSTYPE" == "darwin"* ]]; then
  echo "Installing Ollama on macOS..."
  if command -v brew &>/dev/null; then
    brew install ollama
  else
    echo "Please install Homebrew first: https://brew.sh"
    exit 1
  fi
else
  echo "Windows detected. Please download Ollama from:"
  echo "https://ollama.com/download/windows"
  echo "Then run: ollama pull llama3.1:8b"
  exit 0
fi

echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!
sleep 3

echo "Pulling llama3.1:8b model (~4.7GB, this may take a while)..."
ollama pull llama3.1:8b

echo "Verifying model..."
ollama run llama3.1:8b "Say 'JobExtractor AI ready' and nothing else."

echo ""
echo "Ollama setup complete!"
echo "Model: llama3.1:8b"
echo "Endpoint: http://localhost:11434"
echo ""
echo "To start Ollama manually: ollama serve"
echo "To test: ollama run llama3.1:8b"
