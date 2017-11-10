# -*- coding: utf-8 -*-

"""
Communicating with docker via rancher

NOTE: to convert the output json and read it:
https://jsonformatter.curiousconcept.com/
"""

from utilities.logs import get_logger
log = get_logger(__name__)


class Rancher(object):

    def __init__(self, key, secret, url, project):
        self.connect(key, secret, url)
        self.project_handle(project)

    def connect(self, key, secret, url):
        import gdapi
        self._client = gdapi.Client(
            url=url, access_key=key, secret_key=secret)

    def project_handle(self, project):
        self._project = project
        return self._client.by_id_project(self._project)

    def hosts(self):
        """
        'state':'active'
        'agentIpAddress':'130.186.13.150'
        'hostname':'sdc01'
        'driver':'openstack',
        'openstackConfig':{
            'username':'pdonorio'
        'info':{
            'osInfo':{
               'dockerVersion':'Docker version 1.13.1, build 092cba3',
               'kernelVersion':'4.4.0',
               'operatingSystem':'Ubuntu 16.04 LTS'
            'diskInfo':{
               'fileSystems':{
                  '/dev/vda1':{
                     'capacity':29715

            'cpuInfo':{
               'count':8,
            'memoryInfo':{
                'memFree':20287,
                'memTotal':24111,
            "physicalHostId":"1ph3",
        """
        hosts = {}
        for data in self._client.list_host():
            host = data.get('hostname')
            if not data.get('state') == 'active':
                log.warning("Host %s not active", host)
                continue
            hosts[data.get('physicalHostId').replace('p', '')] = {
                'name': host,
                'ip': data.get('agentIpAddress'),
                'provider': data.get('driver'),
            }
        return hosts

    def obj_to_dict(self, obj):
        import json
        return json.loads(obj.__repr__().replace("'", '"'))

    def containers(self):
        """
        https://github.com/rancher/gdapi-python/blob/master/gdapi.py#L68
        'io.rancher.container.system': 'true'
        """

        system_label = 'io.rancher.container.system'

        containers = {}
        for info in self._client.list_container():

            # detect system containers
            labels = self.obj_to_dict(info.get('labels', {}))
            if labels.get(system_label) is not None:
                continue

            # info.get('externalId')
            cid = info.get('data', {}) \
                .get('fields', {}).get('labels', {}) \
                .get('io.rancher.container.uuid')
            name = info.get('name')

            if cid is None:
                log.warning("Container %s launching", name)

            containers[cid] = {
                'name': name,
                'image': info.get('imageUuid'),
                'command': info.get('command'),
                'host': info.get('hostId'),
            }

        return containers

    def list(self):

        resources = {}
        containers = self.containers()
        ckey = 'containers'

        for host_id, host_data in self.hosts().items():

            host_name = host_data.get('name')
            if ckey not in host_data:
                host_data[ckey] = {}

            for container_id, container_data in containers.items():
                if container_data.get('host') == host_id:
                    container_data.pop('host')
                    host_data['containers'][container_id] = container_data

            resources[host_name] = host_data

        return resources

    def test(self):

        # https://github.com/rancher/rancher/issues/10305
        project = self.project_handle()
        uri = project.actions.get('update')
        # FIXME: use uri to create a host and a container
        uri

        # client.list_host()
        # client.list_project()
        # client.list_service()

        # for element in client.list_host().data:
        #     # log.pp(element.data)
        #     print(element.id, element.uuid, element.hostname)
        #     # for key, value in element.items():
        #     #     print(key)
        # # break

        pass
