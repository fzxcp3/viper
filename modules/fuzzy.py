import os
import getopt

from viper.common.out import *
from viper.common.abstracts import Module
from viper.core.database import Database
from viper.core.session import __session__

try:
    import pydeep
    HAVE_PYDEEP = True
except ImportError:
    HAVE_PYDEEP = False

class Fuzzy(Module):
    cmd = 'fuzzy'
    description = 'Search for similar files through fuzzy hashing'

    def run(self):
        if not __session__.is_set():
            print_error("No session opened")
            return

        if not HAVE_PYDEEP:
            print_error("Missing dependency, install pydeep (`pip install pydeep`)")
            return

        if not __session__.file.ssdeep:
            print_error("No ssdeep hash available for opened file")
            return

        def usage():
            print("usage: fuzzy [-v]")

        def help():
            usage()
            print("")
            print("Options:")
            print("\t--help (-h)\tShow this help message")
            print("\t--verbose (-v)\tPrints verbose logging")
            print("")

        verbose = False

        try:
            opts, argv = getopt.getopt(self.args[0:], 'v', ['verbose'])
        except getopt.GetoptError as e:
            print(e)
            return

        for opt, value in opts:
            if opt in ('-h', '--help'):
                help()
                return
            elif opt in ('-v', '--verbose'):
                verbose = True

        db = Database()
        samples = db.find(key='all')

        for sample in samples:
            if sample.sha256 == __session__.file.sha256:
                continue

            if not sample.ssdeep:
                continue

            score = pydeep.compare(__session__.file.ssdeep, sample.ssdeep)
            if score > 40 or verbose:
                print("Match {0}%: {1}".format(score, sample.sha256))
