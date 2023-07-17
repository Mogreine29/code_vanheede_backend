# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 23:27:42 2022

@author: Cedri
"""

# authentication/forms.py
from django import forms
from django.forms import ModelForm
from .models import Bulles,Site

class User(forms.Form):
    username = forms.CharField(label="Username ", max_length=30, widget=forms.TextInput(attrs={'class':'', 'placeholder' : 'Username'}))
    password = forms.CharField(label="Password  ", widget=forms.PasswordInput(attrs={'class':'', 'placeholder' : 'Password'}))


bulles = Bulles.objects.select_related('id_site').all()

adresse = [(bulle.id_bulle, bulle.id_site.nom) for bulle in bulles]

class BinForm(ModelForm):
    class Meta:
        model = Bulles
        fields = ('id_bulle','num_bulle','type_bulle','colories','latitude','longitude','date_vidange','id_depot','id_site')
        label = {
            'id_bulle' : '',
            'num_bulle' : '',
            'type_bulle' : '',
            'colories' : '',
            'latitude' : '',
            'longitude' : '',
            'date_vidange' :'', 
            'id_depot' : '',
            'id_site' : '',
        }
        
        CHOICES = (('Coloured', 'Coloured'),('White', 'White'),('Coloured/White', 'Coloured/White'))
        CHOICES2 = (('Mono', 'Mono'),('Double', 'Double'),('Mono ent', 'Mono ent'),('Double ent', 'Double ent'))
        
        widgets = {
            'num_bulle' : forms.TextInput(attrs={'class':'form-control2', 'placeholder' : 'Numero de la bulle'}),
            'type_bulle' : forms.Select(attrs={'class':'form-control2', 'placeholder':''}, choices = CHOICES2),
            'colories' : forms.Select(attrs={'class':'form-control2', 'placeholder':''}, choices = CHOICES),
            'latitude' : forms.NumberInput(attrs={'class':'form-control2', 'placeholder':'Latitude', 'step':'.0001'}),
            'longitude' : forms.NumberInput(attrs={'class':'form-control2', 'placeholder':'Longitude','step':'.0001'}),
            'date_vidange' : forms.DateInput(attrs={'class':'form-control2', 'type':'date'}),
            'id_depot' : forms.Select(attrs={'class':'form-control2', 'placeholder':'Id_depot'}),
            'id_site' : forms.Select(attrs={'class':'form-control2', 'placeholder':'Id_site'}, choices = adresse),

            }

class SiteForm(ModelForm):
    class Meta:
        model = Site
        fields = ('id_site','id_depot','nom','type_site','longitude','latitude','date_vidange')
        
        Labels = {
            'id_site' : '',
            'id_depot' : '',
            'nom' : '',
            'type_site' :'', 
            'longitude' : '',
            'latitude' : '',
            'date_vidange' : '',
        }
        
        CHOICES = (('Site', 'Site'),('Recycle Park', 'Recycle Park'))
        CHOICES2 = (('1', 'Quévy'),('2', 'Dottignies'),('3', 'Mineral'))

        widgets = {
            'id_site' : forms.TextInput(attrs={'class':'form-control2', 'placeholder' : 'Id_site'}),
            'id_depot' : forms.Select(attrs={'class':'form-control2', 'placeholder':'Id_depot'}, choices = CHOICES2),
            'nom' : forms.TextInput(attrs={'class':'form-control2', 'placeholder' : 'Adresse du site',}),
            'type_site' : forms.Select(attrs={'class':'form-control2', 'placeholder' : 'Type de site'}, choices = CHOICES),
            'longitude' : forms.NumberInput(attrs={'class':'form-control2', 'placeholder' : 'longitude','step':'.0001'}),
            'latitude' : forms.NumberInput(attrs={'class':'form-control2', 'placeholder' : 'latitude','step':'.0001'}),
            'date_vidange' : forms.DateInput(attrs={'class':'form-control2','type':'date'}),
            }