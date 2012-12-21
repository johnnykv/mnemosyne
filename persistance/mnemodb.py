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

from sqlalchemy import select

from datetime import datetime

import basedatabase

import logging


class MnemoDB(basedatabase.BaseDatabase):
    def __init__(self, connection_string):
        super(MnemoDB, self).__init__(connection_string)

        self.fk_mapping = {}
        for key in self.tables.keys():
            self.fk_mapping[key] = []
            for fk in self.tables[key].foreign_keys:
                self.fk_mapping[key].append(fk.parent.name)
            self.fk_mapping[key].sort()

        self.need_id_generation = ['url']
        self.check_existance = ['url']

    def insert_normalized(self, ndata, hpfeed_id):
        logging.debug('Inserting normalized item origination from hpfeeds with id: %i' % (hpfeed_id, ))
        conn = self.engine.connect()
        trans = conn.begin()
        try:
            for key, value in ndata.items():
                stack = [[key, value], ]
                fk = {'hpfeed_id': hpfeed_id, }
                while stack:
                    insert = True
                    column, content = stack.pop()
                    if set(self.fk_mapping[column]).issubset(fk.keys()) and 'INSERTED' not in content:
                        if column in self.need_id_generation:
                            content = self.generate_id(column, content)
                        if column in self.check_existance:
                            result = self.already_exists(column, content, conn)
                            if result != None:
                                content['INSERTED'] = True
                                fk[column + '_id'] = result
                                insert = False
                        if insert:
                            result = conn.execute(self.tables[column].insert(
                                dict(content.items() + fk.items())))
                            fk[column + '_id'] = result.inserted_primary_key[0]
                            content['INSERTED'] = True
                    else:
                        if 'INSERTED' not in content:
                            stack.append([column, content])
                    for k, v in content.items():
                        if isinstance(v, dict):
                            if not 'INSERTED' in v:
                                stack.append([k, v])
            #TODO: Set hpfeed normalized = True
            conn.execute(self.tables['hpfeed'].update().
                where(self.tables['hpfeed'].c.hpfeed_id == hpfeed_id).
                values(normalized=True))
            trans.commit()
        except:
            trans.rollback()
            raise

    #special cases
    def generate_id(self, column, content):
        if column == 'url':
            content['url_id'] = content['url']
            del content['url']
        return content

    def already_exists(self, column, content, conn):
        for p in self.tables[column].primary_key:
            pk = p.name
            break
        table = self.tables[column]
        result = conn.execute(select([table], table.c.url_id == content[pk])).fetchone()
        if result != None:
            return result[pk]
        else:
            return None

    def insert_hpfeed(self, ident, chan, payload):
        conn = self.engine.connect()
        result = conn.execute(self.tables['hpfeed'].insert(),
                              {'channel': chan,
                               'ident': ident,
                               'payload': payload,
                               'timestamp': datetime.utcnow()})
        return result.inserted_primary_key[0]

    #extract unnormalized hpfeed data
    def get_hpfeed_data(self, max=None):
        conn = self.engine.connect()
        table = self.tables['hpfeed']
        result = conn.execute(select([table], table.c.normalized == False)).fetchmany(size=max)
        #pk (hpfeed_id) must key in dict.
        return_dict = {}
        for row in result:
            return_dict[row['hpfeed_id']] = {'channel': row['channel'],
                                             'ident': row['ident'],
                                             'payload': str(row['payload']),
                                             'timestamp': row['timestamp'], }
        return return_dict
