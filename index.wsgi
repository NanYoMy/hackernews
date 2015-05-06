import sae

from helloworld import app

application = sae.create_wsgi_app(app)
