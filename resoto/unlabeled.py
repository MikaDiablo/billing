# Definitions of searching unlabeled resources
import pandas as pd
import os

# Dump the list to  json file
def dump_data_json(filename, data):
    df = pd.DataFrame(data)

    if not os.path.exists("/tmp/unlabeled"): # gcp functions only permit directory in /tmp
        os.makedirs("/tmp/unlabeled")

    df.to_json(os.path.join("/tmp/unlabeled", f'{filename}.json'), orient='index')

# Searching for resources with Resoto
def search_cli(client, kind):
    result = client.cli_execute(f"search is({kind}) and tags.env == null | format")
    return result

# Searching for a successor for a specific resource
def search_successors_cli(client, kind, id):
    result = client.cli_execute(f"search is({kind}) and id = '{id}' | successors | format")
    return result

# Get infos about the unlabeled forwarding_rule_unlabeled
def forwarding_rule_unlabeled(client):
    # Initialize empty lists to store data
    ids = []
    ip_addresses = []
    instances = []
    FRs = search_cli(client, 'gcp_forwarding_rule')
    # Loop through FRs
    for fr in FRs:
        for object, _ in fr.items():
            if object == "reported":
                target_pool = search_successors_cli(client, 'gcp_forwarding_rule', fr[object]['id'])
                for target in target_pool:
                    for instance, value in target.items():
                        if instance == "reported":
                            # Append data to lists
                            ids.append(fr[object]['id'])
                            ip_addresses.append(fr[object]['ip_address'])
                            # Check if instances_value is an error, if yes, append an empty string
                            try:
                                instances_value = target[instance]['instances']
                            except KeyError:
                                instances_value = ''
                            instances.append(instances_value)
    return dump_data_json('forwarding_rule',{'id': ids, 'ip_address': ip_addresses, 'instances': instances})

# Get infos about the unlabeled buckets
def buckets_unlabeled(client):
    buckets = []
    project = []
    result = search_cli(client, 'gcp_bucket')
    for bucket in result:
        for object, _ in bucket.items():
            if object == "reported":
                buckets.append(bucket[object]['name'])
            if object == "ancestors":
                project.append(bucket[object]['account']['reported']['name'])
    return dump_data_json('buckets',{'Name': buckets, 'Project': project})

# Get infos about the unlabeled disk
def disk_unlabeled(client):
    volumes = []
    users = []
    size = []
    project = []
    result = search_cli(client, 'volume')
    for volume in result:
        for object, _ in volume.items():
            if object == "reported":
                volumes.append(volume[object]['name'])
                users.append(volume[object]['users'])
                size.append(volume[object]['size_gb'])
            if object == "ancestors":
                project.append(volume[object]['account']['reported']['name'])    
    return dump_data_json('volumes',{'Name': volumes, 'users': users, 'Size': size, 'Project': project}) 

# Get infos about the unlabeled ip
def ip_unlabeled(client):
    ips = []
    users = []
    address = []
    result = search_cli(client, 'gcp_address')
    for ip in result:
        for object, _ in ip.items():
            if object == "reported":
                ips.append(ip[object]['name'])
                users.append(ip[object]['users'])
                address.append(ip[object]['address'])
    return dump_data_json('ips',{'Name': ips, 'users': users, 'address': address})

# Get infos about the unlabeled instance
def instance_unlabeled(client):
    instances = []
    cpus = []
    ram = []
    project = []
    result = search_cli(client, 'instance')
    for instance in result:
        for object, _ in instance.items():
            if object == "reported":
                instances.append(instance[object]['name'])
                cpus.append(instance[object]['instance_cores'])
                ram.append(instance[object]['instance_memory'])
            if object == "ancestors":
                project.append(instance[object]['account']['reported']['name'])    
    return dump_data_json('instances',{'Name': instances, 'CPUs': cpus, 'RAM': ram, 'Project': project})