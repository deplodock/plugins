import os
import requests
import json
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):

        ret = []
        dk = "https://api.deplodock.ru/v1/inventory"

        if os.environ.get('DK_TOKEN'):
            token = os.environ['DK_TOKEN']
        else:
            raise AnsibleError("DK_TOKEN not set")

        if len(terms) < 2:
            raise AnsibleError(terms)

        inventory = terms[0]
        entity = terms[1]
        entity = "/".join([inventory, entity])
        entity = entity.replace('//', '/')

        variable = entity.split("/")
        variable = variable[len(variable) - 1]

        # Build API uri
        dk_api = [dk, entity]
        api_uri = "/".join(dk_api)

        headers = {'X-Auth-Token': token}
        r = requests.get(api_uri, headers=headers)

        resp = json.loads(r.content)
        json_var = json.loads(resp[variable])

        ret.append(json_var)

        return ret
