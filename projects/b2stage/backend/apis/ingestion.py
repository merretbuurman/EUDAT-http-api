# -*- coding: utf-8 -*-

"""
Ingestion process submission to upload the SeaDataNet marine data.
"""

from b2stage.apis.commons.endpoint import EudatEndpoint
from b2stage.apis.commons.endpoint import MISSING_BATCH, NOT_FILLED_BATCH
from b2stage.apis.commons.endpoint import PARTIALLY_ENABLED_BATCH, ENABLED_BATCH
from b2stage.apis.commons.endpoint import BATCH_MISCONFIGURATION
from restapi.services.uploader import Uploader
from restapi.flask_ext.flask_celery import CeleryExt
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from b2stage.apis.commons.cluster import INGESTION_DIR, MOUNTPOINT
from b2stage.apis.commons.queue import log_start, log_failure, log_success, log_success_uncertain, log_submitted_async
from utilities import htmlcodes as hcodes
from utilities import path
# from restapi.flask_ext.flask_irods.client import IrodsException
from utilities.logs import get_logger

log = get_logger(__name__)
ingestion_user = 'RM'
BACKDOOR_SECRET = 'howdeepistherabbithole'


class IngestionEndpoint(Uploader, EudatEndpoint, ClusterContainerEndpoint):
    """ Create batch folder and upload zip files inside it """

    def get(self, batch_id):

        log.info("Batch request: %s", batch_id)
        json = {'batch_id': batch_id}
        taskname = 'get_enable_status'
        log_start(self, taskname, json)

        ########################
        # get irods session

        imain = self.get_service_instance(service_name='irods')
        # obj = self.init_endpoint()
        # icom = obj.icommands

        batch_path = self.get_irods_batch_path(imain, batch_id)
        local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
        log.info("Batch irods path: %s", batch_path)
        log.info("Batch local path: %s", local_path)

        batch_status, batch_files = self.get_batch_status(imain, batch_path, local_path)

        ########################
        # if not imain.is_collection(batch_path):
        if batch_status == MISSING_BATCH:
            err_msg = ("Batch '%s' not enabled or you have no permissions"
                % batch_id)
            log_failure(self, taskname, json, err_msg)
            return self.send_errors(
                err_msg,
                code=hcodes.HTTP_BAD_NOTFOUND)

        if batch_status == BATCH_MISCONFIGURATION:
            err_msg = "Misconfiguration for batch_id %s" % batch_id
            err_msg2 = ('$%s %s files in %s (expected 1)' %
                err_msg, len(batch_files), batch_path))
            log_failure(self, taskname, json, err_msg2)
            return self.send_errors(
                err_msg,
                code=hcodes.HTTP_BAD_REQUEST)

        # files = imain.list(batch_path, detailed=True)
        # if len(files) != 1:
        #     return self.send_errors(
        #         "Batch '%s' not yet filled" % batch_id,
        #         code=hcodes.HTTP_BAD_REQUEST)

        # if batch_status == NOT_FILLED_BATCH:
        #     return self.send_errors(
        #         "Batch '%s' not yet filled" % batch_id,
        #         code=hcodes.HTTP_BAD_REQUEST)

        data = {}
        data['batch'] = batch_id

        if batch_status == NOT_FILLED_BATCH:
            data['status'] = 'not_filled'
            desc = 'The batch was not filled' # TODO MATTIA: What does this mean?
            log_success(self, taskname, json, data['status'], desc]) # TODO MATTIA: Is this success or not?

        elif batch_status == ENABLED_BATCH:
            data['status'] = 'enabled'
            desc = 'The batch was enabled.'
            log_success(self, taskname, json, data['status'], desc])

        elif batch_status == PARTIALLY_ENABLED_BATCH:
            data['status'] = 'partially_enabled'
            desc = 'The batch was partially enabled' # TODO MATTIA: What does this mean?
            log_success(self, taskname, json, data['status'], desc]) # TODO MATTIA: Is this success or not?

        # data['files'] = []
        # for _, f in files.items():
        #     data['files'].append(f)
        data['files'] = batch_files

        return data
        # return "Batch '%s' is enabled and filled" % batch_id

    def put(self, batch_id, file_id):
        """
        Let the Replication Manager upload a zip file into a batch folder
        """

        log.info('Received request to upload batch "%s"' % batch_id)

        # Log start (of upload) into RabbitMQ
        taskname = 'upload'
        json_input = self.get_input() # call only once
        log_start(self, taskname, json_input)

        ########################
        # get irods session
        obj = self.init_endpoint()
        icom = obj.icommands

        batch_path = self.get_irods_batch_path(icom, batch_id)
        log.info("Batch path: %s", batch_path)

        ########################
        # Check if the folder exists and is empty

        # Failure: Folder does not exist or no permissions
        if not icom.is_collection(batch_path):
            err_msg = ("Batch '%s' not enabled or you have no permissions"
                       % batch_id)
            log.warn(err_msg)
            log_failure(self, taskname, json_input, err_msg)
            return self.send_errors(err_msg, code=hcodes.HTTP_BAD_NOTFOUND)

        ########################
        # Check for mimetype
        # NOTE: only streaming is allowed, as it is more performant
        ALLOWED_MIMETYPE_UPLOAD = 'application/octet-stream'
        from flask import request

        # Failure: Wrong mimetype:
        if request.mimetype != ALLOWED_MIMETYPE_UPLOAD:
            err_msg = ("Only mimetype allowed for upload: %s"
                % ALLOWED_MIMETYPE_UPLOAD)
            log.warn(err_msg)
            log_failure(self, taskname, json_input, err_msg)
            return self.send_errors(
                err_msg,
                code=hcodes.HTTP_BAD_REQUEST)

        backdoor = file_id == BACKDOOR_SECRET
        response = {
            'batch_id': batch_id,
            'status': 'filled',
        }

        ########################
        zip_name = self.get_input_zip_filename(file_id)
        zip_path_irods = self.complete_path(batch_path, zip_name)
        # E.g. /myIrodsZone/batches/<batch_id>/<zip-name>

        # This path is created by the POST method, important to keep this check here
        if backdoor and icom.is_dataobject(zip_path_irods):
            response['status'] = 'exists'
            desc = 'Backdoor: A file had been uploaded already for this batch. Stopping.'
            log_success_uncertain(self, taskname, json_input, response['status'], desc)
            return response

        ########################
        log.verbose("Cloud path: %s", zip_path_irods)  # ingestion

        local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
        path.create(local_path, directory=True, force=True)
        zip_path = path.join(local_path, zip_name)
        log.info("Local path: %s", zip_path)

        # try:
        #     # NOTE: we know this will always be Compressed Files (binaries)
        #     iout = icom.write_in_streaming(destination=zip_path_irods, force=True)
        # except BaseException as e:
        #     log.error("Failed streaming to iRODS: %s", e)
        #     return self.send_errors(
        #         "Failed streaming towards B2SAFE cloud",
        #         code=hcodes.HTTP_SERVER_ERROR)
        # else:
        #     log.info("irods call %s", iout)
        #     # NOTE: permissions are inherited thanks to the POST call

        try:
            # NOTE: we know this will always be Compressed Files (binaries)
            out = self.upload_chunked(destination=zip_path, force=True)

        except BaseException as e:

            # Failure: Streaming into iRODS
            log.error("Failed streaming zip path (%s) to file system: %s", zip_path, e)
            err_msg = 'Failed streaming zip path to file system'
            log_failure(self, taskname, json_input, err_msg)
            return self.send_errors(
                err_msg,
                code=hcodes.HTTP_SERVER_ERROR)
        else:
            msg = ("File uploaded: %s", out)
            log.info(msg)
            log_progress(self, taskname, json_input, msg)

        log.info("Submit async celery task (copy_from_b2host_to_b2safe)")
        # task = CeleryExt.copy_from_b2safe_to_b2host.apply_async(
        task = CeleryExt.copy_from_b2host_to_b2safe.apply_async(
            args=[batch_id, zip_path_irods, str(zip_path), backdoor],
            queue='ingestion', routing_key='ingestion')
        log.warning("Async job: %s", task.id)

        # return self.force_response(response)
        # TODO: Return 202!
        log_submitted_async(self, taskname, json_input, task.id)
        return self.return_async_id(task.id)

    def post(self):
        """
        Create the batch folder if not exists
        """

        json_input = self.get_input() # call only once
        batch_id = json_input['batch_id'] if 'batch_id' in json_input else None

        if batch_id is None:
            return self.send_errors(
                "Mandatory parameter 'batch_id' missing",
                code=hcodes.HTTP_BAD_REQUEST)

        log.info('Received request to enable batch "%s"' % batch_id)
        taskname = 'enable'
        log_start(self, taskname, json_input)

        ##################
        # Get irods session
        obj = self.init_endpoint()
        # icom = obj.icommands

        # NOTE: Main API user is the key to let this happen
        imain = self.get_service_instance(service_name='irods')

        batch_path = self.get_irods_batch_path(imain, batch_id)
        log.info("Batch path: %s", batch_path)

        ##################
        # Does it already exist? Is it a collection?
        if not imain.is_collection(batch_path):
            # Enable the batch
            batch_path = self.get_irods_batch_path(imain, batch_id)
            # Create the path and set permissions
            imain.create_collection_inheritable(batch_path, obj.username)
            # # Remove anonymous access to this batch
            # ianonymous.set_permissions(
            #     batch_path,
            #     permission='null', userOrGroup=icom.anonymous_user)
            local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
            path.create(local_path, directory=True, force=True)

            ##################
            response = "Batch '%s' enabled" % batch_id
            status = 'enabled'

        else:
            log.debug("Already exists")
            response = "Batch '%s' already exists" % batch_id
            status = 'exists'

        log_success(self, taskname, json_input, status, response)
        return self.force_response(response)

    def delete(self):

        json_input = self.get_input()
        taskname = 'delete_batch'
        log_start(self, taskname, json_input)

        imain = self.get_service_instance(service_name='irods')
        batch_path = self.get_irods_batch_path(imain)
        log.debug("Batch path: %s", batch_path)

        task = CeleryExt.delete_batches.apply_async(
            args=[batch_path, json_input],
            queue='ingestion', routing_key='ingestion'
        )
        log.warning("Async job: %s", task.id)
        log_submitted_async(self, taskname, json_input, task.id)
        return self.return_async_id(task.id)
