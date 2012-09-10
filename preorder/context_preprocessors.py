from django.conf import settings # import the settings file

def app_settings(context):
    return {'settings': settings}