import sys
import getopt
import requests
import os
import zipfile
import occ_properties


def usage():
    print(__doc__)
    sys.exit(2)

# Get authorization token for future use

def login(url, app_key):
    "Submit application key to login endpoint and receive authorization token"

    # Authorization parameter for grant type. Should be set to client_credentials
    payload = 'grant_type=client_credentials'
    payload = payload.encode('utf-8')  # data should be bytes

    # OAuth token should be set in Authorization header using value: Bearer <auth_token>
    headers = {'Authorization': 'Bearer ' + app_key,
               'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post(url, data=payload, headers=headers)
    """ Set access token from JSON response. 
	Sample response:
	{
	token_type: "bearer"
	access_token: "[token]"
	}	
	"""
    print(r.text)
    return r.json()['access_token']


# Get authorization token for future use
def login_admin(url, admin_name_pwd):
    "Submit application key to login endpoint and receive authorization token"

    # Authorization parameter for grant type. Should be set to client_credentials
    payload = 'grant_type=password&' + admin_name_pwd
    payload = payload.encode('utf-8')  # data should be bytes

    # OAuth token should be set in Authorization header using value: Bearer <auth_token>
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post(url, data=payload, headers=headers)
    """ Set access token from JSON response. 
	Sample response:
	{
	token_type: "bearer"
	access_token: "[token]"
	}	
	"""
    print(r.text)
    return r.json()['access_token']


# Perform logout operation
def logout(url, token):
    "Perform logout operation"

    # OAuth token should be set in Authorization header using value: Bearer <auth_token>
    headers = {'content-type': 'application/json',
               'Authorization': 'Bearer ' + token}

    r = requests.post(url, headers=headers)
    """ 
	Sample response:
	result 	boolean 	true - logout was success full, false - it failed.
	{
	  "result": true
	}
	"""
    if (r.status_code == requests.codes.ok):
        return r.json()['result']

# Get JSON response from URL endpoint


def get(url, token, params):
    "Get JSON response from URL endpoint"

    # Auth token should be set in Authorization header using value: Bearer <auth_token>
    headers = {'Authorization': 'Bearer ' + token}

    r = requests.get(url, params=params, headers=headers)
    print(r.text)
    return r.json()

# Post data to URL endpoint


def post(url, token, payload):
    "Post data to URL endpoint"

    # Auth token should be set in Authorization header using value: Bearer <auth_token>
    header = {'content-type': 'application/json',
              'Authorization': 'Bearer ' + token}

    r = requests.post(url, data=json.dumps(payload), headers=header)
    print(r.text)
    return r.json()

# Post data to URL endpoint


def post_file(url, token, payload):
    "Post data to URL endpoint"

    # Auth token should be set in Authorization header using value: Bearer <auth_token>
    header = {'Authorization': 'Bearer ' + token}

    r = requests.post(url, files=payload, headers=header)
    print(r.text)
    return str(r.json()['token'])


# Archive contents of specified directory
def zipdir(path, ziph):
    # ziph is zipfile handle
    lenDirPath = len(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            #print ("archiving file %s" % (file)	)
            filePath = os.path.join(root, file)
            ziph.write(filePath, filePath[lenDirPath:])


def get_extension_logs(host, app_key, level):

    print('START get logs')

    # Login using /ccadminui endpoint, must pass in name/pwd
    login_url = occ_properties.oauth_login_admin_url.format(root_url=host)
    print('Get login auth from: ' + login_url)
    token = login(login_url, app_key)
    print('Login success!')

    extension_logs_url = occ_properties.extension_logs_url.format(
        root_url=host)
    print('Get logs from: ' + extension_logs_url)
    result = get(extension_logs_url, token, {"loggingLevel": level})

    print('Log file: ' + result['filename'])
    # Save to file
    with open(result['filename'], 'w') as f:
        f.write(result['fileContents'])

    #print (result)

    # Logout
    logout_url = occ_properties.oauth_logout_url.format(root_url=host)
    if logout(logout_url, token):
        print('Logout success!')

    print('END get logs')


def main(argv):

    # Set default url & response header values
    host, app_key, level = ('', '', 'error')

    try:
        opts, args = getopt.getopt(argv, "hu:k:l:", ["host", "key", "level"])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt == '-h':
            usage()
        elif opt in ("-l", "--level"):
            level = arg
        elif opt in ("-u", "--host"):
            host = arg
        elif opt in ("-k", "--key"):
            app_key = arg

    print('*** Host = ', host, '; Id = ', app_key,
          '; Logging Level = ', level, " ***")

    if not host or not app_key:
        usage()
    get_extension_logs(host, app_key, level)

    print("Done!")


if __name__ == "__main__":
    main(sys.argv[1:])