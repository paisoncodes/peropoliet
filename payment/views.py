import json
import io
import secrets
from django.shortcuts import render
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect, get_object_or_404
from myshop.settings import lazerpay
from orders.models import Order
from .models import PayWithCrypto


# gateway = 'uwjdksidljjzld'

async def payment_process(request):
   order_id = request.session.get('order_id')
   order = get_object_or_404(Order, id=order_id)
   total_cost = order.get_total_cost()

   if request.method == 'POST':
      try:
         payment_info = PayWithCrypto.objects.create(
            name=request.data['name'],
            email=request.data['email'],
            currency=request.data['currency'],
            coin=request.data['coin']
         )
         response = lazerpay.initTransaction( 
            reference=payment_info['reference'], # Replace with a reference you generated
            amount=payment_info["amount"], 
            customer_name=payment_info['name'], 
            customer_email=payment_info['email'], 
            coin=payment_info['coin'], 
            currency=payment_info['currency'], 
            accept_partial_payment=False # By default, it's false
         )
         return Response(response, status=status.HTTP_200_OK)
      except Exception as e:
         return Response(e, status=status.HTTP_400_BAD_REQUEST)

      if response['is_success']:
         #mark the order as paid
         order.paid = True

   return render (request, 'payment/done.html')

def payment_canceled(request):
   return render(request, 'payment/canceled.html')

class PaymentLink(APIView):
   def post(self, request):
      # order_id = request.session.get('order_id')
      # order = get_object_or_404(Order, id=order_id)
      # amount = order.get_total_cost()
      # payment_info = request.data

      try:
         serializer = CreatePaymentSerializer(data=request.data)
         if serializer.is_valid():
            serializer.save()
            payment = serializer.data
            response = lazerpay.initTransaction( 
               reference=payment['reference'], # Replace with a reference you generated
               amount=payment['amount'], 
               customer_name=payment['name'], 
               customer_email=payment['email'], 
               coin=payment['coin'], 
               currency=payment['currency'], 
               accept_partial_payment=False # By default, it's false
            )
            fix_bytes_value = response.replace(b"'", b'"')
            response = json.load(io.BytesIO(fix_bytes_value))
            return Response(response, status=status.HTTP_200_OK)
         else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ConfirmPayment(APIView):
   def post(self, request):
      try:
         response_1 = lazerpay.confirmPayment(
            identifier = request.data['reference']|request.data['address']
         )
         if response_1:
            PayWithCrypto.objects.filter(reference=request.data['reference']).update(successful=True)
            return Response(
               {
                  'message':'Payment Successful'
               },
               status=status.HTTP_200_OK
            )
         else:
            return Response(
               {
                  "message":"Payment Failed"
               },
               status=status.HTTP_200_OK
            )
      except Exception as e:
         return Response(e, status=status.HTTP_400_BAD_REQUEST)

class GetCoins(APIView):
   def post(self, request):
      try:
         response = lazerpay.getAcceptedCoins()
         fix_bytes_value = response.replace(b"'", b'"')
         response = json.load(io.BytesIO(fix_bytes_value))
         return Response(response["data"], status=status.HTTP_200_OK)
      except Exception as e: 
         return Response(
            {
               "error": str(e)
            },
            status=status.HTTP_401_UNAUTHORIZED
         )

class GetPaymentInfo(APIView):
   
   def get(self, request):
      infos = PayWithCrypto.objects.all()
      serializer = PaymentSerializer(infos, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)

class PaymentSerializer(serializers.ModelSerializer):
   class Meta:
      model = PayWithCrypto
      fields = "__all__"

class CreatePaymentSerializer(serializers.ModelSerializer):
   class Meta:
      model = PayWithCrypto
      fields = ("id", "name", "email", "currency", "amount", "coin", "reference")

      read_only_fields = ["id", "reference"]
   
   def create(self, validated_data):
      payment = PayWithCrypto.objects.create(
         name=validated_data["name"],
         email=validated_data['email'],
         currency=validated_data['currency'],
         amount=validated_data['amount'],
         coin=validated_data['coin']
      )
      payment.save()

      return payment

