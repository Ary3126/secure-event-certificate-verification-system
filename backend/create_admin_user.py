from __future__ import annotations

import secrets

from backend.app import create_app
from backend.models import Admin, db


def main() -> None:
    app = create_app("development")

    username = f"admin_{secrets.token_hex(3)}"
    password = f"SGP@{secrets.token_hex(4)}"
    email = f"{username}@charusat.edu.in"

    with app.app_context():
        while Admin.query.filter_by(username=username).first() is not None:
            username = f"admin_{secrets.token_hex(3)}"
            email = f"{username}@charusat.edu.in"

        admin = Admin(username=username, email=email)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

    # Print only credentials (one per line)
    print(username)
    print(password)


if __name__ == "__main__":
    main()

