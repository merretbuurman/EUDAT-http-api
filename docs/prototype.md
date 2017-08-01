
# Prototype

Hello EUDAT user!

The first release candidate was created.

Before getting our hands on the first `HTTP-API` server prototype, here's a list of key points to consider:

- You need `B2ACCESS` credentials as an EUDAT user inside the [development instance](https://unity.eudat-aai.fz-juelich.de:8443/home/).
- B2SAFE/irods credentials do not work as HTTP API credentials at the moment.
- The current instance is working on a testbed B2SAFE running at [CINECA](http://hpc.cineca.it/).

The HTTP API prototype endpoints are accessible at the URI bases:

- https://b2stage.cineca.it/api
- https://b2stage.cineca.it/auth

e.g. once you authenticated: https://b2stage.cineca.it/auth/profile

## Status

The status page for the current prototype is:
https://b2stage.cineca.it/api/status

This is an endpoint to call if you want to automatically verify if the server is responding to request. This endpoint is also automatically monitored from the [uptime robot service](https://stats.uptimerobot.com/xGG9gTK3q).


## Swagger specifications

The EUDAT B2STAGE HTTP API provide description of the current specifications following the latest version (`3.0`) of the `openapi` standard from [Swagger](https://swagger.io/specification/). 

The description in `JSON` format is available at:

https://b2stage.cineca.it/api/specs


## Clients

### authentication process

Details on how to create a valid token upon the current release of the HTTP API is available [inside the user guide](user/authentication.md)

### curl

See also the [main user page](user/user.md) to understand which endpoints exists and how to use them from command line/terminal with the `curl` application.

### official swagger-ui website

Since the HTTP API server follows the `openapi` standard, you can query its endpoints also using the official `swagger-ui` web server, by just passing the `JSON` file in input:

http://petstore.swagger.io/?url=https://b2stage.cineca.it/api/specs&docExpansion=none

### python script

This is yet a work in progress: 

> creating a dedicated python package to officially query the EUDAT B2STAGE HTTP-API