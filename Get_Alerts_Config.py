import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# FMC connection details
FMC_HOST = "x.x.x.x"
USERNAME = "api"
PASSWORD = "your_password"

# Use the provided domain UUID
DOMAIN_UUID = "e276abec-e0f2-11e3-8169-6d9ed49b625f"

def get_auth_token():
    """
    Authenticate to FMC and obtain the X-auth-access-token from response headers.
    """
    url = f"https://{FMC_HOST}/api/fmc_platform/v1/auth/generatetoken"
    response = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()
    token = response.headers.get('X-auth-access-token')
    if not token:
        raise Exception("Failed to obtain auth token")
    return token

def get_snmp_alerts(token):
    """
    Retrieve SNMP alerts configuration using the specified API endpoint with expanded=true.
    """
    url = f"https://{FMC_HOST}/api/fmc_config/v1/domain/{DOMAIN_UUID}/policy/snmpalerts?expanded=true"
    headers = {
        'X-auth-access-token': token,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def get_syslog_alerts(token):
    """
    Retrieve Syslog alerts configuration using the specified API endpoint with expanded=true.
    """
    url = f"https://{FMC_HOST}/api/fmc_config/v1/domain/{DOMAIN_UUID}/policy/syslogalerts?expanded=true"
    headers = {
        'X-auth-access-token': token,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def main():
    try:
        token = get_auth_token()

        snmp_alerts_data = get_snmp_alerts(token)
        snmp_alerts = snmp_alerts_data.get('items', [])
        if snmp_alerts:
            print(f"Total SNMP alerts found: {len(snmp_alerts)}")
            for idx, alert in enumerate(snmp_alerts, start=1):
                # Extract fields with fallback to 'N/A' if missing
                print(f"SNMP Alert #{idx}:")
                print("{")
                print(f'  "server": "{alert.get("server", "N/A")}",')
                print(f'  "userName": "{alert.get("userName", "N/A")}",')
                print(f'  "privProtocol": "{alert.get("privProtocol", "N/A")}",')
                print(f'  "authProtocol": "{alert.get("authProtocol", "N/A")}",')
                print(f'  "name": "{alert.get("name", "N/A")}",')
                print(f'  "id": "{alert.get("id", "N/A")}",')
                print(f'  "type": "{alert.get("type", "N/A")}",')
                print(f'  "version": "{alert.get("version", "N/A")}"')
                print("}")
                print("-" * 50)
        else:
            print("No SNMP alerts configuration found.")

        syslog_alerts_data = get_syslog_alerts(token)
        syslog_alerts = syslog_alerts_data.get('items', [])
        if syslog_alerts:
            print(f"Total Syslog alerts found: {len(syslog_alerts)}")
            for idx, alert in enumerate(syslog_alerts, start=1):
                print(f"Syslog Alert #{idx}:")
                print("{")
                print(f'  "host": "{alert.get("host", "N/A")}",')
                print(f'  "facility": "{alert.get("facility", "N/A")}",')
                print(f'  "port": {alert.get("port", "N/A")},')
                print(f'  "severity": "{alert.get("severity", "N/A")}",')
                print(f'  "name": "{alert.get("name", "N/A")}",')
                print(f'  "id": "{alert.get("id", "N/A")}",')
                print(f'  "type": "{alert.get("type", "N/A")}"')
                print("}")
                print("-" * 50)
        else:
            print("No Syslog alerts configuration found.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as ex:
        print(f"An error occurred: {ex}")

if __name__ == "__main__":
    main()
