import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# FMC connection details
FMC_HOST = "10.122.51.26"
USERNAME = "luis_api"
PASSWORD = "C1scoRocks!"

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

def get_access_policies(token, domain_uuid):
    """
    Retrieve all access control policies for the given domain UUID.
    """
    url = f"https://{FMC_HOST}/api/fmc_config/v1/domain/{domain_uuid}/policy/accesspolicies"
    headers = {
        'X-auth-access-token': token,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def get_logging_settings(token, domain_uuid, policy_id):
    """
    Retrieve logging settings for a specific access control policy with expanded=true.
    """
    url = f"https://{FMC_HOST}/api/fmc_config/v1/domain/{domain_uuid}/policy/accesspolicies/{policy_id}/loggingsettings?expanded=true"
    headers = {
        'X-auth-access-token': token,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def print_logging_settings(logging_data):
    """
    Nicely format and print logging settings details, including requested fields.
    """
    items = logging_data.get('items', [])
    if not items:
        print("  No logging settings found.")
        return

    for item in items:
        print("  Logging Setting ID:", item.get('id', 'N/A'))
        print("  Logging Type:", item.get('type', 'N/A'))

        # Print syslogConfigFromPlatformSetting, enableFileAndMalwareSyslog, enableipsSyslog
        print(f"  syslogConfigFromPlatformSetting: {item.get('syslogConfigFromPlatformSetting', 'N/A')}")
        print(f"  enableFileAndMalwareSyslog: {item.get('enableFileAndMalwareSyslog', 'N/A')}")
        print(f"  enableipsSyslog: {item.get('enableipsSyslog', 'N/A')}")

        # Print severityForPlatformSettingSyslogConfig
        print(f"  severityForPlatformSettingSyslogConfig: {item.get('severityForPlatformSettingSyslogConfig', 'N/A')}")

        # Print syslogConfig object details if present
        syslog_config = item.get('syslogConfig')
        if syslog_config:
            print("  syslogConfig:")
            print(f"    Name: {syslog_config.get('name', 'N/A')}")
            print(f"    ID: {syslog_config.get('id', 'N/A')}")
            print(f"    Type: {syslog_config.get('type', 'N/A')}")

        # Print syslog settings if present
        syslog_settings = item.get('syslogSettings')
        if syslog_settings:
            print("  Syslog Settings:")
            print(f"    Enabled: {syslog_settings.get('enabled', 'N/A')}")
            print(f"    Host: {syslog_settings.get('host', {}).get('name', 'N/A')}")
            print(f"    Port: {syslog_settings.get('port', 'N/A')}")
            print(f"    Protocol: {syslog_settings.get('protocol', 'N/A')}")

        # Print event logging settings if present
        event_logging = item.get('eventLogging')
        if event_logging:
            print("  Event Logging:")
            for key, value in event_logging.items():
                print(f"    {key}: {value}")

        print("-" * 40)

def main():
    try:
        token, domain_uuid = get_auth_token()
        print(f"Obtained token and domain UUID: {domain_uuid}")

        policies_data = get_access_policies(token, domain_uuid)
        policies = policies_data.get('items', [])
        print(f"Total access control policies retrieved: {len(policies)}")

        for policy in policies:
            policy_name = policy.get('name')
            policy_id = policy.get('id')
            print(f"Access Control Policy Name: {policy_name}, ID: {policy_id}")

            logging_data = get_logging_settings(token, domain_uuid, policy_id)
            print("Logging Settings:")
            print_logging_settings(logging_data)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as ex:
        print(f"An error occurred: {ex}")

if __name__ == "__main__":
    main()