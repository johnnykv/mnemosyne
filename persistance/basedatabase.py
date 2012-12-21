# Copyright (C) 2012 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, DateTime, String, Boolean
from sqlalchemy import create_engine


class BaseDatabase(object):
        def __init__(self, connection_string):
            self.engine = create_engine(connection_string)
            self.tables = {}

            metadata = MetaData()

            self.tables['hpfeed'] = Table('hpfeed', metadata,
                                          Column(
                                          'hpfeed_id', Integer, primary_key=True),
                                          Column('timestamp',
                                                 DateTime, nullable=False),
                                          Column(
                                          'channel', String, nullable=False),
                                          Column(
                                          'ident', String, nullable=False),
                                          Column(
                                          'payload', String, nullable=False),
                                          Column('normalized', Boolean, default=False),
                                          )

            self.tables['session'] = Table('session', metadata,
                                           Column(
                                           'session_id', Integer, primary_key=True),
                                           Column(
                                           'session_type', String, nullable=False),
                                           Column('hpfeed_id',
                                                  Integer, ForeignKey(
                                                  'hpfeed.hpfeed_id')),
                                           Column('timestamp',
                                                  DateTime, nullable=False),
                                           Column(
                                           'source_ip', String, nullable=True),
                                           Column('source_port',
                                                  Integer, nullable=True),
                                           Column(
                                           'destination_ip', String, nullable=True),
                                           Column(
                                           'destination_port', Integer, nullable=True),
                                           )

            self.tables['url'] = Table('url', metadata,
                                       Column('url_id', String,
                                              primary_key=True, autoincrement=False),
                                       Column('hpfeed_id', Integer,
                                              ForeignKey('hpfeed.hpfeed_id')),
                                       Column('scheme', String, nullable=True),
                                       Column('netloc', String, nullable=True),
                                       Column('path', String, nullable=True),
                                       Column('params', String, nullable=True),
                                       Column('query', String, nullable=True),
                                       )

            self.tables['session_http'] = Table('session_http', metadata,
                                                Column('session_id', Integer, ForeignKey('session.session_id'), primary_key=True, autoincrement=False),
                                                Column('header',
                                                       String, nullable=True),
                                                Column(
                                                'body', String, nullable=True),
                                                Column(
                                                'host', String, nullable=True),
                                                Column(
                                                'verb', String, nullable=True),
                                                Column('url_id', String, ForeignKey(
                                                       'url.url_id'), nullable=False)
                                                )

            metadata.create_all(self.engine)
