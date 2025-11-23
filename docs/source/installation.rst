============
Installation
============


Requirements
------------

 * pymadx is developed exclusively for Python 3. Version 3.9 is the minimum version.

 * matplotlib
 * numpy
 * pyg4ometry

These are installed automatically with pip.

Installation
------------

pyflubl can be installed using pip with internet access without downloading
the git repository:

::

   pip install pyflubl


Alternatively, if cloning the git repository and installing locally, a set of
useful commands are provided in a simple Makefile included in the main
directory. In this case, to install pymadx, simply run ``make install`` from
the root pymadx directory.::

  cd /my/path/to/repositories/
  git clone git@github.com:bdsim-collaboration/pyflubl.git
  cd pyflubl
  pip install -e .[dev]