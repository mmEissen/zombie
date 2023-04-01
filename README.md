
On M1 platform:

if `psycopg2.OperationalError: SCRAM authentication requires libpq version 10 or above`

Run:
```
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```
https://stackoverflow.com/questions/62807717/how-can-i-solve-postgresql-scram-authentication-problem
