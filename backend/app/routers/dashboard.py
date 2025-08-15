from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.crud import (
    get_user_search_history, 
    get_user_image_history,
    delete_search_history,
    delete_image_history
)
from app.schemas.search import SearchHistoryResponse
from app.schemas.image import ImageHistoryResponse
from app.schemas.user import User
from app.services.file_export import export_to_csv, export_to_pdf

router = APIRouter()

@router.get("/search", response_model=List[SearchHistoryResponse])
async def get_dashboard_searches(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated search history for dashboard."""
    searches = get_user_search_history(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    # Filter by search term if provided
    if search:
        searches = [s for s in searches if search.lower() in s.query.lower()]

    return searches

@router.get("/images", response_model=List[ImageHistoryResponse])
async def get_dashboard_images(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated image history for dashboard."""
    images = get_user_image_history(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    # Filter by search term if provided
    if search:
        images = [i for i in images if search.lower() in i.prompt.lower()]

    return images

@router.delete("/search/{search_id}")
async def delete_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a search history entry."""
    success = delete_search_history(db=db, search_id=search_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Search not found")
    return {"message": "Search deleted successfully"}

@router.delete("/image/{image_id}")
async def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an image history entry."""
    success = delete_image_history(db=db, image_id=image_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}

@router.get("/export/csv")
async def export_data_csv(
    data_type: str = "all",  # "searches", "images", or "all"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export user data to CSV."""
    try:
        csv_content = await export_to_csv(
            db=db,
            user_id=current_user.id,
            data_type=data_type
        )

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=mindcanvas_data.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/export/pdf")
async def export_data_pdf(
    data_type: str = "all",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export user data to PDF."""
    try:
        pdf_content = await export_to_pdf(
            db=db,
            user_id=current_user.id,
            data_type=data_type
        )

        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=mindcanvas_data.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    
    