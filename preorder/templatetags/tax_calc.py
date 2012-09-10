from django import template

# this is LOL, but it finally works.

register = template.Library()

@register.filter 
def tax_calc(value, arg):
	if value and arg:
		return float(value) * (float(1-(float(arg)/100)))
	else:
		return