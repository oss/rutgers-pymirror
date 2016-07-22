# rutgers-pymirror

An easy-to-configure rsync mirroring script, written in Python.

## Setup

By default, rutgers-pymirror looks for your config file at 
`/etc/rutgers-pymirror.cfg` -- if using another path, change `CONFIG_PATH` in 
`rutgers-pymirror` accordingly.

## Usage

```
Usage: rutgers-pymirror [options] distro1 distro2 ...

Options:
  -h, --help       show this help message and exit
  --action=ACTION  action to take: sync, list, or check. sync (default): sync
                   the distro with rsync. list: display a list of all repos
                   defined in the config file. check: display a list of all
                   repos out of date
  --hours=HOURS    the number of hours (default: 24) since the last sync to be
                   considered out of date; only used with --action=check
  -a, --all        perform action on all distros
  -v, --verbose    display all output

```
