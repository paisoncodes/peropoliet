from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from orders.models import Order

from lazerpay import Lazerpay



lazerpay = Lazerpay(LAZER_PUBLIC_KEY, LAZER_SECRET_KEY)

async def payment_tx():
   transaction_payload = {
      'reference': 'YOUR_REFERENCE', # Replace with a reference you generated
      'customer_name': 'Njoku Emmanuel',
      'customer_email': 'kalunjoku123@gmail.com',
      'coin': 'BUSD', # BUSD, DAI, USDC or USDT
      'currency': 'USD', # NGN, AED, GBP, EUR
      'amount': 100,
      'accept_partial_payment': True, # By default it's false
   }

   response = await lazerpay.payment.initialize_payment(transaction_payload)
   print(response)


