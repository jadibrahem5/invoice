from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import widgets
from .models import *
import json

#Form Layout from Crispy Forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column



class DateInput(forms.DateInput):
    input_type = 'date'


class UserLoginForm(forms.ModelForm):
    username = forms.CharField(
                            widget=forms.TextInput(attrs={'id': 'floatingInput', 'class': 'form-control mb-3'}),
                            required=True)
    password = forms.CharField(
                            widget=forms.PasswordInput(attrs={'id': 'floatingPassword', 'class': 'form-control mb-3'}),
                            required=True)

    class Meta:
        model=User
        fields=['username','password']


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name','phoneNumber','address']



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['id','title', 'description', 'quantity', 'price', 'currency']


class InvoiceForm(forms.ModelForm):
    STATUS = [
        ('UNPAID', 'UNPAID'),
        ('PAID', 'PAID'),
    ]


    status = forms.ChoiceField(
                    choices = STATUS,
                    required = True,
                    label='Change Invoice Status',
                    widget=forms.Select(attrs={'class': 'form-control mb-3'}),)

    duedate = forms.DateField(
                        required = True,
                        label='Invoice Due',
                        widget=DateInput(attrs={'class': 'form-control mb-3'}),)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('duedate', css_class='form-group col-md-6'),
                css_class='form-row'),
            Row(

                Column('status', css_class='form-group col-md-6'),
                css_class='form-row'),
            'notes',

            Submit('submit', ' EDIT INVOICE '))

    class Meta:
        model = Invoice
        fields = [ 'duedate','status']


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['companyName', 'companyLogo', 'address','postalCode', 'phoneNumber', 'email','website', 'taxID']



class ClientSelectForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        self.initial_client = kwargs.pop('initial_client')
        self.CLIENT_LIST = Client.objects.all()
        self.CLIENT_CHOICES = [('-----', '--Select a Client--')]


        for client in self.CLIENT_LIST:
            d_t = (client.id, client.name)
            self.CLIENT_CHOICES.append(d_t)


        super(ClientSelectForm,self).__init__(*args,**kwargs)

        self.fields['Client'] = forms.ChoiceField(
                                        label='Choose a related client',
                                        choices = self.CLIENT_CHOICES,
                                        widget=forms.Select(attrs={'class': 'form-control mb-3'}),)

    class Meta:
        model = Invoice
        fields = ['Client']


    def clean_client(self):
        c_client = self.cleaned_data['client']
        if c_client == '-----':
            return self.initial_client
        else:
            return Client.objects.get(uniqueId=c_client)




















