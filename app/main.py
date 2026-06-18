from contextlib import asynccontextmanager

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import config, schemas
from app.database import get_db, init_db
from app.ml import classifier, train_model
from app.models import Ticket


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and load the model ONCE at startup (not per request).
    init_db()
    classifier.load()  # no-op if nothing has been trained yet
    yield


app = FastAPI(title="Warehouse Ticket Routing", version="1.0.0", lifespan=lifespan)


@app.get("/")
def root():
    return {
        "service": "Warehouse Ticket Routing",
        "model_loaded": classifier.is_ready,
        "endpoints": ["/train", "/predict", "/feedback", "/departments", "/tickets"],
    }


@app.post("/train", response_model=schemas.TrainResponse)
def train():
    """Train BERT on the CSV and hot-reload it into the running app."""
    try:
        result = train_model()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Reload so subsequent /predict calls use the freshly trained weights.
    if not classifier.load():
        raise HTTPException(
            status_code=500, detail="Training finished but model failed to reload"
        )
    return result


@app.post("/predict", response_model=schemas.PredictResponse)
def predict(req: schemas.PredictRequest, db: Session = Depends(get_db)):
    if not classifier.is_ready:
        raise HTTPException(
            status_code=409,
            detail="Model not trained yet. Call POST /train before predicting.",
        )

    department, confidence = classifier.predict(req.ticket_text)

    ticket = Ticket(
        ticket_text=req.ticket_text,
        predicted_department=department,
        confidence=confidence,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return schemas.PredictResponse(
        id=ticket.id,
        ticket_text=ticket.ticket_text,
        predicted_department=ticket.predicted_department,
        confidence=ticket.confidence,
    )


@app.post("/feedback", response_model=schemas.MessageResponse)
def feedback(req: schemas.FeedbackRequest, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, req.ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket {req.ticket_id} not found")

    ticket.correct_department = req.correct_department
    db.commit()
    return schemas.MessageResponse(
        message=f"Correction saved for ticket {req.ticket_id}: "
        f"{req.correct_department}"
    )


@app.get("/departments", response_model=list[str])
def departments():
    """Departments from the trained model if available, else from the CSV."""
    if classifier.is_ready and classifier.id2label:
        return sorted(classifier.id2label.values())
    try:
        df = pd.read_csv(config.CSV_PATH)
        return sorted(df["department"].dropna().unique().tolist())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No model trained and no CSV found")


@app.get("/tickets", response_model=list[schemas.TicketOut])
def tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).order_by(Ticket.id.desc()).all()
