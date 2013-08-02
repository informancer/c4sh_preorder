from django import forms
from preorder.models import *
from django.contrib.auth.forms import SetPasswordForm
import re
from django.utils.translation import ugettext as _
from captcha.fields import CaptchaField

class UsernameField(forms.CharField):
	def validate(self, value):
		super(UsernameField, self).validate(value)

		try:
			u = User.objects.get(username=value)
			raise forms.ValidationError(_("This username has already been taken."))
		except User.DoesNotExist:
			pass

class GoldenTokenField(forms.CharField):
	def validate(self, value):
		super(GoldenTokenField, self).validate(value)

		try:
			t = GoldenToken.objects.get(token=value)
			if t.redeemed == True:
				raise forms.ValidationError(_("This token has already been redeemed."))
		except GoldenToken.DoesNotExist:
			raise forms.ValidationError(_("This token does not exist."))

class GoldenTokenForm(forms.Form):
	token = GoldenTokenField(max_length=50, required=True)

class SignupForm(forms.Form):
	username = UsernameField(max_length=100, required=True)
	password = forms.CharField(min_length=8, max_length=255, required=True)
	email = forms.EmailField(required=False)
	captcha = CaptchaField()

	class Meta:
		model = User

	def clean_email(self):
		email = self.cleaned_data.get('email')
		username = self.cleaned_data.get('username')
		if email and User.objects.filter(email=email).exclude(username=username).count():
			raise forms.ValidationError(u'Email addresses must be unique.')
		return email

class EmailForm(forms.Form):
	email = forms.EmailField(required=True)

class CSVForm(forms.Form):
	csv_file = forms.FileField()

class PasswordForm(forms.Form):
	old_password = forms.CharField(required=True)
	new_password1 = forms.CharField(required=True)
	new_password2 = forms.CharField(required=True)
	def __init__(self, user, *args, **kwargs):
		self.user = user
		super(PasswordForm, self).__init__(*args, **kwargs)	

	def clean(self):
		cleaned_data = self.cleaned_data
		if 'new_password1' in cleaned_data and 'new_password2' in cleaned_data:
			if cleaned_data.get('new_password1') != cleaned_data.get('new_password2'):
				raise forms.ValidationError(_("The two password fields didn't match."))
			if len(cleaned_data.get('new_password1')) < 8:
				raise forms.ValidationError(_("Your password has to be at least 8 characters long."))
			if not re.search('\d+', cleaned_data.get('new_password1')) or not re.search('([a-zA-Z])+', cleaned_data.get('new_password1')):
				raise forms.ValidationError(_("Your password needs to contain at least one number and one character."))
			if not self.user.check_password(cleaned_data.get('old_password')):
				raise forms.ValidationError(_("This is not your current password."))
		
		return cleaned_data

class BillingAddressForm(forms.Form):
	company = forms.CharField(required=False)
	firstname = forms.CharField(required=True)
	firstname = forms.CharField(required=True)
	lastname = forms.CharField(required=True)
	address1 = forms.CharField(required=True)
	address2 = forms.CharField(required=False)
	city = forms.CharField(required=True)
	zip = forms.CharField(required=True)
	country = forms.CharField(required=True)