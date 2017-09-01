
# Quick start

This is a reference page to quick start your knowledge of the HTTP API project; by reading this page you may get a first insight on how this project works.


## Feedback on the first Release Candidate

To gather into one place the feedback of any user testing a deployed HTTP API server or the online prototype, we created a dedicated free chat room on gitter:

https://gitter.im/EUDAT-B2STAGE/http-api

Please feel free to report or comment to help us improve!


## Using the prototype online

If you don't want to deploy or develop the current project state, you may test online our [prototype](https://b2stage.cineca.it/api/status). If that is the case see the [dedicated instructions](prototype.md).


## Deployment pre-requisites

In order to deploy this project you need to install the `RAPyDO controller` and use it to startup the services on a `Docker` environment with containers.

The following instruction are based on the hyphotesis that you will work on a `UNIX`-based OS. Any `Linux` distributions (Ubuntu, CentOS, Fedora, etc.) or any version of `Mac OSX` will do. Command line examples were heavily tested on `bash` terminal (version `4.4.0`, but also version `3.x` should work).

Please note that for installing tools into your machine the suggested option is through your preferred OS package manager (e.g. `apt`, `yum`, `brew`, etc.).

## Ports

The only port that is need to be accessible from the outside world is 443 where the HTTP-API will be served.

For the letsencrypt-service (used for creating a signeg certificate and thus avoiding security exceptions for the users accessing the API), ports 80 and 443 are needed. **(right?)**

For debugging, other ports may be useful, such as 81 for the adminer interface, to track down database config problems, etc.

**(any other ports? incoming, outgoing)?**


### Base tools

- The `git` client. 
 
Most of UNIX distributions have it already installed. If that is not that case then refer to the [official documentation]()

- The `python 3.4+` interpreter installed together with its main package manager `pip3`.

Most of distributions comes bundled with `python 2.7+`, which is not suitable for our project. Once again use a package manager, for example in ubuntu you would run:

```bash
$ apt-get update && apt-get install python3-pip
```


### Containers environment

#### docker engine

To install docker on a unix terminal you may use the [get docker script](https://get.docker.com):

```
# Install docker
$ curl -fsSL get.docker.com -o get-docker.sh
$ sh get-docker.sh
```

For Mac and Windows users dedicated applications were written: 

- [Docker for Mac](https://www.docker.com/docker-mac)  
- [Docker for Windows](https://www.docker.com/docker-windows)

As alternative, the best way to get Docker ALL tools working
is by using their [toolbox](https://www.docker.com/toolbox).

#### docker compose

`Compose` is a tool for docker written in Python. See the [official instructions](https://docs.docker.com/compose/install/) to install it.

NOTE: compose comes bundled with the toolbox.

## Two modes

There are two main modes to work with the API server. The main one - called `debug` - is for developers: you are expected to test, debug and develop new code. The other options is mode `production`, suited for deploying your server in a real use case scenario on top of your already running `B2SAFE` instance. The main difference between these modes is that the production mode requires a B2SAFE instance, while the debug mode installs its own
iRODS instance in a container. **(TODO: Is this correct?)**


## Start-up the project

Here's a step-by-step tutorial to work with the HTTP API project.


### 1. cloning 

For doing these steps, you do not need sudo rights. You can run them as your normal linux user,
for example in your normal linux user's home directory.

To clone the working code, run:

```bash
$ VERSION=0.6.0 \
    && git clone https://github.com/EUDAT-B2STAGE/http-api.git \
    && cd http-api \
    && git checkout $VERSION  

# now you will have the current latest release (RC1)
```


### 2. configure

Now that you have all necessary software installed, before launching services you should consider editing the main configuration:

[`projects/eudat/project_configuration.yaml`](projects/eudat/project_configuration.yaml)

Here you can change at least the basic passwords, or configure access to external service (e.g. your own instance of iRODS/B2SAFE) for production.

Some hints:

**Dockerized DB:** http-api installs its own postgresql database for internal use, in an extra container. In debug mode, that postgresql installation is also used for storing the ICAT (the database needed by the iRODS instance). As postgresql will be installed freshly and the database created freshly, you can choose username and password freely. The username "rods" is recommended because **(TODO: Add a reason)**. **(TODO: Is all this correct?)**

| Keyword          | Value         | Comment                                          |
| -----------------|---------------| -------------------------------------------------|
| ALCHEMY_USER     | rods          | Leave "rods" because **(TODO: Add a reason)**    |
| ALCHEMY_PASSWORD | please choose | Choose a password for the database to be created |
| ALCHEMY_API_DB   | SQL_API       | Leave "SQL_API" because **(TODO: Add a reason)** |

**B2ACCESS:** Not currently used. No need to configure anything there.

| Keyword          | Value            | Comment                                           |
| -----------------|------------------| --------------------------------------------------|
| B2ACCESS_ACCOUNT | **(TODO: what)** | Which value to put and why and where get it from? |
| B2ACCESS_SECRET  | **(TODO: what)** | Where to get it from? Needed for?                 |

**LOCAL iRODS server VERSION:** This is only used in DEBUG mode. Please leave all the defaults. **(TODO: Correct?)**

**PRODUCTION iRODS server VERSION:** This is used in production mode, i.e. if you want to connect your http-api instance to an existing iRODS instance, either on the same machine or on another machine.

| Keyword                  | Value            | Comment                                                                      |
| -------------------------|------------------| -----------------------------------------------------------------------------|
| IRODS_HOST               | host name        | IP **(TODO: IP ok??)** or fully qualified domain name of your iRODS server.  |
| IRODS_USER               | alice            | The iRODS username to be used to connect to iRODS. **(TODO: Why? Shouldn't any user be able to connect? I don't understand this.)** |
| IRODS_GUEST_USER         | **(TODO: what)** | **(TODO: What is this? Needed for what?)**                                   |
| IRODS_DEFAULT_ADMIN_USER | **(TODO: what)** | **(TODO: What is this? Needed for what?)**                                   |
| IRODS_ZONE               | **(TODO: what)** | The name of your iRODS zone.                                                 |
| IRODS_HOME               | home             | The home directory for your data. In standard installations, this is "home". |
| IRODS_DN                 | **(TODO: what)** | The DN from your server certificate. You can find this by executing FOOBAR. This is used by B2ACCESS, so as long as B2ACCESS is not used, it does not matter. |
| IRODS_PASSWORD           | **(TODO: what)** | **(TODO: The password of which irods user?)**                                |
| IRODS_AUTHSCHEME         | credentials      | **(TODO: What is this? Needed for what? Which choices exist?)**              | 

Note: The value "IRODS_DN" 

**PID credentials:** The http-api creates/modifies the Handles (persistent identifiers) of data collections. To do so, it is
necessary to provide credentials for the Handle service.

| Keyword                          | Value             | Comment                                                       |
| ---------------------------------|-------------------| --------------------------------------------------------------|
| HANDLE_CREDENTIALS_INTERNAL_PATH | **(TODO: what)**  | **(TODO: Which value to put and why and where get it from?)** |
| HANDLE_BASE                      | **(TODO: what)**  | **(TODO: Where to get it from? Needed for?)**                 |
| HANDLE_USER                      | **(TODO: what)**  | **(TODO: Where to get it from? Needed for?)**                 |
| HANDLE_PREFIX                    | **(TODO: what)**  | **(TODO: Where to get it from? Needed for?)**                 |
| HANDLE_PASS                      | **(TODO: what)**  | **(TODO: Where to get it from? Needed for?)**                 |

** TODO Question: Why is write access to a handle server needed? Is this only needed in debug mode, when there is an iRODS instance installed? Or also in production mode? What for? **

### 3. controller

The controller is what let you manage the project without much effort.

**TODO:** It would be cool to know a little more about it! E.g. what it is based on, whether it runs in a container, ... for example:
rapydo is a python tool that is used to... All the user's interaction with the http-api installation
uses rapydo. The commands to initialize, build, start or stop the http-api are passed to the rapydo tool. It runs
outside the docker containers and takes care of starting and stopping the docker containers the http-api consists of.
For more information, please check [rapydo's page] on pypi(https://pypi.python.org/pypi/rapydo-controller).

Here's what you need to use it:

```bash
# install and use the rapydo controller
$ data/scripts/prerequisites.sh 
# you have now the executable 'rapydo'
$ rapydo --version
# If you use a shell different from bash (e.g. zsh) 
# you can try also the short alias 'do'
$ do --help
```

NOTE: python install binaries in `/usr/local/bin`. If you are not the admin/`root` user then the virtual environment is created and you may find the binary in `$HOME/.local/bin`. Make sure that the right one of these paths is in your `$PATH` variable, otherwise you end up with `command not found`.


### 4. deploy initialization

Your current project needs to be initialized. This step is needed only the first time you use the cloned repository.

** TODO: Please explain what to do if you messed up your init, e.g. by providing wrong config. Can you just rerun init? **

```bash
$ rapydo init
```

NOTE: with `RC1` there is no working `upgrade` process in place to make life easier if you already have this project cloned from a previous release. This is something important already in progress [here](https://github.com/EUDAT-B2STAGE/http-api/issues/87). **(TODO: --> So, what to do now, until this is fixed?)**

### 5. Launch the project

As mentioned above, there are two main modes to work with the API server. The commands to start the http-api are
different for these modes. Please follow one of the sections below, depending on your desired mode.

#### debug mode

NOTE: follow this paragraph only if you plan to develop new features on the HTTP API.

```bash
################
# bring up the docker containers in `debug` mode
$ rapydo start
# NOTE: this above is equivalent to default value `do --mode debug start`

# laungh the restful http-api server 
$ rapydo shell backend --command 'restapi launch'
# or
$ rapydo shell backend 
[container shell]$ restapi launch
```

NOTE: the block of commands above can be used at once with:

```bash
$ rapydo start --mode development
# drawback: when the server fails at reloading, it crashes
```


And now you may access a client for the API, from another shell and test the server:

```bash
$ rapydo shell restclient
```

The client shell will give you further instructions on how to test the server. In case you want to log with the only existing admin user:

- username: user@nomail.org
- password: test

NOTE: on the client image you have multiple tools installed for testing:
- curl
- httpie
- http-prompt


#### production mode

Some important points before going further:

1. Please follow this paragraph only if you plan to deploy the HTTP API server in production (this is misleading! Our testbed for example is not production) on top of an existing B2SAFE instance.
2. Usually in production you have a domain name associated to your host IP (e.g. `b2stage.cineca.it` to 240.bla.bla.bla). But you can just use 'localhost' if this is not the case.
3. You need a `B2ACCESS` account on the development server for the HTTP API application. Set the credentials [here](https://github.com/EUDAT-B2STAGE/http-api/blob/0.6.0/projects/eudat/project_configuration.yaml#L22-L26) otherwise the endpoint `/auth/askauth` would not work.  

Deploying is very simple:

```bash
# define your domain, i.e. the fully qualified domain name of the machine that runs the http-api
# (find it with the command "hostname")
$ DOMAIN='b2stage.cineca.it'
# launch production mode
$ rapydo --host $DOMAIN --mode production start
```

Now may access your IP or your domain and the HTTP API endpoints are online, protected by a proxy server. You can test this with:

```bash
open $DOMAIN/api/status # or:
wget $DOMAIN/api/status | cat # (if "open" results in "Couldn't get a file descriptor referring to the console")
```

### Certificates

Up to now the current SSL certificate is self signed and is 'not secure' for all applications. Your browser is probably complaining for this. This is why we need to produce one with the free `letsencrypt` service.

```bash
$ rapydo --host $DOMAIN --mode production ssl-certificate
#NOTE: this will work only if you have a real domain associated to your IP
```

If you check again the server should now be correctly certificated. At this point the service should be completely functional.

Instead, you can use other certificates, e.g. if your institution provides signed certificates. In that case, need the certificate (*.pem) and the private key (*.pem or *.key).
To install them, do the following: **(TODO: Please check whole section)**

1. Log into the docker container "eudat_proxy_1":

```bash
docker exec -it eudat_proxy_1 bash

# Prompt has changed, also username and hostname:
whoami # root, was your username on the host machine before
hostname # reverseproxy, was the host machine's hostname before
```

2. Make copies of the existing certificates:

```bash
cp /etc/letsencrypt/real/fullchain1.pem /etc/letsencrypt/real/fullchain1.pem_backup
cp /etc/letsencrypt/real/privkey1.pem   /etc/letsencrypt/real/privkey1.pem_backup
```

3. Exit from the docker shell:

```bash
exit
whoami # your username on the host machine
hostname # your host machine's hostname
```

4. Copy the certificates to the right location inside the docker container and make sure they have the correct names:

```bash
docker cp /path/to/certificate.pem eudat_proxy_1:/etc/letsencrypt/real/fullchain1.pem
docker cp /path/to/privatekey.pem  eudat_proxy_1:/etc/letsencrypt/real/privkey1.pem
```

5. Restart the docker container **(necessary?)**

```bash
docker restart eudat_proxy_1
```



## Other operations

Here we have more informations for further debugging/developing the project


### launch interfaces

To explore data and query parameters there are few other services as options:

```bash
SERVER=localhost  # or your IP / Domain
PORT=8080

# access a swagger web ui
rapydo interfaces swagger
# access the webpage:
open http://$SERVER/swagger-ui/?url=http://$SERVER:$PORT/api/specs

# SQL admin web ui
rapydo interfaces sqlalchemy
# access the webpage:
open http://$SERVER:81/adminer
```

### add valid b2handle credentials

To resolve non-public `PID`s prefixes for the `EPIC HANDLE` project we may leverage the `B2HANDLE` library providing existing credentials. 

You can do so by copying such files into the dedicated directory:

```bash
cp PATH/TO/YOUR/CREDENTIALS/FILES/* data/b2handle/
```

### destroy all

If you need to clean everything you have stored in docker from this project:

```bash
# BE CAREFUL
rapydo clean --rm-volumes  # very DANGEROUS, you lose all data!
# BE CAREFUL
```

### hack the certificates volume

This hack is necessary if you want to raw copy a CA certificate if your VM DN was produced with an internal certification authority.

```bash
path=`docker inspect $(docker volume ls -q | grep sharedcerts) | jq -r ".[0].Mountpoint"`
sudo cp /PATH/TO/YOUR/CA/FILES/CA-CODE.* $path/simple_ca

```
