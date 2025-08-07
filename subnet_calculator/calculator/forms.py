from django import forms

class SubnetCalculatorForm(forms.Form):
    network = forms.CharField(
        label='Base IPv4 Network (e.g., 192.168.1.0/24)',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    host_requirements = forms.CharField(
        label='Host Requirements (comma-separated, e.g., 50,20,10)',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email (optional, to receive results)',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

