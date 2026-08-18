from django.db import models
from djangorestecommerce.common.models import BaseModel
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager as BUM
from django.contrib.auth.models import PermissionsMixin 
from phonenumber_field.modelfields import PhoneNumberField 
from django.utils.translation import gettext_lazy as _



class BaseUserManager(BUM):
    def create_user(
                        self, first_name, last_name, phone,
                        email, is_active=True,is_admin=False,
                        password=None
                    ):
        if not email:
            raise ValueError("Users must have an email address") 

        if not phone: 
            raise ValueError("User must have a phone number.")

        user = self.model(
                            first_name=first_name,
                            last_name=last_name, phone=phone, 
                            email=self.normalize_email(email.lower()),
                            is_active=is_active, is_admin=is_admin
                        )

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(
                        self, email,
                        phone, password=None,
                        first_name=None, last_name=None
                        ):
        """if not phone:
            phone=input('please input phone number:')"""
            
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            is_active=True,
            is_admin=True,
            password=password,
        )

        user.is_superuser = True
        user.save(using=self._db)

        return user


class BaseUser(BaseModel, AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(
        verbose_name="first name", max_length=50, blank=True, null=True
    )
    last_name = models.CharField(
        verbose_name="last name", max_length=50, blank=True, null=True
    )
    phone = PhoneNumberField(verbose_name="phone number", unique=True)
    email = models.EmailField(verbose_name = "email address",
                              unique=True)
    

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False) 

   

    objects = BaseUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    def __str__(self):
        return self.email
    
    @property
    def is_staff(self):
        return self.is_admin



class Profile(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email}"


class ShippingAddress(BaseModel):
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="shipping_addresses", verbose_name=_("Customer"))
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    company = models.CharField(max_length=200, blank=True, verbose_name=_("Company"))
    address = models.CharField(max_length=200, verbose_name=_("Address"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    state = models.CharField(max_length=100, verbose_name=_("State"))
    postal_code = models.CharField(max_length=20, verbose_name=_("Postal Code"))
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone"))
    is_default = models.BooleanField(default=False, verbose_name=_("Default Address"))

    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")

    def save(self, *args, **kwargs):
        if self.is_default:
            ShippingAddress.objects.filter(customer=self.customer, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}, {self.country}"



