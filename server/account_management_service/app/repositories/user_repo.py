from sqlmodel import Session, select
from models.user import User
from models.role import Role
from models.user_role import UserRole
from core.db import engine  # ← Use engine
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def create_user(self, username: str, email: str, plain_pw: str) -> User:
        hashed = pwd_context.hash(plain_pw)
        user = User(userName=username, email=email, password=hashed)

        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)

            # Assign role
            role = session.exec(select(Role).where(Role.name == "user")).first()
            if not role:
                role = Role(name="user", description="Default user")
                session.add(role)
                session.commit()
                session.refresh(role)
            session.add(UserRole(userId=user.id, roleId=role.id))
            session.commit()

        return user

    def find_by_email(self, email: str) -> User | None:
        with Session(engine) as session:
            return session.exec(select(User).where(User.email == email)).first()