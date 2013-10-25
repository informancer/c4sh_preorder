from django import forms

class FriendsApplicationField(forms.CharField):
	def validate(self, value):
		super(FriendsApplicationField, self).validate(value)

class FriendsApplicationForm(forms.Form):
	application = FriendsApplicationField(min_length=50, required=True)
