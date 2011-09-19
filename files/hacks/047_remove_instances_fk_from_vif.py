# Copyright 2011 OpenStack LLC.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sqlalchemy import Column, Integer, MetaData, Table
from migrate import ForeignKeyConstraint

from nova import log as logging


meta = MetaData()


instances = Table('instances', meta,
             Column('id', Integer(), primary_key=True, nullable=False),
             )


vifs = Table('virtual_interfaces', meta,
        Column('id', Integer(), primary_key=True, nullable=False),
        Column('instance_id', Integer()),
        )


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine;
    # bind migrate_engine to your metadata
    meta.bind = migrate_engine
    dialect = migrate_engine.url.get_dialect().name
    if dialect.startswith('sqlite'):
        return

    try:
        ForeignKeyConstraint(columns=[vifs.c.instance_id],
                             refcolumns=[instances.c.id]).drop()
    except Exception:
        try:
            migrate_engine.execute("ALTER TABLE migrations DROP " \
                                   "FOREIGN KEY " \
                                   "`virtual_interfaces_ibfk_2`;")
        except Exception:
            logging.error(_("foreign key constraint couldn't be removed"))
#            raise


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    dialect = migrate_engine.url.get_dialect().name
    if dialect.startswith('sqlite'):
        return

    try:
        ForeignKeyConstraint(columns=[vifs.c.instance_id],
                             refcolumns=[instances.c.id]).create()
    except Exception:
        logging.error(_("foreign key constraint couldn't be added"))
        raise
