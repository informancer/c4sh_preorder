from django import template

# this is LOL, but it finally works.

register = template.Library()

@register.filter
def get_index(value, arg):
	try:
		return value[arg]
	except:
		return False
