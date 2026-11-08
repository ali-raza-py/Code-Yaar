import os

os.environ['DEBUG'] = 'False'
os.environ['PYTHON_DOTENV_DISABLED'] = '1'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.cloudflare')

from django.core.wsgi import get_wsgi_application
from workers import wsgi

application = get_wsgi_application()

Default = wsgi.entrypoint(application)
