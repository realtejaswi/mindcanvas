from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.crud import create_image_history, get_user_image_history
from app.schemas.image import ImageGenerationRequest, ImageGenerationResponse, ImageHistoryResponse
from app.schemas.user import User
from app.services.mcp_client import generate_image

router = APIRouter()

@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image_endpoint(
    image_request: ImageGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate image using Flux ImageGen MCP server."""
    try:
        # Generate image using MCP client
        image_result = await generate_image(
            prompt=image_request.prompt,
            width=image_request.width,
            height=image_request.height,
            steps=image_request.steps
        )

        # Save to database
        create_image_history(
            db=db,
            user_id=current_user.id,
            prompt=image_request.prompt,
            image_url=image_result.get("image_url"),
            image_data=image_result.get("image_data"),
            meta_data={
                "width": image_request.width,
                "height": image_request.height,
                "steps": image_request.steps
            }
        )

        return image_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.get("/history", response_model=List[ImageHistoryResponse])
async def get_image_history(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's image generation history."""
    image_history = get_user_image_history(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return image_history