import os
# Import the 'os' module to access environment variables stored in the .env file.

from azure.identity import DefaultAzureCredential
# Import DefaultAzureCredential for authentication with Azure services.

from azure.mgmt.compute import ComputeManagementClient
# Import ComputeManagementClient to manage Azure Compute resources.

def azure_cleanup_snapshots():
    # Define a function to clean up unused Azure snapshots.

    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    # Retrieve the Azure subscription ID from environment variables.

    credential = DefaultAzureCredential()
    # Use DefaultAzureCredential to authenticate with Azure services.

    compute_client = ComputeManagementClient(credential, subscription_id)
    # Create a ComputeManagementClient instance to interact with Azure Compute resources.

    snapshots = compute_client.snapshots.list()
    # List all snapshots available in the Azure subscription.

    for snapshot in snapshots:
        # Iterate through each snapshot in the subscription.

        snapshot_id = snapshot.id
        # Get the unique identifier for the snapshot.

        managed_disk_id = snapshot.managed_disk.id if snapshot.managed_disk else None
        # Check if the snapshot is associated with a Managed Disk. If not, set managed_disk_id to None.

        if not managed_disk_id:
            # If the snapshot is not linked to a Managed Disk:

            compute_client.snapshots.begin_delete(snapshot.id.split('/')[4], snapshot.name)
            # Delete the snapshot using its resource group (extracted from ID) and name.

            print(f"Deleted snapshot {snapshot.name} as it was not attached to any Managed Disk.")
            # Log a message to the console indicating that the snapshot was deleted.

            with open('/app/logs/cleanup_log.txt', 'a') as log_file:
                # Open the cleanup log file in append mode.

                log_file.write(f"Deleted snapshot {snapshot.name} as it was not attached to any Managed Disk.\n")
                # Write the snapshot deletion details into the log file.

        else:
            try:
                # If the snapshot is associated with a Managed Disk, perform further checks:

                disk = compute_client.disks.get(managed_disk_id.split('/')[4], managed_disk_id.split('/')[-1])
                # Retrieve the Managed Disk using its resource group (extracted from ID) and name.

                if disk.disk_state != "Attached":
                    # If the Managed Disk exists but is not attached:

                    compute_client.snapshots.begin_delete(snapshot.id.split('/')[4], snapshot.name)
                    # Delete the snapshot since the disk is not actively in use.

                    print(f"Deleted snapshot {snapshot.name} as its associated Managed Disk was not attached.")
                    # Log a message to the console indicating that the snapshot was deleted.

                    with open('/app/logs/cleanup_log.txt', 'a') as log_file:
                        # Open the cleanup log file in append mode.

                        log_file.write(f"Deleted snapshot {snapshot.name} as its associated Managed Disk was not attached.\n")
                        # Write the snapshot deletion details into the log file.

            except Exception as e:
                # Handle any errors that occur during disk checks:

                print(f"Error checking Managed Disk for snapshot {snapshot.name}: {e}")
                # Log the error message to the console.

                with open('/app/logs/cleanup_log.txt', 'a') as log_file:
                    # Open the cleanup log file in append mode.

                    log_file.write(f"Error checking Managed Disk for snapshot {snapshot.name}: {e}\n")
                    # Write the error details into the log file.
