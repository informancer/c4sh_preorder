# Django settings for c4sh project.
import socket, sys

if socket.gethostname() == "$YOUR_DEPLOYMENT_HOST":
	DEFAULT_FROM_EMAIL = "orga@example.com"
	DEBUG = False
	TEMPLATE_DEBUG = DEBUG
	APP_URL = "preorder"
	EMAIL_BACKEND = 'c4sh_preorder.preorder.sendmail.EmailBackend'
	MEDIA_ROOT = '/home/www/presale/c4sh_preorder/media/'
	MEDIA_URL = '/media/'
	STATIC_ROOT = '/home/www/presale/c4sh_preorder/static/'
	STATIC_URL = '/static/'
	TEMPLATE_DIRS = (
		"/home/www/presale/c4sh_preorder/templates",
	)
	DATABASES = {
		'default': {
			'NAME': 'dpresale',
			'ENGINE': 'django.db.backends.mysql',
			'USER': 'upresale',
			'HOST': 'localhost',
			'PASSWORD': 'ppresale6'
		}
	}
	SECRET_KEY = 'change this to a long random string'
	ADMINS = (
		('you', 'where@errors.will.be.sent'),
	)

	# is this a ssl installation?
	import sys
	try:
		if (sys.argv[1] != 'runserver'):
			SESSION_COOKIE_SECURE = True
	except:
		pass
	
	# path to c4sh installation. at least preorder models required.
	sys.path.append('/home/www/presale/')

	# path to c4sh_preorder installation. required for gunicorn
	sys.path.append('/home/www/presale/c4sh_preorder/')

	# import event settings from file event_sigint12.py
	from event_sigint12 import *
elif socket.gethostname() == "devhost.local":
	DEFAULT_FROM_EMAIL = "foo@bar"
	DEBUG = True
	TEMPLATE_DEBUG = DEBUG
	APP_URL = "preorder"
	EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
	MEDIA_ROOT = '/Users/zakx/git/c4sh_preorder/media/'
	MEDIA_URL = '/media/'
	STATIC_ROOT = '/Users/zakx/git/c4sh_preorder/static/'
	STATIC_URL = '/static/'
	TEMPLATE_DIRS = (
		"/Users/zakx/git/c4sh_preorder/templates",
	)
	DATABASES = {
		'default': {
			'NAME': '/Users/zakx/git/c4sh.sqlite3',
			'ENGINE': 'django.db.backends.sqlite3',
		}
	}
	SECRET_KEY = 'change this to a long random string'
	ADMINS = (
		('zakx', 'zakx@example.com'),
	)
	SESSION_COOKIE_SECURE = False
	
	# path to c4sh installation. at least preorder models required.
	sys.path.append('/Users/zakx/git')

	# path to c4sh_preorder installation. required for gunicorn
	sys.path.append('/Users/zakx/git/c4sh_preorder/')

	# import event settings
	from event_sigint12 import *
else:
	import sys
	print "Please configure c4sh_preorder in settings.py. Your hostname is %s." % socket.gethostname()
	sys.exit(0)


SESSION_COOKIE_HTTPONLY = True
MANAGERS = ADMINS
TIME_ZONE = 'Europe/Berlin'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
ADMIN_MEDIA_PREFIX = '/static/admin/'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"preorder.context_preprocessors.app_settings",
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.i18n",
	"django.contrib.messages.context_processors.messages"
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.transaction.TransactionMiddleware', # <- important
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
ROOT_URLCONF = 'c4sh_preorder.urls'

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin',
	'django.contrib.admindocs',
	'c4sh_preorder.preorder',
	'captcha',
	'south'
)

# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': {
		'mail_admins': {
			'level': 'ERROR',
			'class': 'django.utils.log.AdminEmailHandler'
		},
		'file': {
			'level': 'DEBUG',
			'class': 'logging.FileHandler',
			'filename': 'preorder.log'
		}
	},
	'loggers': {
		'django.request': {
			'handlers': ['mail_admins'],
			'level': 'ERROR',
			'propagate': True,
		},
		'c4sh_preorder.preorder.management.commands': {
			'handlers': ['file'],
			'level': 'INFO',
			'propagate': True,	
		},
	}
}
