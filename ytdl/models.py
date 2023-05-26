from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from elasticsearch_dsl import Document, Text


class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('The Username field must be set.')

        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin


class UserDocument(Document):
    username = Text(required=True)
    password = Text(required=True)

    class Index:
        name = 'users'
