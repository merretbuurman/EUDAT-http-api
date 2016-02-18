# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from ..base import ExtendedApiResource
from .. import decorators as decorate

from ..services.neo4j import migraph
from ..services.irodsclient import icom

# AUTH
# from confs import config
# from flask.ext.security import roles_required, auth_token_required

from restapi import get_logger
logger = get_logger(__name__)


#####################################
class PidHandle(ExtendedApiResource):

    @decorate.apimethod
    def get(self):
        """ Get pid """
        logger.warning("irods call %s", icom.list())
        logger.warning("graph call %s", migraph.other())
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        migraph.cypher(query)
        return self.response('Hello PID!')
