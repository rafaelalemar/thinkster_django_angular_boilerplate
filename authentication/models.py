from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class AccountManager(BaseUserManager):
    '''
    When substituting a customer user model, it is required that you also define a related 'Manager' class
    that overrides the create_user() and create_superuser() methods.
    '''
    def create_user(self, email, password=None, **kwargs):

        # Because users are required to have both an email and a username, we should raise an error if either of these
        # attributes are missing.
        if not email:
            raise ValueError('Users must have a valid email address.')

        if not kwargs.get('username'):
            raise ValueError('Users must have a valid username.')

        # Since we haven't defined a model attribute on the AccountManager class, self.model refers to the model
        # attribute of BaseUserManager. This defaults to settings.AUTH_USER_MODEL, which we will change in just a
        # moment to point to the Account class.
        account = self.model(
            email = self.normalize_email(email), username = kwargs.get('username')
        )

        account.set_password(password)
        account.save()

        return account


    def create_superuser(self, email, password, **kwargs):

        # Writing the same thing more than once sucks. Instead of copying all of the code from create_account and
        # pasting it in create_superuser, we simply let create_user handle the actual creation. This frees up create_
        # superuser to only worry about turning an Account into a superuser.
        account = self.create_user(email, password, **kwargs)

        account.is_admin = True
        account.save()

        return account



class Account(AbstractBaseUser):
    '''
    Extending Django's built-in User model

    Django has a built-in User model that offers a lot of functionality. The problem with User is that the model
    cannot be extended to include more information. For example, we will be giving our users a tagline to display
    on their profile. User does not have a tagline attribute and we cannot add one ourselves.

    User inherits from AbstractBaseUser. That is where User gets most of it's functionality. By creating a new
    model called Account and inheriting from AbstractBaseUser, we will get the necessary functionality of User
    (password hashing, session management, etc) and be able to extend Account to include extra information, such
    as a tagline.
    '''
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, unique=True)

    fist_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)
    tagline = models.CharField(max_length=140, blank=True)

    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __unicode__(self):
        return self.email

    def get_full_name(self):
        return ' '.join([self.fist_name], self.last_name)

    def get_short_name(self):
        return self.fist_name