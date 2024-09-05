from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Transaction, User
from .serializers import TransactionSerializer, UserSerializer
from io import BytesIO
from django.http import HttpResponse
from .permissions import IsManager, IsStaff
import random
from django.template.loader import render_to_string
from django.template import Context
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from .models import Transaction

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class TransactionListCreate(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsStaff()]
        return [IsAuthenticated()]

    def generate_transaction_id(self):
        # Generate a random 4-digit number
        random_number = random.randint(1000, 9999)
        # Create the transaction ID with the 'TXNID' prefix
        txn_id = f'TXNID{random_number}'
        return txn_id

    def perform_create(self, serializer):
        if self.request.user.is_authenticated and self.request.user.user_type == 'staff':
            # Generate a unique transaction ID
            txn_id = self.generate_transaction_id()
            # Save the transaction with the generated ID
            serializer.save(transaction_id=txn_id)
        else:
            self.permission_denied(self.request)

    def post(self, request, *args, **kwargs):
        # Call the superclass's post method to handle creation
        response = super().post(request, *args, **kwargs)
        # Extract the transaction ID from the response data
        transaction_id = response.data.get('transaction_id')
        # Return the transaction ID in the response
        return Response({'transaction_id': transaction_id}, status=status.HTTP_201_CREATED)
    

class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    lookup_field = 'transaction_id'
    
    def get_permissions(self):
        if self.request.method in ['DELETE', 'PUT', 'PATCH']:
            return [IsManager()]
        return [IsAuthenticated()]
    

    def update(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and self.request.user.user_type in ['staff', 'manager']:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Check if the status is set to 'approved'
            if serializer.validated_data.get('status') == 'approved':
                # Generate PDF after approval
                pdf_response = self.generate_pdf_for_transaction(instance)
                return pdf_response

            return Response(serializer.data)
        return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
    
    def generate_pdf_for_transaction(self, transaction):
        # Render the HTML for the PDF
        html = render_to_string('transaction_detail_template.html', {'txn': transaction})
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="transaction_{transaction.transaction_id}.pdf"'
            return response
        else:
            return HttpResponse(f'We had some errors <pre>{html}</pre>', content_type='text/html')    

    def destroy(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and self.request.user.user_type == 'manager':
            return super().destroy(request, *args, **kwargs)
        return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)




class PDFTransactionListView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

# if user approved, then only the pdf will be available.
    def get(self, request, *args, **kwargs):
        if not request.user.user_type == 'manager':
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
    
        transactions = Transaction.objects.filter(status='approved')
        html = render_to_string('transaction_list_template.html', {'transactions': transactions})
        response = self.render_to_pdf(html, "transactions_list.pdf")
        return response

    def render_to_pdf(self, html_string, filename):
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        return HttpResponse(f'We had some errors <pre>{html_string}</pre>', content_type='text/html')


class PDFTransactionDetailView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, txnid, *args, **kwargs):
        try:
            txn = Transaction.objects.get(transaction_id=txnid)
            if txn.status != 'approved':  
                return HttpResponse("Transaction is not approved", status=403)
            html = render_to_string('transaction_detail_template.html', {'txn': txn})
            response = self.render_to_pdf(html, f"transaction_{txnid}.pdf")
            return response
        except Transaction.DoesNotExist:
            return HttpResponse("Transaction not found", status=404)

    def render_to_pdf(self, html_string, filename):
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        return HttpResponse(f'We had some errors <pre>{html_string}</pre>', content_type='text/html')
    


