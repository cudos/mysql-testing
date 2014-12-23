# -*- coding: utf-8 -*-
# Copyright 2014, Jens Hoffmann <xmcpam@gmail.com>
#
# This file is part of mysql-testing.
#
# mysql-testing is free software: you can redistribute it and/or
# modify # it under the terms of the GNU General Public License as
# published by # the Free Software Foundation, either version 3 of the
# License, or # (at your option) any later version.
#
# mysql-testing is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
import getpass as _getpass
import os as _os
import shutil as _shutil
import sqlalchemy as _sqlalchemy
import sqlalchemy.engine.url as _sqlalchemy_url
import subprocess as _subprocess
import tempfile as _tempfile
import time as _time


class MySQLTestHelper(object):
    """
    Help to setup and maintain temporary mysql instances

    Example session:
    >>> my = MySQLTestHelper()
    >>> my.start_server()
    >>> my.create_database("test-db")
    >>> con = my.get_connection("test-db")
    >>> # con is a sqlalchemy connection!
    >>> # do nasty things with it here...
    >>> con.close()
    >>> my.create_database("test-db-2")
    >>> con = my.get_connection("test-db-2")
    >>> # ...
    >>> con.stop_server()
    >>> # Be aware that this wipes out the whole DB
    >>> con.clean()
    """
    def __init__(self):
        self._stdout = open(_os.devnull, "w")
        self._basedir = _tempfile.mkdtemp()
        self._current_user = _getpass.getuser(),
        self._datadir = _os.path.join(self._basedir, "data"),
        _subprocess.call([
            "/usr/bin/mysql_install_db",
            "--no-defaults",
            "--user=%s" % self._current_user,
            "--datadir=%s" % self._datadir
        ], stdout=self._stdout)
        self._error_log_file = _os.path.join(self._basedir, "error.log")
        self._pid_file = _os.path.join(self._basedir, "pid")
        self._socket_file = _os.path.join(self._basedir, "socket")
        self._is_running = False

    def get_basedir(self):
        return self._basedir

    def create_database(self, db_name):
        _subprocess.call([
            "/usr/bin/mysqladmin",
            "--no-defaults",
            "--user=root",
            "--socket=%s" % self._socket_file,
            "create",
            db_name
        ], stdout=self._stdout)

    def start_server(self):
        if self._is_running:
            print "The server is already running"
            return
        _subprocess.Popen([
            "/usr/bin/mysqld_safe",
            "--no-defaults",
            "--log-error=%s" % self._error_log_file,
            "--pid-file=%s" % self._pid_file,
            "--datadir=%s" % self._datadir,
            "--user=%s" % self._current_user,
            "--socket=%s" % self._socket_file,
        ], stdout=self._stdout)
        connection = None
        while not connection:
            try:
                connection = self.get_connection("mysql")
            except Exception, e:
                _time.sleep(1)
        connection.close()
        self._is_running = True

    def stop_server(self):
        if _os.path.exists(self._pid_file):
            pid = int(open(self._pid_file, "r").read())
            _subprocess.call([
                "/usr/bin/mysqladmin",
                "--user=root",
                "--socket=%s" % self._socket_file,
                "shutdown"
            ], stdout=self._stdout)
            while _os.path.exists("/proc/%d" % pid):
                _time.sleep(1)
        self._is_running = False

    def get_connection(self, db_name):
        db = _sqlalchemy_url.URL(
            drivername="mysql", username="root", database=db_name, query={
                "unix_socket": self._socket_file,
            }
        )
        engine = _sqlalchemy.create_engine(name_or_url=db)
        return engine.connect()

    def clean(self):
        if _os.path.exists(self._basedir):
            _shutil.rmtree(self._basedir)

