# ShowNxt API

## Practices

### Commits/Semver

```bash
brew install commitizen
```

```bash
cz c
```

## Local Development

### Setup

1. Run pre-commit install

    ```bash
    pre-commit install
    ```

2. Create a virtual environment

    ```bash
    python -m venv venv
    ```

3. Activate it

    ```bash
    source venv/bin/activate 
    ```

4. Install packages

    ```bash
    pip install -r requirements.txt  
    ```

### Convenience commands with Just

The justfile in the repo makes it a little faster for us to run common commands. For example, instead of needing to say `docker-compose exec web pytest -m unit` you can now say `just testu`. It also allows for passing in additional args e.g. `just testu -k test_retrieve_no_profiles -vv``.

To use just, you must first install it locally: `brew install just.`

View a list of available commands for the repo by running just, or `just --list`. Add new commands in the justfile.

### Running the Server

1. Build the image

    ```bash
    just up
    ```

2. Open another terminal

3. Apply migrations

    ```bash
    just migrate
    ```

4. Create an admin user to login with.

    ```bash
    docker compose exec web sh -c "DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_EMAIL=admin@site.com DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --noinput"
    ```

5. View the admin panel at [http://localhost:8000/admin/](http://localhost:8000/admin/) and login with the credentials from the previous step.

6. View the API docs at [http://localhost:8000/docs/](http://localhost:8000/docs/)

7. When you are done, stop the docker service with

    ```bash
    just down
    ```

### Tips

* `docker compose exec web sh -c "<COMMAND>"` runs your `<COMMAND>` against the running docker service
