from preorder.models import *
from django.contrib import admin

class BillingAddressInline(admin.StackedInline):
	model = PreorderBillingAddress
	extra = 0

class PositionsInline(admin.StackedInline):
	model = PreorderPosition
	extra = 1

class CustomPreorderAdmin(admin.ModelAdmin):
	list_display = ('username', 'time', 'get_sale_amount')
	inlines = [PositionsInline, BillingAddressInline]
	search_fields = ['username', 'unique_secret']
	list_filter = ['username', 'time']


admin.site.register(PreorderQuota)
admin.site.register(CustomPreorderTicket)
admin.site.register(Merchandise)
admin.site.register(Tshirt)
admin.site.register(CustomPreorder, CustomPreorderAdmin)
admin.site.register(GoldenToken)
