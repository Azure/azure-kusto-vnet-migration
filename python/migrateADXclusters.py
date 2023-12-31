from azure.identity import DefaultAzureCredential
from azure.mgmt.kusto import KustoManagementClient
from azure.mgmt.kusto.models import ClusterUpdate, VnetState, VirtualNetworkConfiguration
import json
import time

# Load the configuration from a JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

CLUSTERS = config['clusters']
if config['vnet_state'] == 'enabled':
    VNET_STATE = VnetState.ENABLED
else:
    VNET_STATE = VnetState.DISABLED

# Authenticate with Azure using interactive authentication
credential = DefaultAzureCredential()

def MigrateCluster(VNET_STATE, credential, cluster):
    kusto_client = KustoManagementClient(credential, cluster["subscription_id"])

    # Get the cluster config
    clusterConfig = kusto_client.clusters.get(
        resource_group_name=cluster["resource_group_name"],
        cluster_name=cluster["cluster_name"]
    )

    clusterConfig.virtual_network_configuration.state=VNET_STATE

    # Create a ClusterUpdate object with the desired changes
    cluster_update = ClusterUpdate.from_dict(clusterConfig.as_dict())

    print(f"Starting migration of {cluster['cluster_name']}")

    # Update the Kusto cluster
    poller = kusto_client.clusters.begin_update(
        resource_group_name=cluster["resource_group_name"],
        cluster_name=cluster["cluster_name"],
        parameters=cluster_update
    )
    
    return poller

# Start the migration of all clusters
allpoller = {}
for cluster in CLUSTERS:
    poller = MigrateCluster(VNET_STATE, credential, cluster)
    allpoller[cluster["cluster_name"]] = poller

# Wait for the migration to complete
workTodo = True
while workTodo:
    workTodo = False
    for clusterName, poller in allpoller.items():
        
        if(poller.done()):
            continue

        workTodo = True
        print(f"Migrating {clusterName}... Status: {poller.status()}")

        time.sleep(1)
    
    if workTodo:
        time.sleep(30)

# Check the status of the migration
for clusterName, poller in allpoller.items():
    poller_result = poller.result()
    if poller_result.provisioning_state == "Failed":
        print(f"Error while migrating {clusterName}... Status: {poller.status()}")
        print(f"Error details: {poller_result.error}")
    
    else:
        print(f"Migration of {clusterName} completed. Status: {poller.status()}")

print("Done!")