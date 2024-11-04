from django import forms

from django.contrib.auth import get_user_model
from .models import Transport, TransportPrice
User = get_user_model()

from .models import VehicleType

class VehicleTypeForm(forms.ModelForm):
    class Meta:
        model = VehicleType
        fields = ['name', 'max_pallets']

class TransportForm(forms.ModelForm):
    class Meta:
        model = Transport
        fields = ['destination', 'delivery_date', 'pickup_time', 'transporters']
        widgets = {
            'transporters': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transporters'].queryset = User.objects.filter(user_type='transportator')


class TransportPriceForm(forms.ModelForm):
    class Meta:
        model = TransportPrice
        fields = ['price']

    def __init__(self, *args, **kwargs):
        self.transport = kwargs.pop('transport', None)
        super().__init__(*args, **kwargs)



class TransportFilterForm(forms.Form):
    destination = forms.CharField(
        label='Destinatie',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        label='Status',
        required=False,
        choices=[
            ('', 'Alege un status'),
            ('pending', 'În așteptare'),
            ('allocated', 'Alocat'),
            ('departed', 'Plecat'),
            ('completed', 'Finalizat'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    delivery_date = forms.DateField(
        label='Data livrarii',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
