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

def get_snmp_settings(token, domain_uuid, policy_id):
    """
    Retrieve SNMP settings for a specific platform settings policy with expanded=true.
    """
    url = f"https://{FMC_HOST}/api/fmc_config/v1/domain/{domain_uuid}/policy/ftdplatformsettingspolicies/{policy_id}/snmpsettings?expanded=true"
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

            snmp_data = get_snmp_settings(token, domain_uuid, policy_id)
            snmp_items = snmp_data.get('items', [])

            if not snmp_items:
                print("  No SNMP settings found for this policy.")
                continue

            for snmp in snmp_items:
                snmp_id = snmp.get('id')
                print(f"  SNMP Setting ID: {snmp_id}")

                # Enable SNMP servers flag
                enable_snmp_servers = snmp.get('enableSNMPServers')
                print(f"  Enable SNMP Servers: {enable_snmp_servers}")

                # SNMP port
                port = snmp.get('port')
                print(f"  SNMP Port: {port}")

                # SNMP Management Hosts
                snmp_mgmt_hosts = snmp.get('snmpMgmtHosts', [])
                if snmp_mgmt_hosts:
                    print("  SNMP Management Hosts:")
                    for host in snmp_mgmt_hosts:
                        ip_info = host.get('ipAddress', {})
                        ip_name = ip_info.get('name')
                        snmp_version = host.get('snmpVersion')
                        community_string = host.get('communityString')
                        poll = host.get('poll')
                        trap = host.get('trap')
                        host_port = host.get('port')
                        if_snmp_host_mgmt = host.get('ifSnmpHostMgmt')
                        interfaces = host.get('interfaces', {}).get('objects', [])

                        print(f"    - IP Address: {ip_name}")
                        print(f"      SNMP Version: {snmp_version}")
                        print(f"      Community String: {community_string}")
                        print(f"      Poll: {poll}")
                        print(f"      Trap: {trap}")
                        print(f"      Port: {host_port}")
                        print(f"      If SNMP Host Management: {if_snmp_host_mgmt}")
                        if interfaces:
                            print(f"      Interfaces:")
                            for interface in interfaces:
                                iface_name = interface.get('name')
                                iface_id = interface.get('id')
                                iface_type = interface.get('type')
                                print(f"        * Name: {iface_name}, ID: {iface_id}, Type: {iface_type}")
                        else:
                            print("      No interfaces configured.")
                else:
                    print("  No SNMP Management Hosts configured.")

                # SNMP Trap settings
                snmp_trap = snmp.get('snmpTrap', {})
                if snmp_trap:
                    print("  SNMP Trap Settings:")
                    for key, value in snmp_trap.items():
                        print(f"    {key}: {value}")
                else:
                    print("  No SNMP Trap settings configured.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as ex:
        print(f"An error occurred: {ex}")

if __name__ == "__main__":
    main()