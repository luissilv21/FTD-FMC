import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# FMC connection details - replace with your actual FMC IP, username, and password
FMC_HOST = "10.122.51.26"
USERNAME = "luis_api"  # Replace with your FMC username
PASSWORD = "C1scoRocks!"  # Replace with your FMC password

def get_auth_token():
    """
    Authenticate to FMC and obtain the X-auth-access-token and DOMAIN_UUID from response headers.
    """
    url = f"https://{FMC_HOST}/api/fmc_platform/v1/auth/generatetoken"
    response = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()
    token = response.headers.get('X-auth-access-token')
    domain_uuid = response.headers.get('DOMAIN_UUID')
    if not token or not domain_uuid:
        raise Exception("Failed to obtain auth token or domain UUID")
    return token, domain_uuid

def get_server_versions(token, domain_uuid):
    """
    Retrieve Snort 2 (sruVersion) and Snort 3 (lspVersion) versions,
    Vulnerability Database (vdbVersion), Geolocation Database (geoVersion),
    and URL Filter Database versions from FMC.
    """
    url = f"https://{FMC_HOST}/api/fmc_platform/v1/info/serverversion"
    headers = {
        'X-auth-access-token': token,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()
    if 'items' not in data or not data['items']:
        raise Exception("No version information found in response")
    version_info = data['items'][0]

    # Extract versions using specified keys
    snort2_version = version_info.get('sruVersion')  # Snort 2 rules version
    snort3_version = version_info.get('lspVersion')  # Snort 3 rules version
    vdb_version = version_info.get('vdbVersion')     # Vulnerability Database version
    geo_version = version_info.get('geoVersion')     # Geolocation Database version
    url_filter_version = version_info.get('urlFilterVersion')

    return {
        'snort2_version': snort2_version,
        'snort3_version': snort3_version,
        'vdb_version': vdb_version,
        'geo_version': geo_version,
        'url_filter_version': url_filter_version
    }

def main():
    try:
        token, domain_uuid = get_auth_token()
        print(f"Obtained token and domain UUID: {domain_uuid}")

        versions = get_server_versions(token, domain_uuid)

        print("Current Versions on FMC:")
        if versions['snort2_version']:
            print(f"  Snort 2 Version (sruVersion): {versions['snort2_version']}")
        else:
            print("  Snort 2 Version (sruVersion): Not available")

        if versions['snort3_version']:
            print(f"  Snort 3 Version (lspVersion): {versions['snort3_version']}")
        else:
            print("  Snort 3 Version (lspVersion): Not available")

        if versions['vdb_version']:
            print(f"  Vulnerability Database Version (vdbVersion): {versions['vdb_version']}")
        else:
            print("  Vulnerability Database Version (vdbVersion): Not available")

        if versions['geo_version']:
            print(f"  Geolocation Database Version (geoVersion): {versions['geo_version']}")
        else:
            print("  Geolocation Database Version (geoVersion): Not available")

        if versions['url_filter_version']:
            print(f"  URL Filter Database Version: {versions['url_filter_version']}")
        else:
            print("  URL Filter Database Version: Not available")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as ex:
        print(f"An error occurred: {ex}")

if __name__ == "__main__":
    main()