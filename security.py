from argon2 import PasswordHasher


class Passwd():
    def verify_password(self, password_try: str, db) -> bool:
        passwd_hasher = PasswordHasher(time_cost=8, memory_cost=102400, parallelism=4, hash_len=128, salt_len=128)
        hash = db.execute("SELECT Password_hash FROM Settings").fetchall()[0][0]
        try:
            passwd_hasher.verify(hash, password_try.encode('utf-8'))
            return True
        except:
            return False

    def set_new_password(self, password: str, db) -> bool:
        hash = PasswordHasher(time_cost=8, memory_cost=102400, parallelism=4, hash_len=128, salt_len=128).hash(password=password.encode("utf-8"))
        db.execute(f"UPDATE Settings SET Password_hash = '{hash}'")
        db.commit()