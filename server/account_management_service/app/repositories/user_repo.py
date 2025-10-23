from sqlmodel import Session, select
from models.user import User
from models.role import Role
from models.user_role import UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_email(self, email: str) -> User | None:
        return self.session.exec(select(User).where(User.email == email)).first()

    def create_user(self, username: str, email: str, plain_pw: str) -> User:
        hashed = pwd_context.hash(plain_pw)
        user = User(userName=username, email=email, password=hashed)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def assign_role(self, user: User, role_name: str):
        role = self.session.exec(select(Role).where(Role.name == role_name)).first()
        if not role:
            role = Role(name=role_name, description=f"Auto: {role_name}")
            self.session.add(role)
            self.session.commit()
            self.session.refresh(role)
        if not self.session.exec(select(UserRole).where(UserRole.userId == user.id, UserRole.roleId == role.id)).first():
            self.session.add(UserRole(userId=user.id, roleId=role.id))
            self.session.commit()

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)