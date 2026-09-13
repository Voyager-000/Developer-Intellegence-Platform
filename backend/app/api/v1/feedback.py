from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import Feedback, generate_id
from backend.app.schemas.schemas import FeedbackCreate, ResponseEnvelope

router = APIRouter(prefix="/feedback", tags=["Developer Feedback"])

@router.post("", response_model=ResponseEnvelope[dict])
def submit_feedback(fb_in: FeedbackCreate, db: Session = Depends(get_db)):
    fb_obj = Feedback(
        id=generate_id("fb"),
        finding_id=fb_in.finding_id,
        fix_id=fb_in.fix_id,
        rating=fb_in.rating,
        was_accepted=fb_in.was_accepted,
        user_comment=fb_in.user_comment
    )
    db.add(fb_obj)
    db.commit()

    # Sync to Turso cloud
    try:
        from backend.app.core.turso import turso_client
        if turso_client.is_configured():
            turso_client.sync_feedback(
                fb_obj.id, fb_obj.finding_id, fb_obj.fix_id,
                fb_obj.rating, fb_obj.was_accepted, fb_obj.user_comment
            )
    except Exception:
        pass

    return ResponseEnvelope(
        data={"message": "Feedback submitted successfully. Thank you for helping train the intelligence model.", "id": fb_obj.id},
        request_id=generate_id("req")
    )
