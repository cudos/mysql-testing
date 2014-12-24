# -*- coding: utf-8 -*-
# Copyright 2014, Jens Hoffmann <xmcpam@gmail.com>
#
# This file is part of mysql-testing.
#
# mysql-testing is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mysql-testing is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
import os as _os
import pytest as _pytest
import testing.mysql as _mysql


@_pytest.fixture
def my(request):
    mysql = _mysql.MySQLTestHelper()
    def clean():
        mysql.stop_server()
        mysql.clean()
    request.addfinalizer(clean)
    return mysql


def test_MySQLTesHelper___init__(my):
    basedir = my.get_basedir()
    assert _os.path.exists(basedir)
    assert _os.path.exists(_os.path.join(basedir, "data"))
    assert _os.listdir(_os.path.join(basedir, "data")) == [
        "performance_schema",
        "mysql"
    ]


def test_MySQLTesHelper_create_database(my):
    my.start_server()
    my.create_database("test-db")
    con = my.get_connection("test-db")
    con.execute("CREATE TABLE t (id INTEGER)")
    assert con.execute("SHOW TABLES").fetchall() == [('t',)]


def test_MySQLTestHelper_clean(my):
    my.start_server()
    my.create_database("test-db")
    my.stop_server()
    my.clean()
    assert not _os.path.exists(my.get_basedir())


def test_MySQLTesHelper_is_running(my):
    assert my.is_running() == False
    my.start_server()
    assert my.is_running() == True
    my.stop_server()
    assert my.is_running() == False

