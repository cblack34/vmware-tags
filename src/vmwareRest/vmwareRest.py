import json

import requests
from requests.auth import HTTPBasicAuth


class vmwareRest:
    # Connection Vars
    server = None
    username = None
    password = None
    validate_certs = False
    rest_session_id = None

    tags = None

    def __init__(self, url, username, password, verify):
        self.server = url
        self.username = username
        self.password = password
        self.validate_certs = verify

    def get_rest_vcenter_url(self):
        return self.server + "/rest"

    def get_rest_session_id(self):
        vcenter_url = self.get_rest_vcenter_url()
        if self.rest_session_id is None:
            vcenter_auth_url = vcenter_url + "/com/vmware/cis/session"
            resp = requests.post(
                vcenter_auth_url,
                auth=HTTPBasicAuth(self.username, self.password),
                verify=self.validate_certs
            )
            resp.raise_for_status()
            self.rest_session_id = resp.json()['value']

        return self.rest_session_id

    def get_tags(self):
        session_id = self.get_rest_session_id()
        url = f"{self.get_rest_vcenter_url()}/com/vmware/cis/tagging/tag"

        resp = requests.get(
            url,
            headers={'vmware-api-session-id': session_id}, verify=self.validate_certs
        )

        return resp

    def get_tag_info(self, tag):
        session_id = self.get_rest_session_id()
        url = f"{self.get_rest_vcenter_url()}/com/vmware/cis/tagging/tag/id:{tag}"

        resp = requests.get(
            url,
            headers={'vmware-api-session-id': session_id}, verify=self.validate_certs
        )

        return resp

    def get_tags_with_info(self):
        if self.tags is not None:
            return self.tags

        self.tags = {}
        session_id = self.get_rest_session_id()
        vcenter_url = self.get_rest_vcenter_url()

        vcenter_tags_url = vcenter_url + "/com/vmware/cis/tagging/tag"
        vcenter_tags_get_url = vcenter_url + "/com/vmware/cis/tagging/tag/id:{}"
        vcenter_list_tags_url = vcenter_url + "/com/vmware/cis/tagging/tag/id:{}?~action=list-tags-for-category"
        vcenter_category_list_url = vcenter_url + "/com/vmware/cis/tagging/category"
        vcenter_category_get_url = vcenter_url + "/com/vmware/cis/tagging/category/id:{}"

        resp = requests.get(
            vcenter_tags_url,
            headers={'vmware-api-session-id': session_id}, verify=self.validate_certs
        )

        tags_ids = resp.json()['value']

        categories = {}

        for tag_id in tags_ids:
            resp = requests.get(
                vcenter_tags_get_url.format(tag_id),
                headers={'vmware-api-session-id': session_id},
                verify=self.validate_certs
            )
            tag_value = resp.json()['value']
            tag_name = tag_value['name'].replace(" ", "_")
            category_id = tag_value['category_id']

            self.tags[tag_id] = {'name': tag_name, 'category_id': category_id}
            categories[category_id] = 1

        for category_id, nil in categories.items():
            resp = requests.get(
                vcenter_category_get_url.format(category_id),
                headers={'vmware-api-session-id': session_id},
                verify=self.validate_certs
            )
            category_value = resp.json()['value']
            category_name = category_value['name'].replace(" ", "_")
            category_cardinality = category_value['cardinality']
            category_associable_types = category_value['associable_types']
            category_description = category_value['description']

            categories[category_id] = {
                'name': category_name,
                'cardinality': category_cardinality,
                'associable_types': category_associable_types,
                'description': category_description
            }
        for tag_id, tag_info in self.tags.items():
            self.tags[tag_id].update({'category': categories[tag_info['category_id']]})

        return self.tags

    def get_tags_categories(self):
        session_id = self.get_rest_session_id()
        url = f"{self.get_rest_vcenter_url()}/com/vmware/cis/tagging/category"

        resp = requests.get(
            url,
            headers={'vmware-api-session-id': session_id}, verify=self.validate_certs
        )

        return resp

    def get_tag_category_info(self, cat_id):
        session_id = self.get_rest_session_id()
        url = f"{self.get_rest_vcenter_url()}/com/vmware/cis/tagging/category/id:{cat_id}"

        resp = requests.get(
            url,
            headers={'vmware-api-session-id': session_id}, verify=self.validate_certs
        )

        return resp

    def get_vms_by_tags(self, tag):
        session_id = self.get_rest_session_id()
        vcenter_url = self.get_rest_vcenter_url()

        vcenter_vm_by_tag_url = vcenter_url + "/com/vmware/cis/tagging/tag-association?~action=list-attached-objects-on-tags"

        body = {"tag_ids": ["{}".format(tag)]}

        resp = requests.post(
            vcenter_vm_by_tag_url, data=json.dumps(body),
            headers={
                        'vmware-api-session-id': session_id,
                        'content-type': 'application/json'
                    },
            verify=self.validate_certs
            )

        try:
            vms = resp.json()['value'][0]['object_ids']

        except IndexError as e:
            vms = []

        for vm in vms:
            vm['tag'] = tag

        return vms

    def get_clusters(self, filters=None):
        session_id = self.get_rest_session_id()
        vcenter_url = self.get_rest_vcenter_url()

        vcenter_clusters_url = vcenter_url + "/vcenter/cluster"

        if filters != None:
            vcenter_clusters_url = vcenter_clusters_url + '?' + filters

        resp = requests.get(
            vcenter_clusters_url,
            headers={'vmware-api-session-id': session_id}, verify=self.validate_certs
        )

        cluster_ids = resp.json()['value']

        return cluster_ids

    def get_datacenters(self, filters=None):
        session_id = self.get_rest_session_id()
        vcenter_url = self.get_rest_vcenter_url()

        vcenter_datacenter_url = vcenter_url + "/vcenter/datacenter"

        if filters != None:
            vcenter_datacenter_url = vcenter_datacenter_url + '?' + filters

        resp = requests.get(
            vcenter_datacenter_url,
            headers={'vmware-api-session-id': session_id}, verify=self.validate_certs
        )

        datacenter_ids = resp.json()['value']

        return datacenter_ids

    def get_vm(self, vm):
        session_id = self.get_rest_session_id()
        vcenter_url = self.get_rest_vcenter_url()

        vcenter_vm_url = vcenter_url + "/vcenter/vm/{}"

        resp = requests.get(
            vcenter_vm_url.format(vm),
            headers={'vmware-api-session-id': session_id}, verify=self.validate_certs
        )

        full_vm = resp.json()['value']

        return full_vm

    def get_vm_by_cluster(self, cluster):
        session_id = self.get_rest_session_id()
        vcenter_url = self.get_rest_vcenter_url()

        vcenter_vm_url = vcenter_url + "/vcenter/vm?filter.clusters={}"

        resp = requests.get(
            vcenter_vm_url.format(cluster),
            headers={'vmware-api-session-id': session_id}, verify=self.validate_certs
        )

        vms = resp.json()['value']

        for vm in vms:
            vm['id'] = vm['vm']

        return vms
