import os
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from vuka.models.registration import Registration
from vuka.security.audit import record_event
from vuka.security.password import hash_password, verify_password
from vuka.services.email import send_email


SUPPORT_EMAIL = os.getenv(
    "SUPPORT_EMAIL",
    "joselynedusabemungu@gmail.com",
)

def change_user_password(
    *,
    db: Session,
    user: Registration,
    current_password: str,
    new_password: str,
) -> None:
    if current_password == new_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different from your current password.",
        )

    if not verify_password(current_password, user.pass_hash):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect.",
        )

    user.pass_hash = hash_password(new_password)

    record_event(
        db,
        event_type="PASSWORD_CHANGED",
        action="change_password",
        user_id=user.user_id,
        success=True,
    )
    db.commit()


def create_support_request(
    *,
    user: Registration,
    category: str,
    message: str,
) -> dict:
    now = datetime.now(timezone.utc)
    ticket_id = int(now.strftime("%y%m%d%H%M%S%f")[:-3])
    subject = f"Vuka support request #{ticket_id} - {category}"
    body = (
        "A new support request was submitted from the Vuka mobile app.\n\n"
        f"Ticket ID: {ticket_id}\n"
        f"Category: {category}\n"
        f"User ID: {user.user_id}\n"
        f"Name: {user.first_name} {user.last_name}\n"
        f"Username: {user.username}\n"
        f"Email: {user.email}\n"
        f"Submitted at: {now.isoformat()}\n\n"
        "Message:\n"
        f"{message.strip()}\n"
    )

    try:
        send_email(SUPPORT_EMAIL, subject, body)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Support is temporarily unavailable. Please try again later.",
        ) from exc

    return {
        "ticket_id": ticket_id,
        "status": "open",
        "category": category,
        "message": message.strip(),
        "created_at": now.isoformat(),
    }
