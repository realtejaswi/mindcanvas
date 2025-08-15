from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.crud import create_search_history, get_user_search_history
from app.schemas.search import SearchRequest, SearchResponse, SearchHistoryResponse
from app.schemas.user import User
from app.services.mcp_client import search_web

router = APIRouter()

@router.post("/", response_model=SearchResponse)
async def perform_search(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform web search using Tavily MCP server."""
    try:
        # Perform search using MCP client
        search_results = await search_web(
            query=search_request.query,
            max_results=search_request.max_results
        )

        # Save to database
        create_search_history(
            db=db,
            user_id=current_user.id,
            query=search_request.query,
            results=search_results,
            meta_data={"max_results": search_request.max_results}
        )

        return search_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's search history."""
    search_history = get_user_search_history(
        db=db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit
    )
    return search_history

