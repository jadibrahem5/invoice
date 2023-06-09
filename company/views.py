from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum, Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.datastructures import MultiValueDictKeyError
from django.views import View
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Client, Invoice, Product, Company
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.db import models
from .forms import *
from random import randint
from uuid import uuid4
import pdfkit
from django.template.loader import get_template

import os
from django.conf import settings, Settings
from xhtml2pdf import pisa


def loginpage(request):
    page = 'login'
    # if request.user.is_authenticated:
    #     return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user does not exist')
            return render(request, 'login.html', {'page': page})
        user = authenticate(request , username=username , password=password)
        if user is not None:
            login(request, user)
            return redirect('company_create')
        else:
            messages.error(request, 'username or password does not exist')
            return render(request, 'login.html', {'page': page})

    context = {'page': page}
    return render(request, 'login.html', context)

def singuppage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match")
    return render(request, 'signup.html')


def logout_view(request):
    logout(request)
    return redirect('login')


##########################dashboard######################
@login_required
def dash(request):
    try:
         company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        # Handle the case where the user is not associated with a company
        return render(request, 'company/company_create.html')
    clients = Client.objects.all()
    invoices = Invoice.objects.all()

    # Get the number of clients associated with this company
    num_clients = Client.objects.filter(company=company).count()
    num_invoices = Invoice.objects.filter(company=company).count()
    # Get the number of unpaid invoices associated with this company
    num_unpaid_invoices = Invoice.objects.filter(company=company, status='UNPAID').count()

    # Get the total revenue generated by this company
    total_revenue = Invoice.objects.filter(company=company, status='PAID').aggregate(total_revenue=models.Sum('total_price'))['total_revenue']
    #total_revenue =  float(total_revenue)
    # Get the 5 clients with the most invoices for this company
    most_paying_clients = Client.objects.filter(invoice__company=company, invoice__status='PAID').annotate(num_invoices=Count('invoice')).order_by('-num_invoices')[:5]

    # Get the 5 most recent invoices for this company
    recent_invoices = Invoice.objects.filter(company=company).order_by('-date')[:5]
    context = {
        'clients': clients,
        'company': company,
        'num_invoices': num_invoices,
        'num_clients': num_clients,
        'num_unpaid_invoices': num_unpaid_invoices,
        'total_revenue': total_revenue,
        'most_paying_clients': most_paying_clients,
        'recent_invoices': recent_invoices,
    }
    return render(request, 'index.html',context)

@login_required
def dashboard(request):
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        # Handle the case where the user is not associated with a company
        return render(request, 'company/company_create.html')

    # Get the number of clients associated with this company
    num_clients = Client.objects.filter(company=company).count()

    # Get the number of unpaid invoices associated with this company
    num_unpaid_invoices = Invoice.objects.filter(company=company, status='UNPAID').count()

    # Get the total revenue generated by this company
    total_revenue = Invoice.objects.filter(company=company, status='PAID').aggregate(total_revenue=models.Sum('total_price'))['total_revenue']

    context = {
        'company': company,
        'num_clients': num_clients,
        'num_unpaid_invoices': num_unpaid_invoices,
        'total_revenue': total_revenue,
    }
    return render(request, 'dashboard.html', context)

##########################products#########################################################


@login_required
def my_products(request):
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        # Handle the case where the user is not associated with a company
        return render(request, 'company/company_create.html')

    products = Product.objects.filter(company=company)

    return render(request, 'company/product.html', {'products': products})


@login_required
def add_product(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        currency = request.POST.get('currency')
        company = request.user.company

        try:
            product = Product.objects.create(
                title=title,
                description=description,
                quantity=quantity,
                price=price,
                currency=currency,
                company=company
            )
            messages.success(request, 'Product added successfully!')
            product.save()
            return redirect('products_list')
        except Exception as e:
            messages.error(request, f'Error occurred: {e}')
            return redirect('products_add')
    else:
        return render(request, 'company/products_add.html')


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        currency = request.POST.get('currency')

        product.title = title
        product.description = description
        product.quantity = quantity
        product.price = price
        product.currency = currency
        product.save()

        return redirect('products_list')
    else:
        return render(request, 'company/products_edit.html', {'product': product})


@login_required
def delete_product(request, product_id):
    user_company = request.user.company
    product = get_object_or_404(Product, id=product_id, company__user= request.user)
    product.delete()
    return redirect('products_list')


##########################clients#########################################################


@login_required
def my_clients(request):
    try:
     company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        # Handle the case where the user is not associated with a company
        return render(request, 'company/company_create.html')

    clients = Client.objects.filter(company=company)
    company = request.user.company

    if request.method == 'POST':
        name = request.POST['name']
        phoneNumber = request.POST['phoneNumber']
        address = request.POST['address']

        client = Client.objects.create(
            name=name,
            phoneNumber=phoneNumber,
            address=address,
            company=company
        )
        client.save()
        return redirect('clients_list')

    return render(request, 'company/client.html', {'clients': clients})

@login_required
def add_client(request):
    company = request.user.company

    if request.method == 'POST':
        name = request.POST['name']
        phoneNumber = request.POST['phoneNumber']
        address = request.POST['address']

        client = Client.objects.create(
            name=name,
            phoneNumber=phoneNumber,
            address=address,
            company=company
        )
        client.save()
        return redirect('clients_list')

    return render(request, 'company/client_add.html')

@login_required
def edit_client(request, client_id):
    company = request.user.company

    try:
        client = Client.objects.get(id=client_id, company=company)
    except Client.DoesNotExist:
        return redirect('clients_list')

    if request.method == 'POST':
        client.name = request.POST['name']
        client.phoneNumber = request.POST['phoneNumber']
        client.address = request.POST['address']
        client.save()

        return redirect('clients_list')

    return render(request, 'company/client_edit.html', {'client': client})
@login_required
def delete_client(request, client_id):
    user_company = request.user.company
    client = get_object_or_404(Client, id=client_id, company=user_company)
    client.delete()
    return redirect('clients_list')

##########################invoice#########################################################

@login_required
def invoices_list(request):
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        # Handle the case where the user is not associated with a company
        return render(request, 'company/company_create.html')
    user_company = request.user.company
    invoices = Invoice.objects.filter(company=company)
    for invoice in invoices:
        currency = ''
        for product in invoice.products.all():
            currency = product.currency

        invoice.currency = currency
    return render(request, 'company/invoices_list.html', {'invoices': invoices})
@login_required
def invoice_add(request):

    STATUS = [
        ('UNPAID', 'UNPAID'),
        ('PAID', 'PAID'),
    ]
    company = request.user.company
    products = Product.objects.filter(company=company)

    if request.method == 'POST':
        try:
            client = Client.objects.get(pk=request.POST.get('client'))
            product_ids = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            currency = request.POST.get('currency')
            status = request.POST.get('status')
            date = request.POST.get('date')
            due_date = request.POST.get('due_date')

            invoice = Invoice.objects.create(
                company=company,
                status=status,
                date=date,
                due_date=due_date,
                Client=client
            )

            total_price = 0
            for i, product_id in enumerate(product_ids):
                product = Product.objects.get(pk=int(product_id))
                quantity = int(quantities[i])

                product.quantity = quantity  # update the product quantity
                product.currency = currency
                product.save()
                invoice.products.add(product)
                total_price += product.price * quantity


            invoice.total_price = total_price
            invoice.save()

            return redirect('invoices_list')

        except MultiValueDictKeyError as e:
            return HttpResponseBadRequest(f"Invalid form data: {e}")

    clients = Client.objects.filter(company=company)

    return render(request, 'company/invoice_add.html', {'clients': clients, 'products': products,'STATUS':STATUS})
@login_required
def invoice_edit(request, invoice_id):

    STATUS = [
        ('UNPAID', 'UNPAID'),
        ('PAID', 'PAID'),
    ]
    company = request.user.company
    invoice = get_object_or_404(Invoice, pk=invoice_id, company=company)


    if request.method == 'POST':
        client = Client.objects.get(pk=request.POST.get('client'))
        products = request.POST.getlist('products[]')

        invoice.status = request.POST['status']
        invoice.date = request.POST['date']
        invoice.due_date = request.POST['due_date']
        invoice.Client = client
        invoice.products.clear()

        total_price = 0
        for product_id in products:
            product = Product.objects.get(pk=product_id)
            invoice.products.add(product)
            total_price += product.price

        invoice.total_price = total_price
        invoice.save()

        return redirect('invoices_list')

    clients = Client.objects.filter(company=company)
    products = Product.objects.filter(company=company)

    context = {
        'invoice': invoice,
        'clients': clients,
        'products': products,
        'STATUS': STATUS,
    }
    return render(request, 'company/invoice_edit.html', context)

@login_required
def invoice_delete(request, invoice_id):
    company = request.user.company
    invoice = get_object_or_404(Invoice, pk=invoice_id, company=company)
    invoice.delete()
    return redirect('invoices_list')
@login_required
def createInvoice(request):
    # create a blank invoice
    company = request.user.company
    new_invoice = Invoice.objects.create(company=company)

    # redirect to create_build_invoice view with new_invoice's id as a parameter
    return redirect('create_build_invoice', id=new_invoice.id)
@login_required
def createBuildInvoice(request, id):
    company = request.user.company

    # fetch that invoice
    try:
        invoice = Invoice.objects.get(id=id)
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices_list')
    products1 = Product.objects.filter(company=company)
    clients = Client.objects.filter(company=company)
    invoice_form = InvoiceForm()

    products = Product.objects.filter(invoice=invoice)
    if request.method == 'POST':


        # Use the client ID to retrieve the client object
      # initialize client to None
        try:
            client = Client.objects.get(pk=request.POST.get('client'))
            invoice.Client = client
        except Client.DoesNotExist:
            messages.error(request, 'Client does not exist')

        # handle adding product to invoice
        product_id = request.POST.get('product')
        quantity1 = request.POST.get('quantity')
        if product_id and quantity1:
            # create new invoice with the client

            print(invoice.Client.name)
            product = get_object_or_404(Product, id=product_id)
            product.quantity = quantity1
            product.save()

            invoice.products.add(product)
            invoice.save()
  #          return redirect('create_build_invoice', id=id)

    # if GET or invalid form submission, render the invoice creation page
    invoice_id = request.GET.get('invoice_id')
    if invoice_id:
        invoice = Invoice.objects.get(id=invoice_id)
        invoice_form = InvoiceForm(instance=invoice)
    else:
        invoice = None

    context = {
        'products1': products1,
        'products': products,
        'inv_form': invoice_form,
        'clients': clients,
        'invoice': invoice,
    }
    return render(request, 'company/create-invoice.html', context)
#
#
# def createBuildInvoice(request, id):
#     #fetch that invoice
#     try:
#         invoice = Invoice.objects.get(id=id)
#     except:
#         messages.error(request, 'Something went wrong')
#         return redirect('invoices_list')
#
#     if request.method == 'GET':
#         prod_form  = ProductForm()
#         inv_form = InvoiceForm(instance=invoice)
#         client_form = ClientSelectForm(initial_client=invoice.Client)
#         context = {
#             'invoice': invoice,
#             'products': Product.objects.filter(invoice=invoice),
#             'prod_form': prod_form,
#             'inv_form': inv_form,
#             'client_form': client_form
#         }
#         return render(request, 'company/create-invoice.html', context)
#
#     if request.method == 'POST':
#         prod_form = ProductForm(request.POST)
#         inv_form = InvoiceForm(request.POST, instance=invoice)
#         client_form = ClientSelectForm(request.POST, initial_client=invoice.Client, instance=invoice)
#
#         if prod_form.is_valid():
#             obj = prod_form.save(commit=False)
#             obj.invoice = invoice
#             obj.save()
#
#             messages.success(request, "Invoice product added succesfully")
#
#             # Update the products queryset with the newly added product
#             products = Product.objects.filter(invoice=invoice)
#             context = {
#                 'invoice': invoice,
#                 'products': products,
#                 'prod_form': prod_form,
#                 'inv_form': inv_form,
#                 'client_form': client_form
#             }
#             return render(request, 'company/create-invoice.html', context)
#         elif inv_form.is_valid and 'paymentTerms' in request.POST:
#             inv_form.save()
#
#             messages.success(request, "Invoice updated succesfully")
#             return redirect('create_build_invoice', id=id)
#         elif client_form.is_valid() and 'client' in request.POST:
#
#             client_form.save()
#             messages.success(request, "Client added to invoice succesfully")
#             return redirect('create_build_invoice', id=id)
#         else:
#             context = {
#                 'invoice': invoice,
#                 'products': Product.objects.filter(invoice=invoice),
#                 'prod_form': prod_form,
#                 'inv_form': inv_form,
#                 'client_form': client_form
#             }
#             messages.error(request,"Problem processing your request")
#             return render(request, 'company/create-invoice.html', context)

##########################company#########################################################


@login_required
def company_create(request):
    user = request.user
    if Company.objects.filter(user=user).exists():
        messages.error(request, 'You already have a company.')
        return redirect('company')
    if request.method == 'POST':
        user = request.user
        company_name = request.POST.get('companyName')
        address = request.POST.get('address')
        postal_code = request.POST.get('postalCode')
        phone_number = request.POST.get('phoneNumber')
        email = request.POST.get('email')
        tax_id = request.POST.get('taxID')
        website = request.POST.get('website')

        # handle company logo image upload
        if request.FILES.get('companyLogo'):
            company_logo = request.FILES['companyLogo']



            company = Company.objects.create(
                user=user,
                companyName=company_name,
                address=address,
                postalCode=postal_code,
                phoneNumber=phone_number,
                email=email,
                taxID=tax_id,
                website=website,
                companyLogo=company_logo
            )
            company.save()
        return redirect('company')

    return render(request, 'company/company_create.html')


@login_required
def company_view(request):
    company = request.user.company
    return render(request, 'company/company.html', {'company': company})

@login_required
def company_edit(request):
    company = request.user.company

    if request.method == 'POST':
        user = request.user
        company_name = request.POST.get('companyName')
        address = request.POST.get('address')
        postal_code = request.POST.get('postalCode')
        phone_number = request.POST.get('phoneNumber')
        email = request.POST.get('email')
        tax_id = request.POST.get('taxID')
        website = request.POST.get('website')

        # handle company logo image upload
        if request.FILES.get('companyLogo'):
            company_logo = request.FILES['companyLogo']
        else:
            company_logo = company.companyLogo

        company.user = user
        company.companyName = company_name
        company.address = address
        company.postalCode = postal_code
        company.phoneNumber = phone_number
        company.email = email
        company.taxID = tax_id
        company.website = website
        company.companyLogo = company_logo
        company.save()

        return redirect('company')

    return render(request, 'company/company_edit.html', {'company': company})









@login_required
def view_invoice(request, invoice_id):
    invoice = Invoice.objects.get(pk=invoice_id)

    # Check if the invoice belongs to the logged-in user's company
    if invoice.company.user != request.user:
        return render(request, 'error.html', {'error_message': 'You do not have permission to view this invoice.'})

    # Get the invoice details
    company_name = invoice.company.companyName
    company_address = invoice.company.address
    company_logo = invoice.company.companyLogo
    client_name = invoice.Client.name
    client_address = invoice.Client.address
    client_phone = invoice.Client.phoneNumber
    invoice_date = invoice.date
    invoice_due_date = invoice.due_date
    invoice_status = invoice.status


    # Get the product details
    products = []
    total_price = 0
    for product in invoice.products.all():
        product_title = product.title
        product_description = product.description
        product_quantity = product.quantity
        product_price = product.price
        total_price += product_price

        product_currency = product.currency
        products.append({
            'title': product_title,
            'description': product_description,
            'quantity': product_quantity,
            'price': product_price,
            'currency': product_currency,
        })


    return render(request, 'company/invoice.html', {'company_name': company_name, 'company_address': company_address, 'company_logo': company_logo, 'client_name': client_name, 'client_address': client_address, 'client_phone': client_phone, 'invoice_date': invoice_date, 'invoice_due_date': invoice_due_date, 'invoice_status': invoice_status, 'total_price': total_price, 'products': products})




def viewPDFInvoice(request,invoice_id):
    #fetch that invoice
    try:
        invoice = Invoice.objects.get(pk=invoice_id)
        pass
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices_list')

    #fetch all the products - related to this invoice
    products = Product.objects.filter(invoice=invoice)

    #Get Client Settings
    company = request.user.company
    client = invoice.Client
    #Calculate the Invoice Total
    invoiceCurrency = ''
    invoiceTotal = 0.0
    if len(products) > 0:
        for x in products:
            y = float(x.quantity) * float(x.price)
            invoiceTotal += y
            invoiceCurrency = x.currency



    context = {}
    context['invoice'] = invoice
    context['client'] = client
    context['products'] = products
    context['company'] = company
    context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)
    context['invoiceCurrency'] = invoiceCurrency

    return render(request, 'company/invoice-template.html', context)




def viewDocumentInvoice(request,invoice_id):
    #fetch that invoice
    try:
        invoice = Invoice.objects.get(pk=invoice_id)
        pass
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    #fetch all the products - related to this invoice
    products = Product.objects.filter(invoice=invoice)

    company = request.user.company
    client = invoice.Client
    #Calculate the Invoice Total
    invoiceTotal = 0.0
    if len(products) > 0:
        for x in products:
            y = float(x.quantity) * float(x.price)
            invoiceTotal += y



    context = {}
    context['invoice'] = invoice
    context['products'] = products
    context['company'] = company
    context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)

    #The name of your PDF file
    filename = '{}.pdf'.format(invoice.id)

    #HTML FIle to be converted to PDF - inside your Django directory
    template = get_template('company/pdf-template.html')


    #Render the HTML
    html = template.render(context)

    #Options - Very Important [Don't forget this]
    options = {
          'encoding': 'UTF-8',
          'javascript-delay':'2', #Optional
          'enable-local-file-access': None, #To be able to access CSS
          'page-size': 'A4',
          'custom-header' : [
              ('Accept-Encoding', 'gzip')
          ],
      }
      #Javascript delay is optional

    #Remember that location to wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')


    #IF you have CSS to add to template
    css1 = os.path.join(settings.CSS_LOCATION, 'assets', 'css', 'bootstrap.min.css')
    css2 = os.path.join(settings.CSS_LOCATION, 'assets', 'css', 'dashboard.css')

    #Create the file
    file_content = pdfkit.from_string(html, False, configuration=config, options=options)

    #Create the HTTP Response
    response = HttpResponse(file_content, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename = {}'.format(filename)

    #Return
    return response

def generate_pdf(request,invoice_id):
    # fetch that invoice
    try:
        invoice = Invoice.objects.get(pk=invoice_id)
        pass
    except:
        messages.error(request, 'Something went wrong')
        return redirect('invoices')

    # fetch all the products - related to this invoice
    products = Product.objects.filter(invoice=invoice)

    company = request.user.company
    client = invoice.Client
    # Calculate the Invoice Total
    invoiceTotal = 0.0
    if len(products) > 0:
        for x in products:
            y = float(x.quantity) * float(x.price)
            invoiceTotal += y

    context = {}
    context['invoice'] = invoice
    context['products'] = products
    context['company'] = company
    context['invoiceTotal'] = "{:.2f}".format(invoiceTotal)
    template = get_template('company/pdf-template.html')
    html = template.render(context)

    links = lambda uri, rel: os.path.join(settings.MEDIA_ROOT,
                                          uri.replace(settings.MEDIA_URL, ''))
     # Create a PDF object, and write HTML to it
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="invoice.pdf"'
    pdf = pisa.CreatePDF(html, dest=response, link_callback=links)
    # If the PDF is successfully created, return it
    if not pdf.err:
        return response
    return HttpResponse('Error generating PDF')