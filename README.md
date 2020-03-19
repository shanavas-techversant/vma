# VMA

## Setup
  - Setup virtual environment
  ```sh
  virtualenv -p python3.6 venv
  ```
  - create configuration files for parent and child from `sample-config.json` template
  - Create databases for parent and child and update credentials in
    corresponding config file
  - start parent, client application
    ```sh
    ./start -f config-file.json
    ```

## Startup script

  Startup script supports a bunch of operations

``` sh
usage: ./start [-c cert-options] [-d] [-f configfile] [-p port] [-e vevn dir] | -s email password | -m | -h

    -c, --certs certoption       certificate options to be passed to gunicorn
    -d, --debug                  enable debug
    -e, --ven env-dir            virtual enviromrnt directory defaults to venv
    -f, --config  config-file    config file to use defaults to config.in
    -p, --port  port             port to bind application to
    -m, --migrate                create migrations
    -s, --seed email password    seed database
    -h, --help                   show this message and exit
```

## Working
  Parent service creates the database schema from [models](vma_app/models.py)
  and exposes an API `/api/v1/internal/schema` which provides database metadata
  (Serialized [SQLAlchemy MetaData](https://docs.sqlalchemy.org/en/13/core/metadata.html) Object).


  Client service on startup, accesses the above mentioned API and creates
  database schema from it.

  All clients that connect to parent service need to provide a client
  certificate trusted by server. Example certificates are provided [here](certs/)

#### Caveats
  - Current Implementation of database cloning doesn't handle table updates.
  Changes to a table that is already created in child won't be tracked further.
