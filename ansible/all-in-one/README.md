All-in-one deployment of XSnippet
=================================

Deploys both [xsnippet-api](https://github.com/xsnippet/xsnippet-api) web-service
and [xsnippet-web](https://github.com/xsnippet/xsnippet-web) SPA on *one* host
under different *server names* (i.e. domains).

Docker Swarm [stack](https://docs.docker.com/get-started/part5/) is used to spawn
and manage all the required services:

  1. ``xsnippet-api`` Python-powered web-service.
  2. ``mongodb`` database - main storage for application data.
  3. ``nginx`` webserver - used both as a webserver for serving static content
     of the SPA and as a reverse-proxy for the Python application.

The only reason behind using of Docker Swarm is the support for *stacks*, that
allows to declaratively describe the deployed infrastructure similarly to
docker-compose configurations.

The given playbook is meant to be executed against Debian'ish hosts and was
tested on the latest Ubuntu LTS version (currently, Xenial).


Usage
=====

The very same command is used to perform both initial deployments and upgrades:


```shell

    # ansible-playbook -i path_to_inventory deploy.yaml

```


Important variables
===================

Most likely you'll need to override the defaults of the following variables
defined in the playbook:

    # ``xsnippet_api_server_name``: server name of the API in the config of the webserver
    # ``xsnippet_spa_server_name``: server name of the SPA in the config of the webserver
    # ``xsnippet_api_image``: Docker image of the API to be used
    # ``xsnippet_web_assets``: URL of the SPA tarball release to be used

Note, that Docker images of ``xsnippet-api`` are periodically pushed to
[Docker Hub](https://hub.docker.com/r/xsnippet/xsnippet-api/), and SPA assets are released
on [GitHub](https://github.com/xsnippet/xsnippet-web/releases).
