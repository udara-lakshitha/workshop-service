import datetime as dt
from sqlalchemy import select
from app.auth import get_password_hash
from app.database import SessionLocal
from app.models import Role, User, Workshop


def seed() -> None:
    with SessionLocal() as db:
        if db.scalar(select(User.id).limit(1)) is not None:
            return

        db.add_all([
            User(username="admin", password=get_password_hash("admin123"), role=Role.ADMIN),
            User(username="manager", password=get_password_hash("manager123"), role=Role.MANAGER),
            User(username="staff", password=get_password_hash("staff123"), role=Role.STAFF),
        ])

        def at(days: int, hour: int) -> dt.datetime:
            base = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=days)
            return base.replace(hour=hour, minute=0, second=0, microsecond=0)

        samples = [
            ("POT-101", "Pottery for Beginners", "Nadeesha Perera", at(2, 9), 12),
            ("COD-201", "Intro to Python", "Kasun Fernando", at(3, 14), 20),
            ("FIT-110", "Morning Yoga", "Ishara Silva", at(4, 7), 3),
            ("ART-150", "Watercolour Basics", "Dilani Jayasuriya", at(8, 10), 10),
        ]
        for code, title, instructor, when, capacity in samples:
            db.add(Workshop(code=code, title=title, instructor=instructor, date_time=when, capacity=capacity))
        db.commit()

if __name__ == "__main__":
    seed()
    print("Database seeded successfully!")
        