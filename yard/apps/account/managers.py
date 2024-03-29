from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models

from yard.utils.model import get_model_lazily


User = get_model_lazily('account.User')


class UserQuerySet(models.QuerySet):
    pass


class UserManager(BaseUserManager):
    def create_user(self, email, password, **fields):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email), **fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **fields):
        user = self.create_user(email, password=password, **fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=['is_staff', 'is_superuser'], using=self._db)
        return user


UserManager = UserManager.from_queryset(UserQuerySet)
