# recipe-app-api
Recipe API - A Standard Django API Template

# Test
docker-compose run --rm app -sh c "Python manage.py tests"
docker-compose run --rm app -sh c "flake8"

# Run
docker-compose up db && docker-compose up app

# Alt Run
docker-compose up
