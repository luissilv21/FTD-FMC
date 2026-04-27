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

def get_platform_settings_policies(token, domain_uuid):
    """
    Retrieve all platform settings policies for the given domain UUID.
    """
    url = f"https://{FMC_HOST}/api/fmc_config/v1/domain/{domain_uuid}/policy/ftdplatformsettingspolicies?expanded=true"
    headers = {
        'X-auth-access-token': token,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def get_ntp_settings_expanded(token, domain_uuid, policy_id):
    """
    Retrieve the expanded NTP settings for a specific platform settings policy,
    which includes ntpServerInfos with configured NTP server IPs.
    """
    url = f"https://{FMC_HOST}/api/fmc_config/v1/domain/{domain_uuid}/policy/ftdplatformsettingspolicies/{policy_id}/ntpsettings?expanded=true"
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

        policies_data = get_platform_settings_policies(token, domain_uuid)
        policies = policies_data.get('items', [])
        print(f"Total platform settings policies retrieved: {len(policies)}")

        for policy in policies:
            policy_name = policy.get('name')
            policy_id = policy.get('id')
            print(f"Policy Name: {policy_name}, ID: {policy_id}")

            ntp_data = get_ntp_settings_expanded(token, domain_uuid, policy_id)
            ntp_items = ntp_data.get('items', [])

            if not ntp_items:
                print("  No NTP settings found for this policy.")
                continue

            for ntp in ntp_items:
                ntp_id = ntp.get('id')
                print(f"  NTP Setting ID: {ntp_id}")

                # Extract NTP mode if available
                ntp_mode = ntp.get('ntpMode')
                if ntp_mode:
                    # Explicitly display when mode is SYNC_VIA_NTP_SERVER
                    if ntp_mode == "SYNC_VIA_NTP_SERVER":
                        print(f"  NTP Mode: {ntp_mode} (NTP servers are configured)")
                    else:
                        print(f"  NTP Mode: {ntp_mode}")

                # Extract configured NTP server IPs if present
                ntp_servers = ntp.get('ntpServerInfos', [])
                if not ntp_servers:
                    print("  No NTP servers configured.")
                else:
                    print("  Configured NTP Servers:")
                    for server_ip in ntp_servers:
                        print(f"    - {server_ip}")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as ex:
        print(f"An error occurred: {ex}")

if __name__ == "__main__":
    main()
