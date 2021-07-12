# Welcome to RSS Scraper!

This is Django project that allow users to follow multiple RSS.


## Prerequisites

1- Docker (to install follow the [instructions](https://docs.docker.com/get-docker/)).
2- Docker compose (to install follow the [instructions](https://docs.docker.com/compose/install/)).

## Running the project
To run the project all you need to do is trun the following command
```
docker-compose -f local.yml up
```


# Commands
### Create super user
```
docker-compose -f local.yml exec app  ./manage.py createsuperuser --settings=settings.default
``` 
### Build
```
docker-compose -f local.yml build
```

### Run tests
> Before Running the tests please make sure that you have run the **Build** command 
```
docker-compose -f local.yml run app ./manage.py test --settings=settings.default
```
### Access shell
```
docker-compose -f local.yml exec app  ./manage.py shell --settings=settings.default
```

# API Documentation link
```
https://documenter.getpostman.com/view/1966537/Tzm8EaLA
```
