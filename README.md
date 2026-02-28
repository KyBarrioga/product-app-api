# Product App API

A Django REST API template for managing products with a robust, scalable architecture. This project includes user authentication, product management, and a clean API structure following Django best practices and can be used for any future Django projects.

## Overview

This application provides a complete backend API solution for product management built with Django and Django REST Framework. It features a containerized setup using Docker and Docker Compose for easy development and deployment. Built for personal use for any future Django projects.

## Prerequisites

- **Docker** - Container platform for running the application
- **Docker Compose** - Tool for defining and running multi-container Docker applications
- **Python 3.9+** - Required for local development (optional if using Docker)

## Project Structure

- **core/** - Core app with database models and admin configuration
- **product/** - Product management app with API endpoints for products, tags, and ingredients
- **user/** - User authentication and management
- **app/** - Main Django project settings and configuration

## Getting Started

### Quick Start

Build and start all services (database and application):

```bash
docker-compose up
```

Alternatively, start services individually:

```bash
docker-compose up db && docker-compose up app
```

## Testing

Run the complete test suite including unit tests and code linting:

```bash
# Run all tests
docker-compose run --rm app sh -c "python manage.py test"

# Run code linter (flake8) to check code quality
docker-compose run --rm app sh -c "flake8"
```

The test suite covers:
- Model tests
- API endpoint tests
- Admin functionality tests
- Database commands and migrations

## Development

### Running the Application

Start the development server with:

```bash
docker-compose up
```

The API will be available at `http://localhost:8000`

### Common Commands

```bash
# Access Django shell
docker-compose run --rm app sh -c "python manage.py shell"

# Create database migrations
docker-compose run --rm app sh -c "python manage.py makemigrations"

# Apply migrations
docker-compose run --rm app sh -c "python manage.py migrate"

# Create superuser for admin access
docker-compose run --rm app sh -c "python manage.py createsuperuser"
```

## API Endpoints

The application provides RESTful API endpoints for:
- User registration and authentication
- Product management
- Tags management
- Ingredients management

Access the browsable API at `http://127.0.0.1:8000/api/docs/#/`
