from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(
            email,
            password=password,
            **kwargs
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=154,
        unique=True,
        verbose_name='E-mail',
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name='First name'
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name='Last name'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Staff'
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name='Superuser'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
    ]

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email
