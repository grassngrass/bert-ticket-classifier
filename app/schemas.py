from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PredictRequest(BaseModel):
    ticket_text: str = Field(..., min_length=1, description="Raw ticket text to classify")


class PredictResponse(BaseModel):
    id: int
    ticket_text: str
    predicted_department: str
    confidence: float = Field(..., description="Confidence as a percentage (0-100)")


class FeedbackRequest(BaseModel):
    ticket_id: int = Field(..., description="ID of the ticket prediction to correct")
    correct_department: str = Field(..., min_length=1)


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_text: str
    predicted_department: str
    correct_department: Optional[str] = None
    confidence: float
    created_at: datetime


class TrainResponse(BaseModel):
    status: str
    departments: list[str]
    num_samples: int
    epochs: int


class MessageResponse(BaseModel):
    message: str
