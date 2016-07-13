#!/usr/bin/python

from optparse import OptionParser
import sys
from ConfigParser import ConfigParser
from datetime import datetime
from subprocess import call
from os.path import isfile
from os import getpid, remove

def _get_config(file):
    if not isfile(file):
        raise Exception('config file not found')

    parser = ConfigParser()
    parser.read(file)
    return parser


CONFIG = _get_config("rutgers-pymirror.cfg")


def main(options, args):
    distros = list(CONFIG.sections())
    distros.remove('settings')

    if options.list:
        for distro in distros:
            print distro
    elif options.all:
        for distro in distros:
            sync(distro)
    elif len(distros) == 0:
        print "no distros to sync"
    else:
        for distro in args:
            sync(distro)


def lock(file):
    if isfile(file):
        return False
    else:
        with open(file, "w") as fh:
            h.write(str(getpid()))
        return True


def unlock(file):
    if isfile(file):
        remove(file)


def sync(distro): 
    datetime_format = CONFIG.get('settings', 'datetimeformat')
    syncurl = CONFIG.get(distro, 'url')
    synchome = CONFIG.get(distro, 'synchome')
    synclog = CONFIG.get(distro, 'synclog')
    synclock = CONFIG.get(distro, 'synclock')

    if not lock(synclock):
        print "Could not begin {0} sync: lock file exists. Skipping...".format(
            distro)
        return

    print "Starting {0} sync at {1}".format(distro, 
        datetime.now().strftime(datetime_format))
            
    with open(synclog, 'a+') as distro_log:
        distro_log.write("rsync started on {0}".format(
            datetime.now().strftime(datetime_format)))
        
        ret = call( ['rsync', '--recursive', '--safe-links', '--times', 
                     '--links', '--hard-links', '--delete', 
                     '--delete-excluded', '--delete-after', 
                     '--delay-updates', '--safe-links', '-v', 
                     syncurl, synchome], 
                   stdout=distro_log)
            
        if ret == 0:
            print "{0} sync successfully completed at {1}".format(distro, 
                datetime.now().strftime(datetime_format))
            distro_log.write("rsync successfully completed at {0}".format(
                datetime.now().strftime(datetime_format)))
        else:
            print "{0} sync failed at {1} with returncode {2}".format(
                distro, datetime.now().strftime(datetime_format), ret)
            distro_log.write(
                "rsync unsuccessfully ended at {0} with return code {1}".format(
                    datetime.now().strftime(datetime_format), ret))
        
        # Create some spacing between syncs
        distro_log.write("\n\n")

    unlock(synclock)


if __name__ == "__main__":
    parser = OptionParser(usage="Usage: %prog [options] distro1 distro2 ...")
    parser.add_option("-l", "--list", action="store_true", default=False,
                      help="list all possible values for 'distro'")
    parser.add_option("-a", "--all", action="store_true", default=False,
                      help="sync all distros")
    parser.add_option("-v", "--verbose", action="store_true", default=False,
                      help="display all output")
    
    (options, args) = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
    else:
        main(options, args)
