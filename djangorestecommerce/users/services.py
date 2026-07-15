from django.db import transaction 
from .models import BaseUser, Profile


def create_profile(*, user:BaseUser) -> Profile:
    return Profile.objects.create(user=user)

def create_user(*,phone:str, email:str, first_name:str, last_name:str, password:str) -> BaseUser:
    return BaseUser.objects.create_user(phone=phone, email=email, first_name=first_name, last_name=last_name, password=password) #type: ignore


@transaction.atomic
def register(*, phone:str, email:str, first_name:str, last_name:str, password:str) -> BaseUser:

    user = create_user(phone=phone, email=email, first_name=first_name, last_name=last_name, password=password)
    create_profile(user=user)

    return user
