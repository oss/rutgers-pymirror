#!/usr/bin/python

from optparse import OptionParser
from ConfigParser import ConfigParser
from datetime import datetime
from subprocess import call

def _get_config(file):
    parser = ConfigParser()
    parser.read(file)
    return parser

CONFIG = _get_config("rutgers-pymirror.cfg")

def main(options, args):
    datetime_format = CONFIG.get('settings', 'datetimeformat')
    distros = list(CONFIG.sections())
    distros.remove('settings')
    
    if len(distros) == 0:
        print "no distros to sync"
    else:
        for distro in distros:
            print "Starting {} sync at {}".format(distro, 
                datetime.now().strftime(datetime_format))
            
            with open(CONFIG.get(distro, 'synclog'), 'a+') as distro_log:
                ret = call( ['rsync', '--recursive', '--safe-links', '--times', 
                             '--links', '--hardlinks', '--delete', 
                             '--delete-excluded', '--delete-after', 
                             '--delay-updates', '--safe-links', '-v', 
                             CONFIG.get(distro, 'url'), 
                             CONFIG.get(distro, 'synchome')], 
                           stdout=distro_log)
            
                if ret == 0:
                    print "{} sync successfully completed at {}".format(distro, 
                        datetime.now().strftime(datetime_format))
                else:
                    print "{} sync failed at {} with returncode {}".format(
                        distro, datetime.now.strftime(datetime_format), ret)


if __name__ == "__main__":
    parser = OptionParser(usage="Usage: %prog [options] distro")
    parser.add_option("-l", "--list", action="store_true", default=False,
                      help="list all possible values for 'distro'")
    parser.add_option("-a", "--all", action="store_true", default=False,
                      help="sync all distros")
    parser.add_option("-v", "--verbose", action="store_true", default=False,
                      help="display all output")
    
    (options, args) = parser.parse_args()
   
    # Display usage if no argument given
    if len(args) == 0 and not options.all:
        parser.print_help()
    else:
        main(options, args)
