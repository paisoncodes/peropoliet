from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from myshop.settings import lazerpay
from orders.models import Order

gateway = 'uwjdksidljjzld'

async def payment_process(request):
   order_id = request.session.get('order_id')
   order = get_object_or_404(Order, id=order_id)
   total_cost = order.get_total_cost()

   if request.method == 'POST':
      # create and submit transaction
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

      if result["is_success"]:
         # mark the order as paid
         order.paid = True
         # store the unique transaction id
         order.braintree_id = result.transaction.id
         order.save()
         return redirect('payment:done')
      else:
         return redirect('payment:canceled')
   else:
      # generate token
      client_token = gateway
      return render(request,
                     'payment/process.html',
                     {'order': order,
                     'client_token': client_token})

def payment_done(request):
   return render(request, 'payment/done.html')

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
               "message": e
            },
            status=status.HTTP_400_BAD_REQUEST
         )

async def test_create_link(data):
         transaction_payload = {
            'title': data["name"],
            'description': data["description"],
            'logo':
               'https://assets.audiomack.com/fireboydml/bbbd8710eff038d4f603cc39ec94a6a6c2c5b6f4100b28d62557d10d87246f27.jpeg?width=340&height=340&max=true',
            'currency': 'USD',
            'type': 'standard',
            'amount': 100, 
            'redirect_url': "https://keosariel.github.io"
         }

         response = await lazerpay.payment_links.create_payment_link(transaction_payload)
         return response