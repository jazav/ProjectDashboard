import json
import http.client as httplib
import os
import mimetypes
import time
import urllib.parse as urlparse
import io
import base64


class CitrixShareFile:
    def __init__(self, hostname, username, password, client_id, client_secret):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret

    def authenticate(self):
        uri_path = '/oauth/token'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        params = {'grant_type': 'password', 'client_id': self.client_id, 'client_secret': self.client_secret,
                  'username': self.username, 'password': self.password}

        http = httplib.HTTPSConnection(self.hostname)
        http.request('POST', uri_path, urlparse.urlencode(params), headers=headers)
        response = http.getresponse()

        print(response.status, response.reason)
        token = None
        if response.status == 200:
            token = json.loads(response.read())
            print('Received token info', token)

        http.close()
        return token

    def get_authorization_header(self):
        token = self.authenticate()
        return {'Authorization': 'Bearer {}'.format(token['access_token'])}

    def get_hostname(self):
        token = self.authenticate()
        print(token)
        return '{}.sf-api.com'.format(token['subdomain'])

    def get_root(self, get_children=False):
        uri_path = '/sf/v3/Items(allshared)'
        if get_children:
            uri_path = '{}?$expand=Children'.format(uri_path)
        print('GET {}{}'.format(self.get_hostname(), uri_path))
        http = httplib.HTTPSConnection(self.get_hostname())
        http.request('GET', uri_path, headers=self.get_authorization_header())
        response = http.getresponse()

        print(response.status, response.reason)
        items = json.loads(response.read())
        print(items['Id'], items['CreationDate'], items['Name'])
        if 'Children' in items:
            children = items['Children']
            for child in children:
                print(child['Id'], items['CreationDate'], child['Name'])

    def get_item_by_id(self, item_id):
        uri_path = '/sf/v3/Items({})'.format(item_id)
        print('GET {}{}'.format(self.get_hostname(), uri_path))
        http = httplib.HTTPSConnection(self.get_hostname())
        http.request('GET', uri_path, headers=self.get_authorization_header())
        response = http.getresponse()

        print(response.status, response.reason)
        items = json.loads(response.read())
        print(items['Id'], items['CreationDate'], items['Name'])

    def get_folder_with_query_parameters(self, item_id):
        uri_path = '/sf/v3/Items({})?$expand=Children&$select=Id,Name,Children/Id,Children/Name,Children/CreationDate'.format(item_id)
        print('GET {}{}'.format(self.get_hostname(), uri_path))
        http = httplib.HTTPSConnection(self.get_hostname())
        http.request('GET', uri_path, headers=self.get_authorization_header())
        response = http.getresponse()

        print(response.status, response.reason)
        items = json.loads(response.read())
        print(items['Id'], items['Name'])
        if 'Children' in items:
            children = items['Children']
            for child in children:
                print(child['Id'], child['CreationDate'], child['Name'])

        http.close()

    def create_folder(self, parent_id, name, description):
        uri_path = '/sf/v3/Items({})/Folder'.format(parent_id)
        print('POST {}{}'.format(self.get_hostname(), uri_path))
        folder = {'Name': name, 'Description': description}
        headers = self.get_authorization_header()
        headers['Content-Type'] = 'application/json'
        http = httplib.HTTPSConnection(self.get_hostname())
        http.request('POST', uri_path, json.dumps(folder), headers=headers)
        response = http.getresponse()

        print(response.status, response.reason)
        new_folder = json.loads(response.read())
        print('Created Folder {}'.format(new_folder['Id']))

        http.close()

    def update_item(self, item_id, name, description):
        uri_path = '/sf/v3/Items({})'.format(item_id)
        print('PATCH {}{}'.format(self.get_hostname(), uri_path))
        folder = {'Name': name, 'Description': description}
        headers = self.get_authorization_header()
        headers['Content-type'] = 'application/json'
        http = httplib.HTTPSConnection(self.get_hostname())
        http.request('PATCH', uri_path, json.dumps(folder), headers=headers)
        response = http.getresponse()

        print(response.status, response.reason)
        http.close()

    def delete_item(self, item_id):
        uri_path = '/sf/v3/Items({})'.format(item_id)
        print('DELETE {}{}'.format(self.get_hostname(), uri_path))
        http = httplib.HTTPSConnection(self.get_hostname())
        http.request('DELETE', uri_path, headers=self.get_authorization_header())
        response = http.getresponse()

        print(response.status, response.reason)
        http.close()

    def download_item(self, item_id, local_path):
        uri_path = '/sf/v3/Items({})/Download'.format(item_id)
        print('GET {}{}'.format(self.get_hostname(), uri_path))
        http = httplib.HTTPSConnection(self.get_hostname())
        http.request('GET', uri_path, headers=self.get_authorization_header())
        response = http.getresponse()
        location = response.getheader('location')
        redirect = None
        if location:
            redirect_uri = urlparse.urlparse(location)
            redirect = httplib.HTTPSConnection(redirect_uri.netloc)
            redirect.request('GET', '{}?{}'.format(redirect_uri.path, redirect_uri.query))
            response = redirect.getresponse()

        with open(local_path, 'wb') as target:
            b = response.read(1024 * 8)
            while b:
                target.write(b)
                b = response.read(1024 * 8)

        print(response.status, response.reason)
        http.close()
        if redirect:
            redirect.close()

    def upload_file(self, folder_id, local_path):
        uri_path = '/sf/v3/Items({})/Upload'.format(folder_id)
        print('GET {}{}'.format(self.get_hostname(), uri_path))
        http = httplib.HTTPSConnection(self.get_hostname())
        http.request('GET', uri_path, headers=self.get_authorization_header())

        response = http.getresponse()
        upload_config = json.loads(response.read())
        if 'ChunkUri' in upload_config:
            upload_response = self.multipart_form_post_upload(upload_config['ChunkUri'], local_path)
            print(upload_response.status, upload_response.reason)
        else:
            print('No Upload URL received')

    def multipart_form_post_upload(self, url, filepath):
        newline = b'\r\n'
        filename = os.path.basename(filepath)
        data = []
        headers = {}
        boundary = '----------{}'.format(int(time.time()))
        headers['content-type'] = 'multipart/form-data; boundary={}'.format(boundary)
        data.append('--{}'.format(boundary))
        data.append('Content-Disposition: form-data; name="{}"; filename="{}"'.format('File1', filename))
        data.append('Content-Type: {}'.format(self.get_content_type(filename)))
        data.append('')
        data.append(open(filepath, 'rb').read())
        data.append('--{}--'.format(boundary))
        data.append('')

        data_str = newline.join([item if isinstance(item, bytes) else bytes(item, 'utf-8') for item in data])
        headers['content-length'] = len(data_str)

        uri = urlparse.urlparse(url)
        http = httplib.HTTPSConnection(uri.netloc)
        http.putrequest('POST', '{}?{}'.format(uri.path, uri.query))
        for hdr_name, hdr_value in headers.items():
            http.putheader(hdr_name, hdr_value)
        http.endheaders()
        http.send(data_str)
        return http.getresponse()

    @staticmethod
    def get_content_type(filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def get_clients(self):
        uri_path = '/sf/v3/Accounts/GetClients'
        print('GET {}{}'.format(self.get_hostname(), uri_path))
        http = httplib.HTTPSConnection(self.get_hostname())
        http.request('GET', uri_path, headers=self.get_authorization_header())
        response = http.getresponse()

        print(response.status, response.reason)
        feed = json.loads(response.read())
        if 'value' in feed:
            for client in feed['value']:
                print(client['Id'], client['Email'])

    def create_client(self, email, firstname, lastname, company, clientpassword, canresetpassword, canviewmysettings):
        uri_path = '/sf/v3/Users'
        print('POST {}{}'.format(self.get_hostname(), uri_path))
        client = {'Email': email, 'FirstName': firstname, 'LastName': lastname, 'Company': company,
                  'Password': clientpassword,
                  'Preferences': {'CanResetPassword': canresetpassword, 'CanViewMySettings': canviewmysettings}}
        headers = self.get_authorization_header()
        headers['Content-type'] = 'application/json'
        http = httplib.HTTPSConnection(self.get_hostname())
        http.request('POST', uri_path, json.dumps(client), headers=headers)
        response = http.getresponse()

        print(response.status, response.reason)
        new_client = json.loads(response.read())
        print('Created Client {}'.format(new_client['Id']))

        http.close()
