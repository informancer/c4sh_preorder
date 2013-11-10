from preorder.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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

# User admin changes
class UserProfileInline(admin.StackedInline):
	model = UserProfile
	extra = 1

class UserAdminExtended(UserAdmin):
	list_display = ('username', 'email', 'is_active', 'is_staff')
	inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdminExtended)
