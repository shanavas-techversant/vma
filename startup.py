"""
In this sample, the Flask app object is contained within the vma_app *module*;
that is, vma_app contains an __init__.py along with relative imports. Because
of this structure, a file like webapp.py cannot be run directly as the startup
file through Gunicorn; the result is "Attempted relative import in non-package".

The solution is to provide a simple alternate startup file, like this present
startup.py, that just imports the app object. You can then just specify
vma_app:app in the Gunicorn command.
"""

import ssl
from werkzeug import serving

from vma_app.webapp import app


# for flask dev server
# TODO get details from command line args
if __name__ == "__main__":
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_CRT = "certs/server.crt"
    API_KEY = "certs/server.key"
    API_CA_T = "certs/root_ca.crt"

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(API_CA_T)
    context.load_cert_chain(API_CRT, API_KEY)

    serving.run_simple(API_HOST, API_PORT, app, ssl_context=context)
