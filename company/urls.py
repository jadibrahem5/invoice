from django.urls import  path ,include
from . import  views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns =[
    path('singup/', views.singuppage,name= "singup"),
    path('', views.loginpage, name="login"),
    path('login',views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dash/', views.dash, name='dash'),

    path('products_list/', views.my_products, name='products_list'),
    path('products_add/', views.add_product, name='products_add'),
    path('prodcuts/edit/<int:product_id>/', views.edit_product, name='products_edit'),
    path('prodcuts/edit/<int:product_id>/delete/', views.delete_product, name='delete_product'),

    path('clients/', views.my_clients, name='clients_list'),
    path('clients/add/', views.add_client, name='client_add'),
    path('clients/edit/<int:client_id>/', views.edit_client, name='client_edit'),
    path('clients/edit/<int:client_id>/delete/', views.delete_client, name='client_delete'),

    path('invoices/create',views.createInvoice, name='create-invoice'),
    path('invoices/create/<int:id>/',views.createBuildInvoice, name='create_build_invoice'),
    path('invoices_list/', views.invoices_list, name='invoices_list'),
    path('invoices/add/', views.invoice_add, name='invoice_add'),
    path('invoices/edit/<int:invoice_id>/', views.invoice_edit, name='invoice_edit'),
    path('invoices/edit/<int:invoice_id>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoice/<int:invoice_id>/', views.view_invoice, name='invoice'),

    path('company_edit/', views.company_edit, name='company_edit'),
    path('company_create/', views.company_create, name='company_create'),
    path('company/', views.company_view, name='company'),

    path('invoices/view/<int:invoice_id>/',views.viewPDFInvoice, name='invoice-template'),
    path('invoices/view-document/<int:invoice_id>/',views.generate_pdf, name='view-document-invoice'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
