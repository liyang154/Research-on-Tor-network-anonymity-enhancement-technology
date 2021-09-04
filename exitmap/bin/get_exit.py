import sys
import os
import time
import socket
import pkgutil
import argparse
import datetime
import random
import logging
from configparser import ConfigParser
import functools
import pwd

import stem
import stem.connection
import stem.process
import stem.descriptor
from stem.control import Controller, EventType

import modules
import error
import util
import relayselector

def parse_cmd_args():
    """
    Parse and return command line arguments.
    """

    desc = "Perform a task over (a subset of) all Tor exit relays."
    parser = argparse.ArgumentParser(description=desc, add_help=False)

    parser.add_argument("-f", "--config-file", type=str, default=None,
                        help="Path to the configuration file.")

    args, remaining_argv = parser.parse_known_args()

    # First, try to load the configuration file and load its content as our
    # defaults.

    if args.config_file:
        config_file = args.config_file
    else:
        home_dir = os.path.expanduser("~")
        config_file = os.path.join(home_dir, ".exitmaprc")

    config_parser = ConfigParser()
    file_parsed = config_parser.read([config_file])
    if file_parsed:
        try:
            defaults = dict(config_parser.items("Defaults"))
        except ConfigParser.NoSectionError as err:
            log.warning("Could not parse config file \"%s\": %s" %
                        (config_file, err))
            defaults = {}
    else:
        defaults = {}

    parser = argparse.ArgumentParser(parents=[parser])
    parser.set_defaults(**defaults)

    # Now, load the arguments given over the command line.

    group = parser.add_mutually_exclusive_group()

    group.add_argument("-C", "--country", type=str, default=None,
                       help="Only probe exit relays of the country which is "
                            "determined by the given 2-letter country code.")

    group.add_argument("-e", "--exit", type=str, default=None,
                       help="Only probe the exit relay which has the given "
                            "20-byte fingerprint.")

    group.add_argument("-E", "--exit-file", type=str, default=None,
                       help="File containing the 20-byte fingerprints "
                            "of exit relays to probe, one per line.")

    parser.add_argument("-d", "--build-delay", type=float, default=3,
                        help="Wait for the given delay (in seconds) between "
                             "circuit builds.  The default is 3.")

    parser.add_argument("-n", "--delay-noise", type=float, default=0,
                        help="Sample random value in [0, DELAY_NOISE) and "
                             "randomly add it to or subtract it from the build"
                             " delay.  This randomises the build delay.  The "
                             "default is 0.")

    # Create /tmp/exitmap_tor_datadir-$USER to allow many users to run
    # exitmap in parallel.

    tor_directory = "/tmp/exitmap_tor_datadir-" + pwd.getpwuid(os.getuid())[0]

    parser.add_argument("-t", "--tor-dir", type=str,
                        default=tor_directory,
                        help="Tor's data directory.  If set, the network "
                             "consensus can be re-used in between scans which "
                             "speeds up bootstrapping.  The default is %s." %
                             tor_directory)

    parser.add_argument("-a", "--analysis-dir", type=str,
                        default=None,
                        help="The directory where analysis results are "
                             "written to.  If the directory is used depends "
                             "on the module.  The default is /tmp.")

    parser.add_argument("-v", "--verbosity", type=str, default="info",
                        help="Minimum verbosity level for logging.  Available "
                             "in ascending order: debug, info, warning, "
                             "error, critical).  The default is info.")

    parser.add_argument("-i", "--first-hop", type=str, default=None,
                        help="The 20-byte fingerprint of the Tor relay which "
                             "is used as first hop.  This relay should be "
                             "under your control.")

    parser.add_argument("-o", "--logfile", type=str, default=None,
                        help="Filename to which log output should be written "
                             "to.")

    exits = parser.add_mutually_exclusive_group()

    exits.add_argument("-b", "--bad-exits", action="store_true",
                       help="Only scan exit relays that have the BadExit "
                            "flag.  By default, only good exits are scanned.")

    exits.add_argument("-l", "--all-exits", action="store_true",
                       help="Scan all exits, including those that have the "
                            "BadExit flag.  By default, only good exits are "
                            "scanned.")

    parser.add_argument("-V", "--version", action="version",
                        version="%(prog)s 2020.11.23")

    parser.add_argument("module", nargs='+',
                        help="Run the given module (available: %s)." %
                        ", ".join(get_modules()))

    parser.set_defaults(**defaults)

    return parser.parse_args(remaining_argv)

stats = Statistics()
args = parse_cmd_args()
cached_consensus_path = os.path.join(args.tor_dir, "cached-consensus")
fingerprints = relayselector.get_fingerprints(cached_consensus_path)
count = len(exit_relays)
print(count)