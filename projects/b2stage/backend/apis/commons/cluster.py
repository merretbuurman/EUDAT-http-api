# -*- coding: utf-8 -*-

from restapi.rest.definition import EndpointResource
from b2stage.apis.commons.seadatacloud import seadata_vars
from restapi.services.detect import detector
from utilities import path
from utilities.logs import get_logger
log = get_logger(__name__)

DEFAULT_IMAGE_PREFIX = 'docker'

BATCHES_DIR = seadata_vars.get('batch_dir')
ORDERS_DIR = seadata_vars.get('orders_dir')
PRODUCTION_DIR = seadata_vars.get('cloud_dir')

CONTAINERS_VARS = detector.load_group(label='containers')


class ClusterContainerEndpoint(EndpointResource):
    """
    Base to use rancher in many endpoints
    """

    def custom_init(self):
        """ It gets called every time a new request is executed """
        self._handle = None
        self._credentials = {}
        # self.load_credentials()
        # self.get_or_create_handle()

    def load_credentials(self):

        if len(self._credentials) < 1:
            from restapi.services.detect import detector
            self._credentials = detector.load_group(label='resources')
        return self._credentials

    def get_or_create_handle(self):

        if self._handle is None:
            from b2stage.apis.services.rancher import Rancher
            params = self.load_credentials()
            # log.pp(params)
            self._handle = Rancher(**params)
        return self._handle

    def join_paths(self, paths):
        return str(path.build(paths))

    def get_ingestion_path(self, batch_id=None):
        paths = [self._handle._localpath]
        if batch_id is None:
            paths.append('batch')
        else:
            paths.append('ingestion')
            paths.append(batch_id)
        return str(path.build(paths))

    def mount_batch_volume(self, batch_id):
        host_path = self.get_ingestion_path(batch_id)
        container_fixed_path = self.get_ingestion_path()
        return "%s:%s" % (host_path, container_fixed_path)

    def get_input_zip_filename(self, filename=None, extension='zip', sep='.'):
        if filename is None:
            filename = 'input'
        else:
            filename = filename.replace('%s%s' % (sep, extension), '')
        return "%s%s%s" % (filename, sep, extension)

    def get_path_with_suffix(self, icom, mypath, suffix=None):
        paths = [mypath]
        if suffix is not None:
            paths.append(suffix)
        from utilities import path
        suffix_path = str(path.build(paths))
        return icom.get_current_zone(suffix=suffix_path)

    def get_production_path(self, icom, batch_id=None):
        return self.get_path_with_suffix(icom, PRODUCTION_DIR, batch_id)

    def get_batch_path(self, icom, batch_id=None):
        return self.get_path_with_suffix(icom, BATCHES_DIR, batch_id)

    def get_order_path(self, icom, order_id=None):
        return self.get_path_with_suffix(icom, ORDERS_DIR, order_id)

    def get_batch_zipfile_path(self, batch_id, filename=None):
        container_fixed_path = self.get_ingestion_path()
        batch_file = self.get_input_zip_filename(filename)
        return str(path.build([container_fixed_path, batch_file]))

    @staticmethod
    def get_container_name(batch_id, qc_name):
        return '%s_%s' % (batch_id, qc_name.replace('_', ''))

    @staticmethod
    def get_container_image(qc_name, prefix=None):
        if prefix is None:
            prefix = DEFAULT_IMAGE_PREFIX
        return '%s/%s' % (prefix, qc_name)
