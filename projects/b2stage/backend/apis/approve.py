# -*- coding: utf-8 -*-

"""
Move data from ingestion to production
"""

#################
# IMPORTS
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
# from b2stage.apis.commons.endpoint import EudatEndpoint
from b2stage.apis.commons.b2handle import B2HandleEndpoint
# from restapi.rest.definition import EndpointResource
from b2stage.apis.commons.seadatacloud import Metadata as md
from b2stage.apis.commons.queue import log_start, log_failure, log_progress, log_submitted_async
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate
from restapi.flask_ext.flask_irods.client import IrodsException
# from restapi.services.detect import detector
from utilities.logs import get_logger

log = get_logger(__name__)


#################
# REST CLASS
# class Approve(EndpointResource):
class MoveToProductionEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def post(self, batch_id):

        # Log start into RabbitMQ
        log.info('Received request to approve batch "%s"' % batch_id)
        json_input = self.get_input() # may only be called once!
        taskname = 'approve'
        log_start(self, taskname, json_input)

        ################
        # 0. check parameters
        params = json_input.get('parameters', {})

        # Failure: Missing parameters
        if len(params) < 1:
            err_msg = "parameters' is empty"
            log.warn(err_msg)
            log_failure(self, taskname, json_input, err_msg)
            return self.send_errors(
                err_msg, code=hcodes.HTTP_BAD_REQUEST)

        # Get file names from payload
        files = params.get('pids', {}) # TODO: This returns the files names, not the PIDs!

        # Failure: Missing file list in parameter 'pids'
        if len(files) < 1:
            err_msg = "'pids' parameter is empty list"
            log.warn(err_msg)
            log_failure(self, taskname, json_input, err_msg)
            return self.send_errors(
                err_msg,
                code=hcodes.HTTP_BAD_REQUEST)

        # Get file data
        filenames = []
        for data in files:

            # Failure: File data is not a dictionary.
            if not isinstance(data, dict):
                err_msg = "File list contains at least one wrong entry (not valid JSON)"
                log.warn(err_msg)
                log_failure(self, taskname, json_input, err_msg)
                return self.send_errors(
                    err_msg,
                    code=hcodes.HTTP_BAD_REQUEST)

            # Retrieve file parameters
            for key in md.keys:  # + [md.tid]:
                value = data.get(key)
                error = None
                if value is None:
                    error = 'Missing parameter: %s' % key
                else:
                    value_len = len(value)
                if value_len > md.max_size:
                    error = "Param '%s': exceeds size %s" % (key, md.max_size)
                if value_len < 1:
                    error = "Param '%s': empty" % key

                # Failure: Some parameter not valid
                if error is not None:
                    log.warn(error)
                    log_failure(self, taskname, json_input, error)
                    return self.send_errors(
                        error, code=hcodes.HTTP_BAD_REQUEST)

            # Fill list of filenames
            filenames.append(data.get(md.tid))

        ################
        # 1. check if irods path exists
        imain = self.get_service_instance(service_name='irods')
        self.batch_path = self.get_irods_batch_path(imain, batch_id)
        log.debug("Batch path: %s", self.batch_path)

        # Failure: Path does not exist (or no permission)
        if not imain.is_collection(self.batch_path):
            err_msg = ("Batch '%s' not enabled (or no permissions)" % batch_id)
            log.warn(err_msg)
            log_failure(self, taskname, json_input, err_msg)
            return self.send_errors(
                err_msg,
                code=hcodes.HTTP_BAD_REQUEST)

        ################
        # 2. make batch_id directory in production if not existing
        self.prod_path = self.get_irods_production_path(imain, batch_id)
        log.debug("Production path: %s", self.prod_path)
        obj = self.init_endpoint()
        imain.create_collection_inheritable(self.prod_path, obj.username)

        # Log progress into RabbitMQ
        log_progress(self, taskname, json_input, 'Dir on production cloud created (if not existing).')

        ################
        # ASYNC
        log.info("Submit async celery task")
        from restapi.flask_ext.flask_celery import CeleryExt
        task = CeleryExt.move_to_production_task.apply_async(
            args=[batch_id, self.prod_path, json_input],
            queue='ingestion', routing_key='ingestion')
        log.warning("Async job: %s", task.id)

        log_submitted_async(self, taskname, json_input, task.id)
        # TODO return 202
        return self.return_async_id(task.id)
