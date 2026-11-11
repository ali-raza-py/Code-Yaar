import os

os.environ['DEBUG'] = 'False'
os.environ['PYTHON_DOTENV_DISABLED'] = '1'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.cloudflare')

from workers import wsgi


_application = None


def application(environ, start_response):
    global _application
    if _application is None:
        from django.core.wsgi import get_wsgi_application

        _application = get_wsgi_application()
    return _application(environ, start_response)


Default = wsgi.entrypoint(application)
