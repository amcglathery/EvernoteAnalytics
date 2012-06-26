import os
ROOT_PATH = os.path.dirname(__file__)

DATABASES = {
   'default': {
      'ENGINE': 'django.db.backends.sqlite3', 
      'NAME': os.path.join(ROOT_PATH, 'db.sqlite'),
      'USER': '', 
      'PASSWORD': '',
      'HOST': '',
      'PORT': '',                      
  }
}
