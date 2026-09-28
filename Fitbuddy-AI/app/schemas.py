from typing import Literal

from pydantic import BaseModel, Field, field_validator


Goal = Literal[
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
    "endurance",
]


Intensity = Literal[
    "low",
    "medium",
    "high",
]


class UserInput(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=100,
    )

    username: str = Field(
        min_length=2,
        max_length=120,
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float = Field(
        gt=20,
        le=500,
    )

    goal: Goal

    intensity: Intensity


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=100,
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000,
    )

    @field_validator("feedback")
    @classmethod
    def clean_feedback(
        cls,
        value: str,
    ) -> str:

        return value.strip()