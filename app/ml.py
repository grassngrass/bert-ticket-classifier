from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)

from app import config

LABEL_MAP_FILE = "label_map.json"


class TicketDataset(Dataset):
    """Tokenizes ticket text lazily, one row at a time (memory-friendly at scale)."""

    def __init__(self, texts, labels, tokenizer, max_len: int):
        self.texts = list(texts)
        self.labels = list(labels)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int):
        enc = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }


def train_model() -> dict:
    """Fine-tune BERT on the configured CSV and save artifacts to MODEL_DIR.

    No train/test split — this is a demo with very few rows. Returns a summary dict.
    """
    csv_path = config.CSV_PATH
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"Training data not found at {csv_path}")

    df = pd.read_csv(csv_path)
    if not {"ticket_text", "department"}.issubset(df.columns):
        raise ValueError("CSV must contain 'ticket_text' and 'department' columns")
    df = df.dropna(subset=["ticket_text", "department"])

    # Stable, sorted label space derived from the data itself.
    departments = sorted(df["department"].unique().tolist())
    label2id = {dep: i for i, dep in enumerate(departments)}
    id2label = {i: dep for dep, i in label2id.items()}

    df["label_id"] = df["department"].map(label2id)

    tokenizer = AutoTokenizer.from_pretrained(config.BERT_MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        config.BERT_MODEL_NAME,
        num_labels=len(departments),
        id2label=id2label,
        label2id=label2id,
    )
    device = torch.device(config.DEVICE)
    model.to(device)

    dataset = TicketDataset(
        df["ticket_text"], df["label_id"], tokenizer, config.MAX_SEQ_LENGTH
    )
    loader = DataLoader(dataset, batch_size=config.BATCH_SIZE, shuffle=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.LEARNING_RATE)
    total_steps = len(loader) * config.NUM_EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=0, num_training_steps=max(total_steps, 1)
    )

    model.train()
    for _ in range(config.NUM_EPOCHS):
        for batch in loader:
            optimizer.zero_grad()
            outputs = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device),
                labels=batch["labels"].to(device),
            )
            outputs.loss.backward()
            optimizer.step()
            scheduler.step()

    # Persist model, tokenizer and the label map.
    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(config.MODEL_DIR)
    tokenizer.save_pretrained(config.MODEL_DIR)
    with open(config.MODEL_DIR / LABEL_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump({"id2label": id2label, "label2id": label2id}, f)

    return {
        "status": "trained",
        "departments": departments,
        "num_samples": len(df),
        "epochs": config.NUM_EPOCHS,
    }


class Classifier:
    """Holds the loaded model for inference. A single instance lives in app state."""

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.id2label: dict[int, str] = {}

    @property
    def is_ready(self) -> bool:
        return self.model is not None

    def load(self) -> bool:
        """Load a previously trained model from MODEL_DIR. Returns True on success."""
        label_file = config.MODEL_DIR / LABEL_MAP_FILE
        if not (config.MODEL_DIR.exists() and label_file.exists()):
            return False
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(config.MODEL_DIR)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                config.MODEL_DIR
            )
            self.model.to(torch.device(config.DEVICE))
            self.model.eval()
            with open(label_file, encoding="utf-8") as f:
                raw = json.load(f)
            self.id2label = {int(k): v for k, v in raw["id2label"].items()}
            return True
        except Exception:
            # Treat a corrupt/partial model dir as "not trained".
            self.model = None
            self.tokenizer = None
            return False

    def predict(self, text: str) -> tuple[str, float]:
        """Return (department, confidence_percent) for the given text."""
        if not self.is_ready:
            raise RuntimeError("Model is not loaded")
        enc = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=config.MAX_SEQ_LENGTH,
            return_tensors="pt",
        ).to(torch.device(config.DEVICE))

        with torch.no_grad():
            logits = self.model(**enc).logits
        probs = torch.softmax(logits, dim=-1).squeeze(0)
        idx = int(torch.argmax(probs).item())
        confidence = round(float(probs[idx].item()) * 100, 2)
        return self.id2label[idx], confidence


# Single shared instance, loaded at startup.
classifier = Classifier()
