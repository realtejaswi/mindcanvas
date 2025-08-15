from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Any, Dict, Optional
from datetime import datetime


class ImageGenerationRequest(BaseModel):
    prompt: str
    width: Optional[int] = 512
    height: Optional[int] = 512
    steps: Optional[int] = 20


class ImageGenerationResponse(BaseModel):
    prompt: str
    image_url: Optional[str] = None
    image_data: Optional[str] = None  # Base64 encoded
    meta_data: Dict[str, Any]


class ImageHistoryResponse(BaseModel):
    # Enable reading from ORM attributes
    model_config = ConfigDict(from_attributes=True)

    id: int
    prompt: str
    image_url: Optional[str] = None
    image_data: Optional[str] = None
    # Read from ORM attribute "metadata", expose as "metadata" in JSON
    meta_data: Optional[Dict[str, Any]] = Field(default=None, alias="meta_data")
    created_at: datetime
