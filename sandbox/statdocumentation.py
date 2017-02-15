#! /usr/bin/env python

import re
import sys

sys.path.insert(0, "../pyprojectutils")

from cli import stat_documentation_command

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(stat_documentation_command())
