# VMA

## Setup
  - Setup virtual environment
  ```sh
  virtualenv -p python3.6 venv
  ```
  - Create databases for parent and child and update credentials in config.in
  - tunnel localhost connections so that facebook callbacks work
    ```sh
    ngork http 8000
    ```
  - update tunneled domain name in facebook Oauth settings
  - start parent, client application
    ```sh
    ./start
    ```

## Working
  Parent service creates the database schema from [models](parent_app/models.py)
  and exposes an API `/api/get-schema` which provides database metadata
  (Serialized [SQLAlchemy MetaData](https://docs.sqlalchemy.org/en/13/core/metadata.html) Object).


  Client service on startup, accesses the above mentioned API and creates
  database schema from it.

  All clients that connect to parent service need to provide a client
  certificate trusted by server. Example certificates are provided [here](certs/)

  Currently only `/fb-callback` route in parent app is SSO protected.

#### Caveats
  - Current Implementation of database cloning doesn't handle table updates.
  Changes to a table that is already created in child won't be tracked further.

  - The CA certificate that validates client certificates need to specified on
  application startup (for all nginx, gunicorn and flask) and can't be updated
  at runtime. This mandates the application restart for each issue or revocation
  of a client certificate (Assuming each client certificate has its own CA
  certificate at server). This can be addressed by patching client certificate
  verification handler (Werkzeug or gunicorn) or creating an nginx plugin to
  accept a directory instead of a list of CA certificates.
