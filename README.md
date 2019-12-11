# nydata

New Yorker Data exercise

## Basic Requirements

This readme assumes an installed and up-to-date version of 

- `python3.7` (for the proof of concept script)
- `docker` and
- `docker-compose`.

## Quick Proof of Concept

**Requirement:** Please ensure that the ports **5000** and **5432** are available.
You just want to try out the proof of concept:

I. Ensure to provide a NGINX log file. If you do not have one
you can copy it from `nydata/tests/test_log/test_access.log`

```bash
sudo mkdir /var/log/nginx/
sudo cp tests/test_log/test_access.log /var/log/nginx/access.log
```

II. Make a copy of `.env.example` -> `.env`
```
cp .env.example .env
```

III. Start up `docker-compose`

```
sudo docker-compose up db flask-prod
```

IV. **In another shell** create a `virtualenv` and install all
dependencies.

```
mkdir ~/envs/
virtualenv ~/envs/nydata/ --python=python3.7
source ~/envs/nydata/bin/activate
(nydata) cd nydata
(nydata) pip install -r requirements/dev.txt
```

V. Run the proof of concept script in the project root:

```
(nydata) python poc.py
```


**Attention:** Unfortunately there is a bug in `flask-migrate` which 
effects one of my five systems even with Docker! This bug just appeared
in the final test run (this evening) so I cannot provide a solution
yet. 

Here you can find the whole discussion: 
https://github.com/miguelgrinberg/Flask-Migrate/issues/213#issuecomment-404247334
Mid-term problem solution: As long as there is no real bug fix
available and I would verify which builds & versions we use and 
create a whitelist of always working environments.

## API usage

The GraphQL interface requires your authentication. I decided
to use a token authentication for this purpose. In order to 
receive the token run the service and query the API. 
For this task I use the tool `httpie`:

### Local API usage instructions (for development only)

#### Create an user 
```bash
> (nydata) flask adduser <username> <password> <email>
[+] User with username=somename... and email=...@nydata.com was created!
```


#### Create an authentication token
```bash
> http POST http://localhost:5000/auth/get_token/ username=<username> password=<password>
```

Sample response
```
HTTP/1.0 200 OK
Content-Length: 308
Content-Type: application/json
Date: Mon, 09 Dec 2019 19:45:17 GMT
Server: Werkzeug/0.16.0 Python/3.7.4

{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NzU5MjA3MTcsIm5iZiI6MTU3NTkyMDcxNywianRpIjoiODU1YzZmMDctOGY1Yy00ZjA3LWJmNTYtYWU2ODhlMDlmY2E5IiwiZXhwIjoxNTc1OTIxNjE3LCJpZGVudGl0eSI6InRpZ2VyZW50ZTEiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.HFXKnAtXz_Vn32N270MrNurGI57HRi9ut82sxPvkeuY"
}

```
You can use the `access_token` value in your further requests.
The default lifetime of a token is 15 minutes.


#### Use the auth token in GraphQL requests
Sample request format:

```http GET '<url>'  'Authorization: Token <your token>'```

Let's use this. Do not forget to put tick marks `'` around the 
url and the token.:

```bash
> http GET 'http://localhost:5000/graphql/?query=query{logs(dateFrom:"2000-01-01",dateTo:"2019-12-12"){hostIP}}' 'Authorization: Token <your token e.g. eyJ0eXAiOi...>'
```

Sample response
```
HTTP/1.0 200 OK
Content-Length: 327
Content-Type: application/json
Date: Mon, 09 Dec 2019 19:49:29 GMT
Server: Werkzeug/0.16.0 Python/3.7.4

{
    "data": {
        "logs": [
            {
                "hostIP": "77.179.66.156"
            },
            {
                "hostIP": "77.179.66.156"
            },
            ...
```


Another sample request for 

- `hostIP` 
- `timestamp` 
- `userAgent` and 
- `verb`

Request:

```bash
> http GET 'http://localhost:5000/graphql/?query=query{logs(dateFrom:"2000-01-01",dateTo:"2019-12-12"){hostIP timestamp userAgent verb}}' 'Authorization: Token <your token e.g. eyJ0eXAiOi...>'
```

Sample response:
```
HTTP/1.0 200 OK
Content-Length: 2289
Content-Type: application/json
Date: Mon, 09 Dec 2019 20:15:43 GMT
Server: Werkzeug/0.16.0 Python/3.7.4

{
    "data": {
        "logs": [
            ...
            {
                "hostIP": "77.179.66.156",
                "timestamp": 1481103803.0,
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
                "verb": "GET"
            },
            {
                "hostIP": "127.0.0.1",
                "timestamp": 1481105077.0,
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
                "verb": "GET"
            },
            ...
```



## Docker Quickstart

This app can be run completely using `Docker` and `docker-compose`. **Using Docker is recommended, as it guarantees the application is run using compatible versions of Python and Node**.

There are three main services:

To run the development version of the app

```bash
docker-compose up flask-prod
```

The production version requires a correct configuration
of the `NGINX_ACCESS_LOG_PATH` in the `.env` file. 
**Note: You also need to share the directory with your
docker instance. For this you need to configure the 
`docker-compose` file and add in the subsection of `x-default-volumes` 
`volumes`.**

For your convenience I already added the nginx log folder:
```
x-default-volumes: &default_volumes
  volumes:
    - ./:/app
    - node-modules:/app/node_modules
    - ./dev.db:/tmp/dev.db
    - /var/log/nginx:/var/log/nginx
```

```bash
docker-compose up flask-prod
```

The list of `environment:` variables in the `docker-compose.yml` file takes precedence over any variables specified in `.env`.

To run any commands using the `Flask CLI`

```bash
docker-compose run --rm manage <<COMMAND>>
```

Therefore, to initialize a database you would run

```bash
docker-compose run --rm manage db init
docker-compose run --rm manage db migrate
docker-compose run --rm manage db upgrade
```

A docker volume `node-modules` is created to store NPM packages and is reused across the dev and prod versions of the application. For the purposes of DB testing with `sqlite`, the file `dev.db` is mounted to all containers. This volume mount should be removed from `docker-compose.yml` if a production DB server is used.

### Running locally

Run the following commands to bootstrap your environment if you are unable to run the application using Docker

**Note:** If you cannot install the application locally you might 
need to install `python3.7-dev`. Moreover, I recommend to create
a `virtualenv` for your local development process.

#### Creating a virtualenv and mounting it
```bash
mkdir ~/envs/
virtualenv ~/envs/nydata/ --python=python3.7
source ~/envs/nydata/bin/activate
(nydata) cd nydata
(nydata) pip install -r requirements/dev.txt
npm install
npm start  # run the webpack dev server and flask server using concurrently
```


#### Database Initialization (locally)

Once you have installed your DBMS, run the following to create your app's
database tables and perform the initial migration

```bash
flask db init
flask db migrate
flask db upgrade
```

## Deployment

When using Docker, reasonable production defaults are set in `docker-compose.yml`

```text
FLASK_ENV=production
FLASK_DEBUG=0
```

Therefore, starting the app in "production" mode is as simple as

```bash
docker-compose up flask-prod
```

By default, you will have access to the flask `app`.
This will generate a new migration script. Then run

```bash
docker-compose run --rm manage db upgrade
flask db upgrade # If running locally without Docker
```


