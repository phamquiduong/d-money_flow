import bcrypt


class PasswordService:
    @staticmethod
    def hash_password(plain_password: str) -> str:
        password_bytes = plain_password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        password_bytes = plain_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
