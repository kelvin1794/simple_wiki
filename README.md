# simple_wiki

Project that setup a database from Simple Wiki's dump programmatically.

Expose the data two a few endpoints with Django and Django Rest Framework.

## Installation
- Docker
- VS Code with Remote Container extension

## Development
Once installed Docker, start the project with VS Code inside the pre-defined containers with `./devcontainer`
To view and run notebook, we can manually install `ipykernel`. This is not always needed so we don't need to include it in the build.

## Deployment
This project is build for container deployment.
Once ready to deploy, use `.env.sample` file to create a `.env` file and user the `Docker-compose` file to build a container.

## Enhancement

The project is just a minimal example of how the Wiki data can be processed into a application running on production. We can further improve this in my way, let's name a few:

- Create a frontend to have better user experience of managing the tasks
- Use a more mature tool for scheduling jobs like Airflow, Celery, etc.
