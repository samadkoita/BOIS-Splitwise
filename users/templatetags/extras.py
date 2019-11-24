from django import template

register=template.Library()

@register.filter
def sub(value,arg):
	try:
		return value-arg
		
	except:
		print("mostly a type error")