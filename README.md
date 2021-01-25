# Github Repositories Dashboard

## Getting started

Make a virtualenv for the project and install python dependencies

    pip install

Set environment variables or provide a config file (see `config/config.py`).


Start the application

    flask run

The script `scripts/smoke_tests.py` contains a list of smoke tests used to ping Heroku applications and check the presence of a HTML marker within the response. This script will need to be set up with a scheduler (Heroku scheduler, cron etc).
