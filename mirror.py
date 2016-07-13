#!/usr/bin/python

from optparse import OptionParser
import sys
from ConfigParser import ConfigParser
from datetime import datetime
from subprocess import call
from os.path import isfile
from os import getpid, remove
import logging


CONFIG_PATH = "rutgers-pymirror.cfg"
CONFIG = None


def load_config(file):
    if not isfile(file):
        raise Exception('config file not found')

    parser = ConfigParser()
    parser.read(file)
    return parser


def initialize_logger(console_log_level):
    logformat = "[%(asctime)s] %(levelname)s: %(message)s"
    dateformat = CONFIG.get('settings', 'datetimeformat')
    
    # Log everything to the log file
    logging.basicConfig(filename=CONFIG.get('settings', 'mainlog'), 
        datefmt=dateformat, format=logformat, level=logging.DEBUG)

    # Only log warnings and critical errors to the console
    ch = logging.StreamHandler()
    ch.setLevel(console_log_level)
    formatter = logging.Formatter(fmt=logformat, datefmt=dateformat)
    ch.setFormatter(formatter)
    logging.getLogger('').addHandler(ch)


def main(options, args):
    global CONFIG
    CONFIG = load_config(CONFIG_PATH)
    
    # We log everything to the log file, but only certain things to the console
    if options.verbose:
        console_log_level = logging.DEBUG
    else:
        console_log_level = logging.WARNING
    initialize_logger(console_log_level)
     
    distros = list(CONFIG.sections())
    distros.remove('settings')

    if options.list:
        for distro in distros:
            print distro
    elif options.all:
        for distro in distros:
            sync(distro)
    elif len(distros) == 0:
        logging.info("nothing to do")
    else:
        for distro in args:
            sync(distro)


def lock(file):
    if isfile(file):
        return False
    else:
        with open(file, "w") as fh:
            fh.write(str(getpid()))
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
        logging.warning("Could not begin %s sync: lock file exists.", distro)
        logging.warning("Skipping...")
        return

    logging.info("Starting %s sync", distro) 
            
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
            logging.info("%s sync successfully completed", distro)
            distro_log.write("rsync successfully completed at {0}".format(
                datetime.now().strftime(datetime_format)))
        else:
            logging.warning("%s sync failed with returncode %s", distro, ret)
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
