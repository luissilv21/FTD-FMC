import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# FMC connection details - replace with your actual FMC IP, username, and password
FMC_HOST = "x.x.x.x"
USERNAME = "api"
PASSWORD = "your_password"

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

def get_backup_files(token, domain_uuid):
    """
    Retrieve backup files from FMC using the specified API endpoint with expanded=true.
    """
    url = f"https://{FMC_HOST}/api/fmc_config/v1/domain/{domain_uuid}/backup/files?expanded=true"
    headers = {
        'X-auth-access-token': token,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def main():
    try:
        token, domain_uuid = get_auth_token()
        backups_data = get_backup_files(token, domain_uuid)
        backups = backups_data.get('items', [])

        if not backups:
            print("No backup files found.")
            return

        print(f"Total backup files found: {len(backups)}")

        for idx, backup in enumerate(backups, start=1):
            print(f"Backup File #{idx}:")
            print(f"  Backup Version: {backup.get('backupVersion', 'N/A')}")
            print(f"  Target ID: {backup.get('targetId', 'N/A')}")
            print(f"  System Information: {backup.get('systemInformation', 'N/A')}")
            print(f"  File Name: {backup.get('fileName', 'N/A')}")
            print(f"  Size: {backup.get('size', 'N/A')}")
            print(f"  Creation Date: {backup.get('creationDate', 'N/A')}")
            print(f"  Type: {backup.get('type', 'N/A')}")
            print(f"  Download Link: {backup.get('downloadLink', 'N/A')}")
            print(f"  Is TID Enabled: {backup.get('isTidEnabled', 'N/A')}")
            print(f"  Is Events Enabled: {backup.get('isEventsEnabled', 'N/A')}")
            print(f"  Is Configurations Enabled: {backup.get('isConfigurationsEnabled', 'N/A')}")
            print(f"  Device Type: {backup.get('deviceType', 'N/A')}")
            print(f"  Location: {backup.get('location', 'N/A')}")
            print("-" * 50)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as ex:
        print(f"An error occurred: {ex}")

if __name__ == "__main__":
    main()
