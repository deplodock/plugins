import os
import requests
import json
import random
import string
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

        if len(terms) < 3:
            raise AnsibleError(terms)

        inventory = terms[0]
        entity = terms[1]
        data = terms[2]

        entity = "/".join([inventory, entity])
        entity = entity.replace('//', '/')

        variable = entity.split("/")
        variable = variable[len(variable) - 1]

        # Build API uri
        dk_api = [dk, entity]
        api_uri = "/".join(dk_api)

        encrypted = encrypt_data(data, variable)

        headers = {'X-Auth-Token': token}
        r = requests.put(api_uri, headers=headers, data=encrypted)

        resp = json.loads(r.content)
        if resp["status"] != "already exixts":
            r = requests.post(api_uri, headers=headers, data=encrypted)

        ret.append(r.content)

        return ret


def get_random_string(length):
    s = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    return s


def encrypt_data(data, variable):
    temp = ''.join(['/dev/shm/', variable, 'vault_ecrypt_temp', get_random_string(6)])

    wf = open(temp, 'w')
    wf.write(data)
    wf.flush()
    wf.close()
    os.popen(' '.join(['ansible-vault', 'encrypt', temp])).read()

    f = open(temp, 'r')
    encrypted = f.read()
    f.close()

    os.remove(temp)

    return encrypted
