from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("Enter a valid username")

        user = self.model(
            username=username,
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(
            username=username, password=password)
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)

        return user
