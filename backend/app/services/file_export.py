import csv
import io
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.db.crud import get_user_search_history, get_user_image_history
from datetime import datetime

async def export_to_csv(db: Session, user_id: int, data_type: str = "all") -> str:
    """Export user data to CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)

    if data_type in ["all", "searches"]:
        # Export search history
        searches = get_user_search_history(db, user_id, limit=1000)

        if searches:
            writer.writerow(["Search History"])
            writer.writerow(["ID", "Query", "Results Count", "Created At"])

            for search in searches:
                results_count = len(search.results.get("results", []))
                writer.writerow([
                    search.id,
                    search.query,
                    results_count,
                    search.created_at.isoformat()
                ])
            writer.writerow([])  # Empty row separator

    if data_type in ["all", "images"]:
        # Export image history
        images = get_user_image_history(db, user_id, limit=1000)

        if images:
            writer.writerow(["Image Generation History"])
            writer.writerow(["ID", "Prompt", "Has Image", "Created At"])

            for image in images:
                has_image = bool(image.image_url or image.image_data)
                writer.writerow([
                    image.id,
                    image.prompt,
                    has_image,
                    image.created_at.isoformat()
                ])

    csv_content = output.getvalue()
    output.close()
    return csv_content

async def export_to_pdf(db: Session, user_id: int, data_type: str = "all") -> bytes:
    """Export user data to PDF format."""
    # For simplicity, we'll create a text-based PDF
    # In a real implementation, you'd use libraries like reportlab

    content = f"MindCanvas Data Export\nGenerated: {datetime.now().isoformat()}\n\n"

    if data_type in ["all", "searches"]:
        searches = get_user_search_history(db, user_id, limit=1000)
        content += "SEARCH HISTORY\n" + "=" * 50 + "\n\n"

        for search in searches:
            content += f"Query: {search.query}\n"
            content += f"Date: {search.created_at.isoformat()}\n"
            content += f"Results: {len(search.results.get('results', []))}\n"
            content += "-" * 30 + "\n\n"

    if data_type in ["all", "images"]:
        images = get_user_image_history(db, user_id, limit=1000)
        content += "IMAGE GENERATION HISTORY\n" + "=" * 50 + "\n\n"

        for image in images:
            content += f"Prompt: {image.prompt}\n"
            content += f"Date: {image.created_at.isoformat()}\n"
            content += f"Has Image: {bool(image.image_url or image.image_data)}\n"
            content += "-" * 30 + "\n\n"

    # Convert to bytes (mock PDF)
    return content.encode('utf-8')