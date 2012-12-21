from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy import create_engine
from sqlalchemy import exc
from datetime import datetime


class RawlogPersister:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.setup_mapping()
        self.conn = self.engine.connect()

    def insert(self, ident, chan, payload):
        self.conn.execute(self.events_table.insert(),
                          {'chan': chan,
                           'ident': ident,
                           'payload': payload,
                           'submission_time': datetime.utcnow()})

    def setup_mapping(self):
        meta = MetaData()

        self.events_table = Table('events', meta,
                                  Column('id', Integer, primary_key=True, ),
                                  Column('submission_time', String),
                                  Column('channel', String),
                                  Column('ident', String),
                                  Column('payload', String),
                                  )

        self.engine = create_engine(self.connection_string)

        meta.create_all(self.engine)
