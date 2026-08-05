from django.db import transaction 
from djangorestecommerce.orders.models import (
    Order,
)
from djangorestecommerce.orders.services import (
    release_stock_for_order
)
from typing import (
    Optional, 
    Any 
)
import requests 
from django.conf import settings
from django.core.exceptions import ValidationError 
from djangorestecommerce.payment.models import Payment 
import json 
from djangorestecommerce.cart.models import (
    CartItem
) 
from django.core.cache import cache 
from decimal import Decimal 
from django.core.mail import send_mail 
from config.env import (
    env, 
    BASE_DIR
)
import os 
import logging 


env.read_env(os.path.join(BASE_DIR, ".env"))

logger = logging.getLogger(__name__) 


ZARINPAL_MERCHANT_ID = env("ZARINPAL_MERCHANT_ID")
ZARINPAL_REQUEST_URL = env("ZARINPAL_REQUEST_URL")
ZARINPAL_VERIFY_URL = env("ZARINPAL_VERIFY_URL")
ZARINPAL_STARTPAY_URL = env("ZARINPAL_STARTPAY_URL")






@transaction.atomic()
def initiate_payment(
    *,
    order: Order, 
    callback_url: str, 
    email: Optional[str], 
    mobile: Optional[str]
) -> dict[str, Any]:
    
    if order.payment_status == "paid": 
        raise ValidationError("this order was paid")
    
    try:
        total_amount = order.get_total_amount()
        amount_in_rials = int(total_amount * 10)
        
        payment_data = {
            "merchant_id": str(ZARINPAL_MERCHANT_ID),
            "amount": amount_in_rials, 
            "description": f"payment from {order.slug}", #type: ignore
            "callback_url": callback_url
        }
        
        if email:
            payment_data["email"] = email
        if mobile:
            payment_data["mobile"] = mobile 
            
        response = requests.post(url=str(ZARINPAL_REQUEST_URL),
                                 json=payment_data,
                                 timeout=10)
        
        if response.status_code != 200: 
             raise ValidationError("Payment service unavailable") 
        
        result = response.json() 
        
        if result.get("data",{}).get("code") == 100:
            authority = result["data"]["authority"] 
            
            payment = Payment.objects.create(
                order = order,
                payment_id = authority,
                authority = authority,
                amount = total_amount,
                gateway = "zarinpal",
                status = "pending",
            ) 
            
            return {
                "success": True,
                "payment_url": f"{ZARINPAL_STARTPAY_URL}{authority}",
                "authority": authority,
                "payment_id": payment.id #type: ignore
            } 
        else:
            error_message = result.get('errors', {})
            logger.error(f"Zarinpal payment request failed: {error_message}")
            raise ValidationError(f"Payment request failed: {error_message}")
            
    except requests.RequestException as e:
        logger.exception("Error connecting to Zarinpal")
        raise ValidationError(f"Payment service error: {str(e)}")
    
    except Exception as e:
        logger.exception("Error in payment initiation")
        raise ValidationError(f"Payment initiation failed: {str(e)}")


@transaction.atomic()
def verify_payment(
    authority: str, 
    status: str
) -> dict[str, Any]: 
    try:
        # Get payment record
        payment = Payment.objects.select_related('order').get(authority=authority)
        order = payment.order 
        
        
        if payment.status == 'completed':
            return {
                'success': True,
                'message': 'Payment already verified',
                'order_slug': order.slug,  # type: ignore
                'ref_id': payment.ref_id,
                'payment_status': 'completed'
            }
        
        if status != 'OK':
            # Payment was cancelled by user
            payment.status = 'failed'
            payment.gateway_response = json.dumps({'status': 'cancelled'})
            payment.save() 
            
            
            if order.payment_status != "paid": 
                release_stock_for_order(order=order)
                

            return {
                'success': False,
                'message': 'Payment was cancelled',
                'order_slug': order.slug, #type: ignore
                'payment_status': 'failed'
            }
        
        # Verify payment with Zarinpal
        total_amount = order.get_total_amount()
        amount_in_rials = int(total_amount * 10)
        
        verify_data = {
            'merchant_id': str(ZARINPAL_MERCHANT_ID),
            'amount': amount_in_rials,
            'authority': authority,
        }
        
        response = requests.post(
            str(ZARINPAL_VERIFY_URL),
            json=verify_data,
            timeout=10
        )
        
        if response.status_code != 200:
            payment.status = 'failed'
            payment.gateway_response = json.dumps({'error': 'Verification service unavailable'})
            payment.save()
            
            raise ValidationError("Payment verification service unavailable")
        
        result = response.json()
        
        # Check verification result
        if result.get('data', {}).get('code') in {100, 101}:
            # Payment successful
            payment.ref_id = result['data']['ref_id']
            payment.status = 'completed'
            payment.gateway_response = json.dumps(result)
            payment.save()
            
            # Update order status
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()
            
            # Clear cart items
            cart = order.cart
            CartItem.objects.filter(cart=cart).delete()
            cart.total_items = 0
            cart.total_price = Decimal('0.00')
            cart.save()
            
            # Clear cache
            cache.delete(f"cart_{cart.slug}")
            cache.delete(f"cart_totals_{cart.slug}")
            
            # Send email notification
            try:
                send_mail(
                    subject=f"Payment Successful for Order #{order.slug}", #type:ignore
                    message=f"Your payment for order {order.slug}was successful. Reference ID: {  
                        payment.ref_id}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.customer.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")
            
            return {
                'success': True,
                'message': 'Payment verified successfully',
                'order_slug': order.slug, #type: ignore
                'ref_id': payment.ref_id,
                'payment_status': 'completed'
            }
        else:
            # Verification failed
            payment.status = 'failed'
            payment.gateway_response = json.dumps(result)
            payment.save() 
            
            if order.payment != "paid": 
                release_stock_for_order(order=order) 
            
            error_message = result.get('errors', 'Verification failed')
            return {
                'success': False,
                'message': f"Payment verification failed: {error_message}",
                'order_slug': order.slug, #type: ignore
                'payment_status': 'failed'
            }
            
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for authority: {authority}")
        return {
            'success': False,
            'message': 'Payment not found',
            'payment_status': 'failed'
        }
    except requests.RequestException as e:
        logger.exception("Error connecting to Zarinpal for verification")
        return {
            'success': False,
            'message': f"Payment verification error: {str(e)}",
            'payment_status': 'failed'
        }
    except Exception as e:
        logger.exception("Error in payment verification")
        return {
            'success': False,
            'message': f"Verification failed: {str(e)}",
            'payment_status': 'failed'
        }