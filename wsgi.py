import sys
from os import path as op

from biolink.app import main


APPROOT = op.abspath(op.join(op.dirname(__file__), 'base'))
if not APPROOT in sys.path:
    sys.path.insert(0, APPROOT)

main()

