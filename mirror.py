#!/usr/bin/python

from optparse import OptionParser
import sys
from ConfigParser import ConfigParser
from datetime import datetime
from subprocess import call
from os.path import isfile

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
   

def sync(distro): 
    datetime_format = CONFIG.get('settings', 'datetimeformat')
    syncurl = CONFIG.get(distro, 'url')
    synchome = CONFIG.get(distro, 'synchome')
    synclog = CONFIG.get(distro, 'synclog')

    print "Starting {0} sync at {1}".format(distro, 
        datetime.now().strftime(datetime_format))
            
    with open(synclog, 'a+') as distro_log:
        ret = call( ['rsync', '--recursive', '--safe-links', '--times', 
                     '--links', '--hardlinks', '--delete', 
                     '--delete-excluded', '--delete-after', 
                     '--delay-updates', '--safe-links', '-v', 
                     syncurl, synchome], 
                   stdout=distro_log)
            
        if ret == 0:
            print "{0} sync successfully completed at {1}".format(distro, 
                datetime.now().strftime(datetime_format))
        else:
            print "{0} sync failed at {1} with returncode {2}".format(
                distro, datetime.now.strftime(datetime_format), ret)


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
