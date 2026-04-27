import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# FMC connection details
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

def get_access_rules(token, domain_uuid, policy_id):
    """
    Retrieve all access rules for a specific access control policy with expanded=true.
    """
    url = f"https://{FMC_HOST}/api/fmc_config/v1/domain/{domain_uuid}/policy/accesspolicies/{policy_id}/accessrules?expanded=true"
    headers = {
        'X-auth-access-token': token,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def print_rule_logging(rule):
    """
    Nicely format and print logging settings of a single access rule.
    """
    print(f"Rule Name: {rule.get('name', 'N/A')}")
    print(f"  Rule ID: {rule.get('id', 'N/A')}")
    print(f"  Enabled: {rule.get('enabled', 'N/A')}")
    print(f"  Action: {rule.get('action', 'N/A')}")
    print(f"  Enable Syslog: {rule.get('enableSyslog', 'N/A')}")
    print(f"  Log Begin: {rule.get('logBegin', 'N/A')}")
    print(f"  Log End: {rule.get('logEnd', 'N/A')}")
    print(f"  Log Files: {rule.get('logFiles', 'N/A')}")

    snmp_config = rule.get('snmpConfig')
    if snmp_config:
        print("  SNMP Config:")
        print(f"    Name: {snmp_config.get('name', 'N/A')}")
        print(f"    ID: {snmp_config.get('id', 'N/A')}")
        print(f"    Type: {snmp_config.get('type', 'N/A')}")
    else:
        print("  SNMP Config: None")

    print("-" * 50)

def main():
    try:
        token, domain_uuid = get_auth_token()
        print(f"Obtained token and domain UUID: {domain_uuid}")

        policies_data = get_access_policies(token, domain_uuid)
        policies = policies_data.get('items', [])
        if not policies:
            print("No access control policies found.")
            return

        # List all ACPs with numbers
        print("Access Control Policies (ACPs) configured in FMC:")
        for idx, policy in enumerate(policies, start=1):
            print(f"{idx}. {policy.get('name', 'N/A')}")

        # Prompt user to select ACP by number
        while True:
            try:
                selection = int(input(f"Enter the number of the ACP to select (1-{len(policies)}): ").strip())
                if 1 <= selection <= len(policies):
                    break
                else:
                    print(f"Please enter a number between 1 and {len(policies)}.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        selected_policy = policies[selection - 1]
        acp_name = selected_policy.get('name')
        policy_id = selected_policy.get('id')

        print(f"Selected ACP: '{acp_name}' (ID: {policy_id})")
        print("Retrieving access rules and their logging settings...")

        rules_data = get_access_rules(token, domain_uuid, policy_id)
        rules = rules_data.get('items', [])
        if not rules:
            print("No access rules found for this ACP.")
            return

        for rule in rules:
            print_rule_logging(rule)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as ex:
        print(f"An error occurred: {ex}")

if __name__ == "__main__":
    main()
