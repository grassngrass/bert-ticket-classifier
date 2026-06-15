from app.ml import classifier, train_model


def main() -> None:
    # Try to load a previously trained model from models/.
    if not classifier.load():
        print("No trained model found in models/.")
        answer = input("Train it now on tickets.csv? (y/n): ").strip().lower()
        if answer == "y":
            print("Training... (first run downloads BERT, ~a couple minutes)")
            train_model()
            classifier.load()
        else:
            print("Cannot predict without a trained model. Exiting.")
            return

    print("\nModel ready. Type a ticket description (or 'quit' to exit).\n")
    while True:
        text = input("Ticket > ").strip()
        if text.lower() in {"quit", "exit", "q"}:
            break
        if not text:
            continue
        department, confidence = classifier.predict(text)
        print(f"   -> {department}  ({confidence}%)\n")


if __name__ == "__main__":
    main()
