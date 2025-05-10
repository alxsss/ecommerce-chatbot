#!/bin/bash

MODEL_DIR="model"
MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
MODEL_FILE="mistral-7b-instruct-v0.1.Q4_K_M.gguf"

# Create model directory if not exists
mkdir -p "$MODEL_DIR"

# Download the model file if it doesn't already exist
if [ ! -f "$MODEL_DIR/$MODEL_FILE" ]; then
  echo "📦 Downloading Mistral model..."
  curl -L "$MODEL_URL" -o "$MODEL_DIR/$MODEL_FILE"
else
  echo "✅ Model already exists at $MODEL_DIR/$MODEL_FILE"
fi