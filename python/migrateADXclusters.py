from azure.identity import DefaultAzureCredential
from azure.mgmt.kusto import KustoManagementClient
from azure.mgmt.kusto.models import ClusterUpdate, VnetState, VirtualNetworkConfiguration
import json
import time

# Load the configuration from a JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

CLUSTERS = config['clusters']

# Authenticate with Azure using interactive authentication
credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)

def MigrateCluster(credential, cluster):
    kusto_client = KustoManagementClient(credential, cluster['subscription_id'])

	# Get the current VNET state
    state = 'Disabled'
    if cluster['vnet_state'].lower() == 'enabled':
        state = 'Enabled'
	
    # Get the cluster config
    clusterConfig = kusto_client.clusters.get(
        resource_group_name=cluster['resource_group_name'],
        cluster_name=cluster['cluster_name']
    )

    clusterConfig.virtual_network_configuration.state=state
    if 'allowed_ips' in cluster and state == VnetState.DISABLED:
        clusterConfig.allowed_ip_range_list = cluster['allowed_ips']

    # Create a ClusterUpdate object with the desired changes
    cluster_update = ClusterUpdate.from_dict(clusterConfig.as_dict())

    print(f"Starting migration of {cluster['cluster_name']}")

    # Update the Kusto cluster
    poller = kusto_client.clusters.begin_update(
        resource_group_name=cluster['resource_group_name'],
        cluster_name=cluster['cluster_name'],
        parameters=cluster_update
    )
    
    return poller

# Start the migration of all clusters
allpoller = {}
for cluster in CLUSTERS:
    poller = MigrateCluster(credential, cluster)
    allpoller[cluster['cluster_name']] = poller

# Wait for the migration to complete
workTodo = True
while workTodo:
    workTodo = False
    for clusterName, poller in allpoller.items():
        
        if(poller.done()):
            print(f"Migration of {clusterName} completed. Status: {poller.status()}")
            continue

        workTodo = True
        print(f"Migrating {clusterName}... Status: {poller.status()}")

        time.sleep(5)
    
    if workTodo:
        time.sleep(60)

# Check the status of the migration
for clusterName, poller in allpoller.items():
	try:
		poller_result = poller.result()
		if poller_result.provisioning_state == "Failed":
			print(f"Error while migrating {clusterName}... Status: {poller.status()}")
			print(f"Error details: {poller_result.error}")
		else:
			print(f"Migration of {clusterName} completed. Status: {poller.status()}")
	except Exception as e:
		print(f"Exception occurred while migrating {clusterName}: {str(e)}")

print("Done!")