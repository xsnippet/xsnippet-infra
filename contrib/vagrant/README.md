Vagrant for XSnippet
====================

Vagrant for XSnippet is a regular [Vagrant] script to bootstrap all-in-one VM
with development environment. Despite being *development*, it uses the same
deployment scripts we use to deploy production, so this environment is a good
thing to battle test upcoming changes.

[Vagrant]: https://www.vagrantup.com/


Prerequisites
-------------

* It's assumed Vagrant is installed on your system either via package manager,
  homebrew (if you are on macOS) or directly from [the site].

  [the site]: https://www.vagrantup.com/downloads.html

* The Vagrantfile we provide depends on `vagrant-hostmanager` plugin, so please
  install it beforehand.

  ```bash
  $ vagrant plugin install vagrant-hostmanager
  ```

* If you're going to use [VirtualBox], you need to ensure `vagrant-vbguest`
  is installed before moving forward.

  ```bash
  $ vagrant plugin install vagrant-vbguest
  ```

  [VirtualBox]: https://www.virtualbox.org


Running
-------

Running any Vagrant environment usually as simple as running

```bash
$ vagrant up
```

and we are not exception here. :)
