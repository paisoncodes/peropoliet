from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from myshop.settings import lazerpay
from orders.models import Order


gateway = 'uwjdksidljjzld'

async def payment_process(request):
   order_id = request.session.get('order_id')
   order = get_object_or_404(Order, id=order_id)
   total_cost = order.get_total_cost()

   if request.method == 'POST':
      transaction_payload = {
         'reference': 'YOUR_REFERENCE', # Replace with a reference you generated
         'customer_name': 'Njoku Emmanuel',
         'customer_email': 'kalunjoku123@gmail.com',
         'coin': 'BUSD', # BUSD, DAI, USDC or USDT
         'currency': 'USD', # NGN, AED, GBP, EUR
         'amount': total_cost,
         'accept_partial_payment': True, # By default it's false
      }

      result = await lazerpay.payment.initialize_payment(transaction_payload)
      result = result.json()

      if result['is_success']:
         #mark the order as paid
         order.paid = True

   return render (request, 'payment/done.html')

def payment_canceled(request):
   return render(request, 'payment/canceled.html')

class PaymentLink(APIView):
   def post(self, request):
      try:
         response = test_create_link(request.data)
         return Response(response, status=status.HTTP_200_OK)
      except Exception as e:
         return Response(
            {
               'message':e
            },
            status=status.HTTP_400_BAD_REQUEST
         )