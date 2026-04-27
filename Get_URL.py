import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Disable warnings for self-signed certificates (if applicable)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FMC_HOST = "x.x.x.x"
USERNAME = "api"
PASSWORD = "your_password"
ACCESS_POLICY_NAME = "Test-ACP"

# Base URLs for platform and config APIs
BASE_URL_PLATFORM = f"https://{FMC_IP}/api/fmc_platform/v1"
BASE_URL_CONFIG = f"https://{FMC_IP}/api/fmc_config/v1"

def get_auth_token():
    url = f"{BASE_URL_PLATFORM}/auth/generatetoken"
    response = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()
    token = response.headers.get('X-auth-access-token')
    domain_uuid = response.headers.get('DOMAIN_UUID')
    if not token or not domain_uuid:
        raise Exception("Failed to obtain token or domain UUID")
    return token, domain_uuid

def get_access_policy_uuid(token, domain_uuid, policy_name):
    url = f"{BASE_URL_CONFIG}/domain/{domain_uuid}/policy/accesspolicies"
    headers = {'X-auth-access-token': token}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    policies = response.json().get('items', [])
    for policy in policies:
        if policy.get('name') == policy_name:
            return policy.get('id')
    raise Exception(f"Access Control Policy '{policy_name}' not found")

def get_access_rule_uuids(token, domain_uuid, policy_uuid):
    url = f"{BASE_URL_CONFIG}/domain/{domain_uuid}/policy/accesspolicies/{policy_uuid}/accessrules"
    headers = {'X-auth-access-token': token}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    rules = response.json().get('items', [])
    return [rule.get('id') for rule in rules]

def get_rule_details(token, domain_uuid, policy_uuid, rule_uuid):
    url = f"{BASE_URL_CONFIG}/domain/{domain_uuid}/policy/accesspolicies/{policy_uuid}/accessrules/{rule_uuid}"
    headers = {'X-auth-access-token': token}
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def main():
    token, domain_uuid = get_auth_token()
    print(f"Obtained token and domain UUID: {domain_uuid}")

    policy_uuid = get_access_policy_uuid(token, domain_uuid, ACCESS_POLICY_NAME)
    print(f"Access Control Policy UUID for '{ACCESS_POLICY_NAME}': {policy_uuid}")

    rule_uuids = get_access_rule_uuids(token, domain_uuid, policy_uuid)
    print(f"Total rules retrieved: {len(rule_uuids)}")

    found_rules = []
    for rule_uuid in rule_uuids:
        rule = get_rule_details(token, domain_uuid, policy_uuid, rule_uuid)
        urls = rule.get('urls', {})
        url_categories = urls.get('urlCategoriesWithReputation', [])
        if url_categories:
            found_rules.append({
                'name': rule.get('name'),
                'id': rule_uuid,
                'urlCategoriesWithReputation': url_categories
            })

    if found_rules:
        print(f"Rules with UrlCategoryAndReputation information found:")
        for r in found_rules:
            print(f"- Rule Name: {r['name']}, ID: {r['id']}")
            for cat in r['urlCategoriesWithReputation']:
                category = cat.get('category', {})
                print(f"  Category Name: {category.get('name')}, Reputation: {cat.get('reputation')}")
    else:
        print("No rules with UrlCategoryAndReputation information found.")

if __name__ == "__main__":
    main()
