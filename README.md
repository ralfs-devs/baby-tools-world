# Baby Tools World

This repository contains the source code of the Baby Tools World web shop, a simple
full stack application written in Python using Django. Products are grouped by
categories, can be tagged with descriptive labels, and rated by registered users
and guests. Administrators manage catalog data through the Django admin panel.
The project was developed for educational purposes only.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quickstart](#quickstart)
- [Usage](#usage)
  - [Configuration](#configuration)
  - [Seeding the Database](#seeding-the-database)
  - [Testing](#testing)
  - [Admin Panel](#admin-panel)
- [Project Structure](#project-structure)
- [Docker Container](#docker-container)

## Prerequisites

To work with this repository you need the following tools installed on your machine:

- **Git** for cloning the repository
- **Python 3.12 or later** including `pip`
- A virtual environment tool (`venv` ships with Python)
- **Docker** or any OCI-compliant container engine (only needed for the optional
  container section)
- An editor or IDE of your choice (VS Code, PyCharm, etc.)

## Quickstart

**1. Clone the repository into a local folder**
   
   Create a folder and navigate to it in your terminal,  
   then run
   
   ```bash
   git clone https://github.com/ralfs-devs/baby-tools-world.git
   cd baby-tools-world
   ```

**2. Create and activate a virtual environment**
   
   Create a virtual environment with
   ```bash
   python -m venv .venv
   ```
   
   And activate it  

   for Linux/Mac Systems:
   ```bash
   source .venv/bin/activate
   ```
   or for Windows:
   ```bash
   .venv\Scripts\activate
   ```  


**3. Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

**4. Configure environment variables**

   ```bash
   cp example.env src/.env
   ```

**5. Prepare the database and start the server**

   ```bash
   cd src
   python manage.py migrate
   python manage.py runserver
   ```

**6. Verify**

   Open `http://localhost:8000` in your browser.

**7. (optional): Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

## Usage

- Browse the homepage to see all categories and products.
- Open a product detail page to view its description, rating summary and product tags.
  Products without tags show the label "no tags available".
- Log in as an admin at `/admin/` to manage products, categories and tags.
- Submit a rating or comment. After a successful submission the form fields
  (rating stars and comment text) are cleared automatically.

### Configuration

If not done during Quickstart copy the example environment file and adjust it to your needs:

```bash
cp example.env src/.env
```

- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts. Defaults to `localhost, 127.0.0.1, 0.0.0.0`
- `DEBUG`: Set to `True` for development or `False` for production.

### Seeding the Database

To fill the database with sample categories and products, run:

```bash
python manage.py seed_db
```

### Testing

Run the test suite from the `src` directory:

```bash
python manage.py test
```

### Admin Panel

To manage the application data, log in to the Django admin panel at
`http://localhost:8000/admin/` with your superuser credentials.

If you have not yet created a superuser you can do it now:

```bash
python manage.py createsuperuser
```

The admin panel allows you to create and manage products, categories,
tags, and comments.

## Project Structure

- `src/`: Application source code containing the Django project, apps, templates and settings.
- `src/products/`: Manages products, categories, tags, comments and ratings.
- `src/users/`: Handles user authentication and registration.
- `src/products/tests/`: Unit tests for models, views, templates and admin registration.
- `requirements.txt`: All pinned project dependencies.

## Docker Container
This point is optional:  

Build the container image:

```bash
docker build -t baby-tools-world:local .
```

Start a container:

```bash
docker run --rm -it -p 8000:8000 baby-tools-world:local
```

To override the predefined environment configuration, provide an `.env` file:

```bash
docker run --rm -it -p 8000:8000 --env-file .env baby-tools-world:local
```

The application is then reachable at `http://localhost:8000`.