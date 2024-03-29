Infrastructure
==============

```mermaid
---
title: Reference Architecture
---

flowchart LR
    subgraph caddy ["Caddy"]
        reverse_proxy("Reverse Proxy\n@ api.xsnippet.org")
        webserver("Webserver\n@ xsnippet.org")
    end

    letsencrypt[/"Let's Encrypt"/]
    caddy -->|"renew TLS certificates"| letsencrypt

    user(("User"))
    user -->|"HTTPS"| reverse_proxy
    user -->|"HTTPS"| webserver

    reverse_proxy -->|"proxy to"| xsnippet_api[["localhost:8080\n@ /opt/xsnippet-api/xsnippet-api"]]
    webserver -->|"serve at"| xsnippet_web[["HTML/JS/CSS\n@ /opt/xsnippet-web/"]]

    postgres[("PostgreSQL")]
    xsnippet_api --> postgres
```

The project provides the [Ansible] playbook to deploy [XSnippet] service on a
single node. This includes but not limited to provisioning the following
components:

* [XSnippet API]
* [XSnippet Web]
* [PostgreSQL]
* [Caddy]

Some key points about the components can be found below:

* PostgreSQL stores its data on an external volume (if attached).

* XSnippet API is managed by a system level systemd service that drops
  privileges to `xsnippet-api` user on start. It communicates with PostgreSQL
  via unix sockets in order avoid managing passwords.

* Caddy server has been chosen to simplify TLS certs management, since it
  integrates with LetsEncrypt and requests and renews TLS certs automatically
  as the need arise.


Usage
=====

It's as easy as running the following command:

```shell
$ ansible-playbook -i inventories/production site.yml
```

Please note, in order to provision a new node from scratch, the playbook is
expected to be executed from a passwordless sudo user. If such user does not
exist, please create one for ansible usage.

[Ansible]: https://www.ansible.com/
[XSnippet]: https://xsnippet.org/
[XSnippet API]: https://github.com/xsnippet/xsnippet-api
[XSnippet Web]: https://github.com/xsnippet/xsnippet-web
[PostgreSQL]: https://www.postgresql.org/
[Caddy]: https://caddyserver.com/
