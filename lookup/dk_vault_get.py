import os
import requests
import json
import string
import random
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
        if 'status' not in resp:
            decrypted = decrypt_response(resp, variable)
        elif 'status' in resp and resp['status'] == 'not found':
            ret.append(resp["status"])
            return ret

        ret.append(decrypted)

        return ret


def get_random_string(length):
    s = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    return s


# Unencrypt vault data to memory and remove it after variable assignment
def decrypt_response(content, variable):
    rand = get_random_string(6)
    temp = '_'.join(['/dev/shm/', variable, 'vault_decrypt_temp', rand])

    with open(temp, 'w') as f:
        f.write(content[variable])
        f.flush()
        vault = os.popen(' '.join(['ansible-vault', 'decrypt', temp, "--output -"])).read()

    os.remove(temp)

    return vault
