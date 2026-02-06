from datetime import datetime
from dataclasses import dataclass


@dataclass
class User:
    id: int | None
    username: str
    email: str | None
    password_hash: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
