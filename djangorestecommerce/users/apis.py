from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from django.core.validators import MinLengthValidator
from rest_framework_simplejwt.authentication import JWTAuthentication
from .validators import number_validator, special_char_validator, letter_validator
from djangorestecommerce.users.models import BaseUser , Profile, ShippingAddress
from djangorestecommerce.api.mixins import ApiAuthMixin
from djangorestecommerce.users.selectors import (
    get_profile, 
    get_shipping_address_by_id, 
    get_shipping_addresses_by_profile
    
)
from djangorestecommerce.users.services import (
    register, 
    create_shipping_address
) 
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken 
from phonenumber_field.serializerfields import PhoneNumberField

from drf_spectacular.utils import extend_schema


class ProfileApi(ApiAuthMixin, APIView):

    class OutPutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Profile 
            fields = ("user",)

    @extend_schema(responses=OutPutSerializer)
    def get(self, request):
        query = get_profile(user=request.user)
        return Response(self.OutPutSerializer(query, context={"request":request}).data)


class RegisterApi(APIView):


    class InputRegisterSerializer(serializers.Serializer):
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        email = serializers.EmailField()
        phone = PhoneNumberField()
        password = serializers.CharField(
                validators=[
                        number_validator,
                        letter_validator,
                        special_char_validator,
                        MinLengthValidator(limit_value=10)
                    ]
                )
        confirm_password = serializers.CharField(max_length=255)
        
        def validate_email(self, email):
            if BaseUser.objects.filter(email=email).exists():
                raise serializers.ValidationError("email Already Taken")
            return email 
        def validate_phone(self, phone): 
            if BaseUser.objects.filter(phone=phone).exists():
                raise serializers.ValidationError("phone number already taken.")
            return phone 
        def validate(self, data):
            if not data.get("password") or not data.get("confirm_password"):
                raise serializers.ValidationError("Please fill password and confirm password")
            
            if data.get("password") != data.get("confirm_password"):
                raise serializers.ValidationError("confirm password is not equal to password")
            return data


    class OutPutRegisterSerializer(serializers.ModelSerializer):

        token = serializers.SerializerMethodField("get_token")

        class Meta:
            model = BaseUser 
            fields = (
                "email", 
                "phone",
                "first_name",
                "last_name",
                "token", 
                )

        def get_token(self, user):
            data = dict()
            token_class = RefreshToken

            refresh = token_class.for_user(user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return data


    @extend_schema(request=InputRegisterSerializer, responses=OutPutRegisterSerializer)
    def post(self, request):
        serializer = self.InputRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = register(
                    phone=serializer.validated_data["phone"],
                    email=serializer.validated_data["email"],
                    first_name=serializer.validated_data.get("first_name"),
                    last_name=serializer.validated_data.get("last_name"),
                    password=serializer.validated_data.get("password"),
                    )
        except Exception as ex:
            return Response(
                    f"Database Error {ex}",
                    status=status.HTTP_400_BAD_REQUEST
                    )
        return Response(self.OutPutRegisterSerializer(user, context={"request":request}).data)

class ShippingAddressApiView(APIView): 
    permission_classes = [IsAuthenticated] 
    authentication_classes = [JWTAuthentication] 
    
    class InputShippingAddressSerializer(serializers.Serializer): 
        
        first_name = serializers.CharField() 
        last_name = serializers.CharField() 
        company = serializers.CharField() 
        address = serializers.CharField() 
        city = serializers.CharField()
        state = serializers.CharField()
        postal_code = serializers.CharField() 
        country = serializers.CharField()
        phone = PhoneNumberField() 
        
        
    class OutputShippingAddressSerializer(serializers.ModelSerializer): 
        customer_email = serializers.EmailField(source="customer.user.email", read_only=True)
        
        class Meta: 
            model = ShippingAddress 
            fields = (
                "id", 
                "customer_email",
                "first_name", 
                "last_name", 
                "company", 
                "address", 
                "city", 
                "state", 
                "postal_code", 
                "country", 
                "phone", 
                "is_default",
            ) 
            
        def get_customer(self, obj: ShippingAddress): 
            return obj.customer
        
    
    @extend_schema(responses=OutputShippingAddressSerializer)
    def get(self, request, id=None): 
        profile = get_profile(user=request.user) 
        if not profile: 
            return Response(
                {
                    "error": "you don't have any profile."
                }, 
                status=status.HTTP_404_NOT_FOUND
            )
        if id: 
            try:
                shipping_address = get_shipping_address_by_id(
                    address_id=id,
                    customer=profile
                )
                serializer = self.OutputShippingAddressSerializer(
                    shipping_address, context={"request": request}
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as ex: 
                return Response(
                    {
                        "error": str(ex)
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            shipping_addresses = get_shipping_addresses_by_profile(customer=profile)
            serializer = self.OutputShippingAddressSerializer(
                shipping_addresses, many=True, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK) 
        
            
    @extend_schema(
        request=InputShippingAddressSerializer,
        responses=OutputShippingAddressSerializer
    )
    def post(self, request): 
        customer = get_profile(user=request.user) 
        serializer = self.InputShippingAddressSerializer(
            data=request.data
        ) 
        serializer.is_valid(raise_exception=True) 
        validated_data = serializer.validated_data 
        
        if not customer: 
            return Response(
                {
                    "error": "you don't have any profile."
                }, 
                status=status.HTTP_404_NOT_FOUND
            ) 
        try: 
            shipping_address = create_shipping_address(
                customer=customer,
                first_name=validated_data.get("first_name"), 
                last_name=validated_data.get("last_name"),
                company=validated_data.get("company"), 
                address=validated_data.get("address"), 
                city=validated_data.get("city"), 
                state=validated_data.get("state"), 
                postal_code=validated_data.get("postal_code"), 
                country=validated_data.get("country"), 
                phone=validated_data.get("phone")
            )
            serializer = self.OutputShippingAddressSerializer(
                shipping_address, context={"request": request}
            )
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
            )
        
        except Exception as ex: 
            return Response(
                {
                    "error": str(ex)
                },
                status=status.HTTP_400_BAD_REQUEST
            ) 
