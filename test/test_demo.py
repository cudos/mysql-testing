# -*- coding: utf-8 -*-
import getpass as _getpass
import os as _os
import pytest as _pytest
import shutil as _shutil
import subprocess as _subprocess
import tempfile as _tempfile


class MySQLTestHelper(object):
    def __init__(self):
        pass

    def add(self):
        pass

    def setup_tmp_database(self):
        self._basedir = _tempfile.mkdtemp()
        self._datadir = _os.path.join(self._basedir, "data")
        self._my_cnf_file = _os.path.join(self._basedir, "my.cnf")
        self._user = _getpass.getuser()
        self._pid_file = _os.path.join(self._basedir, "mysqld.pid")
        self._socket_file = _os.path.join(self._basedir, "mysqld.sock")
        self._error_log_file = _os.path.join(self._basedir, "error.log")
        user = "--user=%s" % self._user
        datadir = "--datadir=%s" % self._datadir
        _subprocess.call(["mysql_install_db", user, datadir])
        # Render mysql configuration template
        self._my_cnf = self._my_cnf_tmpl % (
            dict(
                user = self._user,
                pid_file = self._pid_file,
                socket_file = self._socket_file,
                error_log_file = self._error_log_file,
                datadir = self._datadir,
                port = "9191",
            )
        )
        open(self._my_cnf_file, "w").write(self._my_cnf)
        defaults_file = "--defaults-file=%s" % self._my_cnf_file
        # Let's start the mysql daemon process
        _os.spawnl(_os.P_NOWAIT, "mysqld_safe %s" % defaults_file)
        import time as _time
        _time.sleep(10)
        # We must set a root password
        _subprocess.call(["mysqladmin", defaults_file, "--user", "jens", "password", "'top-secret'"])
        # _subprocess.call(["mysqladmin", "-u", "root", "-h", "charlotte", "password", "'top-secret'"])

        # _subprocess.call(["cat", self._my_cnf_file])
        _subprocess.call(["cat", self._error_log_file])

    def clean(self):
        _shutil.rmtree(self._datadir)

    _my_cnf_tmpl = """
#
# The MySQL database server configuration file.
#
# You can copy this to one of:
# - "/etc/mysql/my.cnf" to set global options,
# - "~/.my.cnf" to set user-specific options.
#
# One can use all long options that the program supports.
# Run program with --help to get a list of available options and with
# --print-defaults to see which it would actually understand and use.
#
# For explanations see
# http://dev.mysql.com/doc/mysql/en/server-system-variables.html

# This will be passed to all mysql clients
# It has been reported that passwords should be enclosed with ticks/quotes
# escpecially if they contain "#" chars...
# Remember to edit /etc/mysql/debian.cnf when changing the socket location.
[client]
port		= %(port)s
socket		= %(socket_file)s

# Here is entries for some specific programs
# The following values assume you have at least 32M ram

# This was formally known as [safe_mysqld]. Both versions are currently parsed.
[mysqld_safe]
socket		= %(socket_file)s
nice		= 0

[mysqld]
#
# * Basic Settings
#
user		= %(user)s
pid-file	= %(pid_file)s
socket		= $(socket_file)s
port		= %(port)s
basedir		= /usr
datadir		= %(datadir)s
tmpdir		= /tmp
lc-messages-dir	= /usr/share/mysql
skip-external-locking
#
# Instead of skip-networking the default is now to listen only on
# localhost which is more compatible and is not less secure.
bind-address		= 127.0.0.1
#
# * Fine Tuning
#
key_buffer		= 16M
max_allowed_packet	= 16M
thread_stack		= 192K
thread_cache_size       = 8
# This replaces the startup script and checks MyISAM tables if needed
# the first time they are touched
myisam-recover         = BACKUP
#max_connections        = 100
#table_cache            = 64
#thread_concurrency     = 10
#
# * Query Cache Configuration
#
query_cache_limit	= 1M
query_cache_size        = 16M
#
# * Logging and Replication
#
# Both location gets rotated by the cronjob.
# Be aware that this log type is a performance killer.
# As of 5.1 you can enable the log at runtime!
#general_log_file        = /var/log/mysql/mysql.log
#general_log             = 1
#
# Error log - should be very few entries.
#
log_error = %(error_log_file)s
#
# Here you can see queries with especially long duration
#log_slow_queries	= /var/log/mysql/mysql-slow.log
#long_query_time = 2
#log-queries-not-using-indexes
#
# The following can be used as easy to replay backup logs or for replication.
# note: if you are setting up a replication slave, see README.Debian about
#       other settings you may need to change.
#server-id		= 1
#log_bin			= /var/log/mysql/mysql-bin.log
expire_logs_days	= 10
max_binlog_size         = 100M
#binlog_do_db		= include_database_name
#binlog_ignore_db	= include_database_name
#
# * InnoDB
#
# InnoDB is enabled by default with a 10MB datafile in /var/lib/mysql/.
# Read the manual for more InnoDB related options. There are many!
#
# * Security Features
#
# Read the manual, too, if you want chroot!
# chroot = /var/lib/mysql/
#
# For generating SSL certificates I recommend the OpenSSL GUI "tinyca".
#
# ssl-ca=/etc/mysql/cacert.pem
# ssl-cert=/etc/mysql/server-cert.pem
# ssl-key=/etc/mysql/server-key.pem

[mysqldump]
quick
quote-names
max_allowed_packet	= 16M

[mysql]
#no-auto-rehash	# faster start of mysql but no tab completition

[isamchk]
key_buffer		= 16M
"""


@_pytest.fixture
def mysql(request):
    helper = MySQLTestHelper()
    helper.setup_tmp_database()
    request.addfinalizer(helper.clean)
    return helper


def test_demo(mysql):
    mysql.get_session().add(SomeObject())
    result = mysql.get_session().query(SomeObject).all()
    assert result == [1, 2, 3]

