# -*- coding: utf-8 -*-

from b2stage.apis.commons.cluster import ClusterContainerEndpoint as Endpoint
from utilities.logs import get_logger
from b2stage.apis.commons.queue import log_start, log_submitted_async
from restapi.flask_ext.flask_celery import CeleryExt

log = get_logger(__name__)


class ListResources(Endpoint):

    def post(self):

        taskname = 'list_sdc_resources'
        json_input = self.get_input()
        log_start(self, taskname, json_input)

        imain = self.get_service_instance(service_name='irods')
        task = CeleryExt.list_resources.apply_async(
            args=[
                self.get_irods_batch_path(imain),
                self.get_irods_order_path(imain),
                json_input
            ]
        )
        log.warning("Async job: %s", task.id)
        log_submitted_async(self, taskname, json_input, task.id)
        return self.return_async_id(task.id)
