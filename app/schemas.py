from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field
from celery import states


class UserInputRequest(BaseModel):
    age: float = Field(..., ge=0, le=200, description="Insert your age.")
    workclass: Literal["Private", "Local-gov"] = Field(
        ..., description="Select your workclass."
    )
    fnlwgt: float = Field(..., ge=1, le=10_000_000, description="Insert your fnlwgt.")
    education: Literal["HS-grad", "Some-college"] = Field(
        ..., description="Select your education."
    )
    educational_num: float = Field(
        ..., ge=1, le=16, description="Insert your educational-num."
    )
    marital_status: Literal["Married-civ-spouse", "Divorced"] = Field(
        ..., description="Select your marital status."
    )
    occupation: Literal["Exec-managerial", "Craft-repair"] = Field(
        ..., description="Select your occupation."
    )
    relationship: Literal["Husband", "Wife"] = Field(
        ..., description="Select your relationship."
    )
    race: Literal["Black", "White"] = Field(..., description="Select your race.")
    gender: Literal["Male", "Female"] = Field(..., description="Select your gender.")


class FileMetadataResponse(BaseModel):
    columns: List[str]


class AsyncTaskResponse(BaseModel):
    id: str
    status: states
    result: Optional[Any] = None
