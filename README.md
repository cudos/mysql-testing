mysql-testing
=============
This package includes tools to help working with MySQL
databases in test environments on Debian-like systems.

To see how these tools are used, read the tests included in
the test directory.

Requirements
------------
 * mysql-server
 * python-mysqldb
 * libmysqlclient-dev
 * sqlalchemy

Running the tests
-----------------
Because this package does not provide a setup.py, you have
to add the packages parent directory to your PYTHONPATH.
```
$ export PYTHONPATH=""
$ py.test -s -vv
```

