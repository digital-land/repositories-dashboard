> [!IMPORTANT]
> This application is deprecated

# Application replacment

This application tracked the actions in github, we have sinced moved to airflow which tracks the runs made and their results.

# Github Repositories Dashboard


## What this dashboard shows

This shows the outcome of the github build actions of all the digital land repos.

The dashboard is deployed to [digital-land-dashboard](https://digital-land-dashboard.herokuapp.com/). 

## Local development

Make a virtualenv for the project and install python dependencies

    pip install

Set environment variables or provide a config file (see `config/config.py`).

Start the application

    flask run
