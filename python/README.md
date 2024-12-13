This Python script is used to migrate Azure Data Explorer (ADX) from a virtual network injection to a private endpoint based security.

## Setup

Before running the script, you need to install the required Python packages. You can do this by running the following command in your terminal:

```bash
pip install azure-identity azure-mgmt-kusto
```

## Configuration

The script uses a configuration file named `config.json` to get the list of clusters and the desired state of the virtual network. The configuration file should have the following structure:

```json
{
    "clusters": [
        {
            "subscription_id": "<subscription-id-1>",
            "resource_group_name": "<resource-group-name-1>",
            "cluster_name": "<cluster-name-1>",
            "vnet_state": "disabled"
        },
        {
            "subscription_id": "<subscription-id-2>",
            "resource_group_name": "<resource-group-name-2>",
            "cluster_name": "<cluster-name-2>",
            "vnet_state": "disabled",
            "allowed_ips": ["1.1.1.1", "2.2.2.2"]
        }
        // Add more clusters as needed
    ]
}
```

Replace `<subscription-id>`, `<resource-group-name>`, and `<cluster-name>` with your actual Azure subscription ID, resource group name, and cluster name respectively. You can add as many clusters as you want to the `clusters` array.

The `vnet_state` field should be set to either `enabled` or `disabled` depending on whether you want to enable or disable the virtual network.

The `allowed_ips` field can be configured to the list of CIDRs which are allowed to connect to the ADX cluster.

## Usage

After setting up the configuration file, you can run the script from the terminal with the following command:

```bash
python migrateADXclusters.py
```
## Output

Once the script is started, it will print the status of each migration operation. Here is an example of what the output might look like:

```bash
Starting migration for cluster: cluster-name-1
Migration status for cluster-name-1: InProgress
Migration status for cluster-name-1: InProgress
Migration status for cluster-name-1: Succeeded
```
