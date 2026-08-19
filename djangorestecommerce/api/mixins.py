from typing import Sequence, Type, TYPE_CHECKING

from importlib import import_module

from django.conf import settings

from django.contrib import auth

from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.authentication import BaseAuthentication

from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework.pagination import PageNumberPagination

def get_auth_header(headers):
    value = headers.get('Authorization')

    if not value:
        return None

    auth_type, auth_value = value.split()[:2]

    return auth_type, auth_value


if TYPE_CHECKING:
    # This is going to be resolved in the stub library
    # https://github.com/typeddjango/djangorestframework-stubs/
    from rest_framework.permissions import _PermissionClass

    PermissionClassesType = Sequence[_PermissionClass]
else:
    PermissionClassesType = Sequence[Type[BasePermission]]


class ApiAuthMixin:
    authentication_classes: Sequence[Type[BaseAuthentication]] = [
            JWTAuthentication,
    ]
    permission_classes: PermissionClassesType = (IsAuthenticated, )

class ApiPaginationMixin: 
    
    
    pagination_class = PageNumberPagination 
    
    @property
    def paginator(self): 
        if not hasattr(self, "_paginator"):
            self._paginator = self.pagination_class() if self.pagination_class else None 
        return self._paginator 
    
    def paginate_queryset(self, queryset): 
        if not self.paginator: 
            return None 
        return self.paginator.paginate_queryset(
            queryset,
            self.request,
            view=self
        ) 
    def get_paginated_response(self, data): 
        assert self.paginator is not None 
        return self.paginator.get_paginated_response(data)


























