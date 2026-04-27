import requests
import csv
import sys

# Constants for prompt integrity
CONSTANTS = {
    FMC_HOST = "x.x.x.x"
    USERNAME = "api"
    PASSWORD = "your_password",
}
API_VERSION = 'v1'
BASE_URL = f'https://{CONSTANTS["FMC_IP"]}/api/fmc_config/{API_VERSION}/domain'

# All possible FMC object types (from your list)
OBJECT_TYPES = [
    'hosts', 'networks', 'ranges', 'fqdn', 'networkgroups', 'ipv4addresspools', 'ipv4prefixlists',
    'ipv6addresspools', 'ipv6prefixlists', 'macaddresspools', 'dynamicobjects', 'dynamicobjectmappings',
    'protocolportobjects', 'portobjectgroups', 'ports', 'anyprotocolportobjects', 'extendedaccesslists',
    'standardaccesslists', 'standardcommunitylists', 'extendedcommunitylists', 'expandedcommunitylists',
    'communitylists', 'urls', 'urlgroups', 'urlcategories', 'customsiurllists', 'customsiurllistdownload',
    'siurlfeeds', 'siurllists', 'sinetworkfeeds', 'sinetworklists', 'sidnsfeeds', 'sidnslists',
    'continents', 'countries', 'geolocations', 'timeranges', 'timezoneobjects', 'globaltimezones',
    'realms', 'realmusers', 'realmusergroups', 'localrealmusers', 'azureadrealms', 'azureadstatuses',
    'samlrealmusersandgroups', 'securitygrouptags', 'isesecuritygrouptags', 'certenrollments',
    'internalcas', 'internalcertificates', 'internalcertgroups', 'externalcertificates',
    'externalcertificategroups', 'externalcacertificates', 'externalcacertificategroups',
    'certificatemaps', 'grouppolicies', 'intrusionrules', 'intrusionrulegroups', 'filecategories',
    'filetypes', 'applicationcategories', 'applicationfilters', 'applicationproductivities',
    'applicationrisks', 'applications', 'applicationtags', 'applicationtypes', 'dhcpipv6pools',
    'ntpservers', 'dnsservergroups', 'ikev1ipsecproposals', 'ikev1policies', 'ikev2ipsecproposals',
    'ikev2policies', 'interfaceobjects', 'interfacegroups', 'securityzones', 'radiusservergroups',
    'vlantags', 'vlangrouptags', 'aspathlists', 'bfdtemplates', 'distinguishednames',
    'distinguishednamegroups', 'endpointdevicetypes', 'hostscanpackages', 'keychains', 'operational',
    'policylists', 'privateresources', 'privateresourcegroups', 'resourceprofiles', 'routemaps',
    'secureclientcustomizations', 'serviceaccessobjects', 'sinkholes', 'slamonitors', 'ssoservers',
    'variables', 'variablesets', 'tunneltags', 'icmpv4objects', 'icmpv6objects'
]

def get_auth_token():
    url = f'https://{CONSTANTS["FMC_IP"]}/api/fmc_platform/v1/auth/generatetoken'
    try:
        r = requests.post(url, auth=(CONSTANTS["USERNAME"], CONSTANTS["PASSWORD"]), verify=False)
        r.raise_for_status()
    except Exception as e:
        print(f'Failed to get auth token: {e}')
        sys.exit(1)
    headers = r.headers
    return headers['X-auth-access-token'], headers['DOMAIN_UUID']

def get_objects(token, domain_uuid, obj_type):
    url = f'{BASE_URL}/{domain_uuid}/object/{obj_type}?limit=1000'
    all_items = []
    headers = {'X-auth-access-token': token}
    while url:
        r = requests.get(url, headers=headers, verify=False)
        if r.status_code != 200:
            print(f"Failed to fetch {obj_type}: {r.status_code} {r.text}")
            break
        data = r.json()
        items = data.get('items', [])
        all_items.extend(items)
        url = data.get('next', None)
    return all_items

def get_fqdns_from_networkaddresses(token, domain_uuid):
    url = f'{BASE_URL}/{domain_uuid}/object/networkaddresses?filter=type%3AFQDN&limit=1000'
    all_items = []
    headers = {'X-auth-access-token': token}
    while url:
        r = requests.get(url, headers=headers, verify=False)
        if r.status_code != 200:
            print(f"Failed to fetch explicit FQDNs: {r.status_code} {r.text}")
            break
        data = r.json()
        items = data.get('items', [])
        all_items.extend(items)
        url = data.get('next', None)
    return all_items

def flatten(item):
    flat = {}
    for k, v in item.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                flat[f"{k}_{kk}"] = vv
        else:
            flat[k] = v
    return flat

def main():
    requests.packages.urllib3.disable_warnings()
    token, domain_uuid = get_auth_token()
    all_objs = []

    # Retrieve all objects for all types in OBJECT_TYPES
    for obj_type in OBJECT_TYPES:
        print(f"Fetching {obj_type}...")
        objs = get_objects(token, domain_uuid, obj_type)
        for obj in objs:
            flat = flatten(obj)
            flat['object_type'] = obj_type
            all_objs.append(flat)

    # Explicitly retrieve FQDNs via networkaddresses filter (to ensure completeness)
    print("Fetching explicit FQDNs from networkaddresses...")
    fqdns = get_fqdns_from_networkaddresses(token, domain_uuid)
    for fqdn in fqdns:
        flat = flatten(fqdn)
        flat['object_type'] = 'fqdn_networkaddresses'
        all_objs.append(flat)

    # Get all fieldnames for CSV
    fieldnames = set()
    for obj in all_objs:
        fieldnames.update(obj.keys())
    fieldnames = sorted(list(fieldnames))

    # Write to CSV
    with open('fmc_all_objects.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for obj in all_objs:
            writer.writerow(obj)
    print("All FMC objects (including explicit FQDNs) saved to fmc_all_objects.csv")

if __name__ == '__main__':
    main()
