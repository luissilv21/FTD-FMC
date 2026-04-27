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

def get_ntp_servers(token, domain_uuid):
    """
    Retrieve the NTP server objects from FMC for the given domain UUID.
    """
    url = f"https://{FMC_HOST}/api/fmc_config/v1/domain/{domain_uuid}/object/ntpservers"
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
        print(f"Obtained token and domain UUID: {domain_uuid}")

        ntp_servers_data = get_ntp_servers(token, domain_uuid)
        ntp_servers = ntp_servers_data.get('items', [])
        print(f"Total NTP servers retrieved: {len(ntp_servers)}")

        if not ntp_servers:
            print("No NTP servers configured.")
        else:
            for server in ntp_servers:
                name = server.get('name', 'N/A')
                server_id = server.get('id', 'N/A')
                ip_address = server.get('value', 'N/A')
                description = server.get('description', '')
                print(f"NTP Server Name: {name}")
                print(f"  ID: {server_id}")
                print(f"  IP Address: {ip_address}")
                if description:
                    print(f"  Description: {description}")
                print("")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as ex:
        print(f"An error occurred: {ex}")

if __name__ == "__main__":
    main()