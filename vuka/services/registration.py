from sqlalchemy.orm import Session

from vuka.models.registration import Registration
from vuka.schemas.registration import RegistrationCreate, RegistrationUpdate
from vuka.security.password import hash_password


def create_registration(
    db: Session,
    registration: RegistrationCreate
):
    existing_email = (
        db.query(Registration)
        .filter(Registration.email == registration.email)
        .first()
    )

    if existing_email:
        return None

    existing_username = (
        db.query(Registration)
        .filter(Registration.username == registration.username)
        .first()
    )

    if existing_username:
        return None

    registration_data = registration.model_dump()

    password = registration_data.pop("password")

    registration_data["pass_hash"] = hash_password(password)

    last_user = (
        db.query(Registration.user_id)
        .order_by(Registration.user_id.desc())
        .first()
    )

    registration_data["user_id"] = (
        (last_user[0] if last_user else 0) + 1
    )

    db_registration = Registration(**registration_data)

    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)

    return db_registration

def update_registration(
    db: Session,
    user_id: int,
    registration: RegistrationUpdate,
):
    user = (
        db.query(Registration)
        .filter(Registration.user_id == user_id)
        .first()
    )

    if not user:
        return None

    update_data = registration.model_dump(exclude_unset=True)
    allowed = {
        "first_name",
        "last_name",
        "username",
        "email",
        "preferred_language",
        "country",
        "is_active",
        "user_type",
    }
    update_data = {
        key: value
        for key, value in update_data.items()
        if key in allowed
    }

    if "email" in update_data:
        normalized_email = str(update_data["email"]).strip().lower()
        existing_email = (
            db.query(Registration)
            .filter(
                Registration.email == normalized_email,
                Registration.user_id != user_id,
            )
            .first()
        )
        if existing_email:
            raise ValueError("Email already registered")
        update_data["email"] = normalized_email

    if "username" in update_data:
        normalized_username = str(update_data["username"]).strip().lower()
        existing_username = (
            db.query(Registration)
            .filter(
                Registration.username == normalized_username,
                Registration.user_id != user_id,
            )
            .first()
        )
        if existing_username:
            raise ValueError("Username already registered")
        update_data["username"] = normalized_username

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user
