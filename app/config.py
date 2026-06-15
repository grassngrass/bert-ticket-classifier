import os
from pathlib import Path

import torch

# Project root = parent of the `app` package directory.
BASE_DIR = Path(__file__).resolve().parent.parent

# Data source. Override with the TICKETS_CSV env var when swapping in a larger file.
CSV_PATH = Path(os.getenv("TICKETS_CSV", BASE_DIR / "tickets.csv"))

# Where the fine-tuned BERT model + tokenizer + label map are saved.
MODEL_DIR = Path(os.getenv("MODEL_DIR", BASE_DIR / "models"))

# SQLite database file.
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "tickets.db"))
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Base pretrained checkpoint.
BERT_MODEL_NAME = os.getenv("BERT_MODEL_NAME", "bert-base-uncased")

# Training hyperparameters. Defaults are tuned for the tiny demo set; for 100k rows
# fewer epochs and a larger batch size are appropriate (override via env).
NUM_EPOCHS = int(os.getenv("NUM_EPOCHS", "20"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "8"))
LEARNING_RATE = float(os.getenv("LEARNING_RATE", "3e-5"))
MAX_SEQ_LENGTH = int(os.getenv("MAX_SEQ_LENGTH", "64"))

# Device selection. Auto-detects a GPU when present (e.g. on a CUDA server) and
# falls back to CPU otherwise, so the same code runs unchanged on a laptop or a
# GPU box. Force a specific device with the DEVICE env var (e.g. "cpu" / "cuda").
DEVICE = os.getenv("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
