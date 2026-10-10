Build and run the XSnippet image
===============================

Run from the repository root with mkosi 25.3 or newer, systemd-repart,
systemd-nspawn, QEMU, cpio, mtools, apt and the Debian archive keyring installed on the build
host (or supply a mkosi tools tree). Package and release downloads
require network access. The default image is Debian 13 (trixie), with a writable
root filesystem, an EFI system partition, systemd-boot and a kernel selected
for the host architecture (x86-64 or ARM64).

Validation in this workspace: mkosi 25.3 completed a production x86-64 image
build, including Caddy validation and EFI/root partition creation. Shell
syntax, embedded Python and template checks passed; the local ARM64
configuration parsed successfully. Image boot and service smoke tests remain
unverified.

This workspace's filesystem rejected writes by the privileged build process.
The successful build used `--output-directory=/var/tmp/xsnippet-image`, then
copied the artifacts into `mkosi.output/` as the workspace user. Missing host
`cpio` and `mcopy` binaries were supplied temporarily with
`--extra-search-path=/tmp/xsnippet-build-tools/usr/bin`. Install their packages
on the build host for normal builds.

Optionally generate a GoAccess password hash with `caddy hash-password` and
pass it to the build. Without a hash, the report is public, matching Ansible's
optional authentication. Production domains match the production inventory:

```sh
export GOACCESS_PASSWORD_HASH='paste the Caddy hash here'
sudo --preserve-env=GOACCESS_PASSWORD_HASH mkosi build
sudo mkosi boot
mkosi vm
```

The output is `mkosi.output/xsnippet.raw`. Run either container or VM at a time
against that writable image. To boot it directly with nspawn:

```sh
sudo systemd-nspawn --boot --image=mkosi.output/xsnippet.raw \
    --network-veth --capability=CAP_NET_ADMIN
```

Use host systemd-networkd's container/VM network configuration (or configure a
bridge/NAT yourself) to provide DHCP and routing. The guest accepts DHCP on
Ethernet interfaces and uses systemd-resolved. `RuntimeNetwork=interface`
provides an isolated veth/tap interface, allowing nftables without changing the
host's firewall. QEMU needs working UEFI firmware; ARM64 normally needs an
ARM64 host or separately configured emulation. Current mkosi versions may
require newer host systemd services for unprivileged disk-image boot; direct
root nspawn works independently of that integration.

For local testing, build with `mkosi --profile=local build`, then use the same
profile when booting. Map `xsnippet.local`, `api.xsnippet.local`,
`raw.xsnippet.local` and `rt.xsnippet.local` to the guest's address on the host.
Caddy uses its internal CA in this profile. Smoke-test with:

```sh
curl --fail --insecure https://api.xsnippet.local/v1/snippets
curl --fail --insecure https://xsnippet.local/
```

Production domains need DNS pointing at the guest and reachable ports 80/443
for automatic public certificates. When a hash is configured, GoAccess requires the username
(`xsnippet` by default) and password, including for its WebSocket endpoint.
The root account remains locked. Use `machinectl shell` as root for container
administration, or configure credentials locally for VM console access.

Customization and persistence
=============================

Put private build overrides in `mkosi.local.conf`, for example:

```ini
[Build]
Environment=API_RELEASE=nightly WEB_RELEASE=nightly
            API_HOST=api.example.org RAW_HOST=raw.example.org
            WEB_HOST=example.org GOACCESS_HOST=rt.example.org
            CADDY_EMAIL=admin@example.org
```

Pin API and web tags for repeatable application versions. API binary and
migration sources use the same API tag; the moving nightly default follows
the playbook and is not reproducible. Release assets are fetched over HTTPS,
without independent checksum verification, as in the existing roles.

Data, backups, Caddy certificates and GoAccess state live in the writable
image. Rebuilding replaces this state: preserve it outside the image for
deployment. For nspawn, bind host directories into `/var/lib/postgresql`,
`/var/lib/postgresql-backups`, `/var/lib/caddy` and `/var/lib/goaccess`. Match
guest ownership and use `--private-users=no` if managing numeric ownership
directly. For QEMU, attach a formatted data disk and supply an `/etc/fstab`
overlay through `ExtraTrees=` to mount it and bind the data directories.
The database units order themselves after the PostgreSQL and backup mounts.
External disks are deliberately not autoformatted by the image.

To restore, place a PostgreSQL custom-format dump at
`/var/lib/postgresql-backups/restore.pgc`, readable by guest `postgres`, before
booting. Restoration runs only when there are no tables owned by
`xsnippet-api`, then API migrations run. Nightly backups run at 03:00 UTC,
retain 30 dumps per database, and catch up after downtime.

Playbook mapping
================

| Ansible role | Image implementation |
| --- | --- |
| firewall | nftables package, rules overlay and enabled service; DHCP added |
| volume | Writable root by default; optional externally supplied mounts |
| postgres | Debian PostgreSQL 17; fresh cluster on first boot, peer-authenticated application role/database, conditional restore, backup timer |
| caddy | Debian Caddy; four virtual hosts, automatic TLS, CORS and raw routes |
| xsnippet_api | Architecture-specific release, matching migration sources, environment file, systemd service |
| xsnippet_web | Web release and generated domain configuration |
| xsnippet_raw | Caddy rewrite to the API's plain-text endpoint |
| goaccess | Journal/FIFO pipeline, persistent report, HTTPS/WebSocket proxy |

Packages, boot layout, kernel selection, users, directories, networking and
service definitions are declarative. The post-install script only downloads
artifacts, writes profile-dependent settings, prepares empty database state,
and enables services. Database creation/restoration runs at boot instead of
starting PostgreSQL during image construction. Existing Ansible files remain
usable independently.

Differences: Debian's repositories replace the three third-party apt
repositories, so package versions differ. Ansible-only prerequisites are
omitted. The image provisions the inventory's single `xsnippet-api` database;
additional databases require their own initialization and timer definitions.
Booting does not automatically run the Ansible controller's smoke tests.

References: [mkosi configuration and script documentation](https://github.com/systemd/mkosi/blob/v25.3/mkosi/resources/man/mkosi.1.md).
