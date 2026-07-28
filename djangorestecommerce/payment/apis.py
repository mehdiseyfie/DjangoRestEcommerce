from rest_framework.views import APIView 
from rest_framework.permissions import (
    IsAuthenticated, 
    AllowAny
)
from rest_framework_simplejwt.authentication import JWTAuthentication 
from drf_spectacular.utils import extend_schema 
from rest_framework import serializers 
from djangorestecommerce.payment.models import (
    Payment
)
from djangorestecommerce.users.selectors import (
    get_profile
)
from djangorestecommerce.orders.selectors import (
    get_order_by_slug
)
from rest_framework.response import Response 
from rest_framework import status
from djangorestecommerce.payment.services import (
    initiate_payment,
    verify_payment
) 



class OrderPaymentApiView(APIView): 
    permission_classes = [IsAuthenticated] 
    authentication_classes = [JWTAuthentication] 
    
    class OutputPaymentSerializer(serializers.ModelSerializer): 
        
            class Meta: 
                model = Payment 
                fields = "__all__"
    
    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "payment_url": {"type": "string"},
                    "authority": {"type": "string"},
                    "payment_id": {"type": "integer"}
                }
            }
        }) 
    
    def post(self, request, slug): 
        customer = get_profile(user=request.user) 
        
        try: 
            order = get_order_by_slug(customer=customer, slug=slug)
            
            if order.payment_status == "paid":
                return Response({"error": "this order already is paid."
                                 }, status=status.HTTP_400_BAD_REQUEST) 
            
            callback_url = request.build_absolute_uri(
                '/api/payment/callback/'
            )
            
            email = request.user.email if hasattr(request.user,"email") else None
            phone = str(request.user.phone) if hasattr(request.user.phone,"phone") else None 
            result = initiate_payment(
                order=order,
                callback_url=callback_url,
                email=email,
                mobile=phone
            ) 
            
            if result["success"]: 
                return Response({
                    "payment_url": result["payment_url"],
                    "authority": result["authority"], 
                    "payment_id": result["payment_id"], 
                }, 
                status=status.HTTP_200_OK
                )
            else: 
                return Response({"error": "Payment initiation failed"},
                                status=status.HTTP_400_BAD_REQUEST) 
        except Exception as ex:
            return Response({"error": str(ex)}, 
                            status=status.HTTP_400_BAD_REQUEST)
    
        
class OrderPaymentCallbackApiView(APIView):
    
    permission_classes = [AllowAny]
    
    
    @extend_schema(
        responses={
            200: {
                "type": "objects",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "order_slug": {"type": "str"},
                    "ref_id": {"type": "string"},
                    "payment_status": {"type": "string"}
                }
            }
        }
    ) 
    def get(self, request): 
        authority = request.GET.get("Authority")
        status_param = request.GET.get("Status") 
        
        if not authority: 
            return Response({"error": "Authority parameter is missing"},
                            status=status.HTTP_400_BAD_REQUEST) 
        
        try: 
            result = verify_payment(authority=authority,
                                    status=status_param) 
            
            if result['success']:
                return Response({
                    "success": True,
                    "message": result['message'],
                    "order_slug": result['order_slug'],
                    "ref_id": result.get('ref_id'),
                    "payment_status": result['payment_status']
                })
            else:
                return Response({
                    "success": False,
                    "message": result['message'],
                    "order_slug": result.get('order_slug'),
                    "payment_status": result['payment_status']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as ex:
            return Response(
                {"error": str(ex)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )