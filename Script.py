import os
# Import the 'os' module to access environment variables stored in the .env file
# and manage filesystem paths.

from azure.identity import DefaultAzureCredential
# Import DefaultAzureCredential to authenticate with Azure services without
# hardcoding credentials.

from azure.mgmt.compute import ComputeManagementClient
# Import ComputeManagementClient to manage Azure Compute resources such as
# snapshots and disks.

def azure_cleanup_snapshots():
    """
    Function to clean up unused Azure snapshots by:
    - Deleting snapshots not associated with any Managed Disks.
    - Deleting snapshots whose associated Managed Disks are not in use.
    """

    # Retrieve the Azure subscription ID from environment variables.
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")

    # Authenticate with Azure services using DefaultAzureCredential.
    credential = DefaultAzureCredential()

    # Create a client to interact with Azure Compute resources.
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Path for the log file where cleanup details are recorded.
    log_file_path = '/app/logs/cleanup_log.txt'

    # Ensure the logs directory exists and create the log file if it doesn't.
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    if not os.path.isfile(log_file_path):
        open(log_file_path, 'w').close()

    # List all snapshots in the Azure subscription.
    snapshots = compute_client.snapshots.list()

    for snapshot in snapshots:
        # Iterate through each snapshot in the subscription.

        snapshot_id = snapshot.id
        # Extract the unique identifier for the snapshot.

        managed_disk_id = snapshot.managed_disk.id if snapshot.managed_disk else None
        # Determine whether the snapshot is associated with a Managed Disk.

        if not managed_disk_id:
            # If the snapshot is not associated with any Managed Disk:
            
            compute_client.snapshots.begin_delete(snapshot.id.split('/')[4], snapshot.name)
            # Delete the snapshot using its resource group (extracted from the ID) and name.

            print(f"Deleted snapshot {snapshot.name} as it was not attached to any Managed Disk.")
            # Log the deletion action to the console.

            with open(log_file_path, 'a') as log_file:
                log_file.write(f"Deleted snapshot {snapshot.name} as it was not attached to any Managed Disk.\n")
                # Record the action in the cleanup log file.

        else:
            try:
                # If the snapshot is linked to a Managed Disk, retrieve the disk's details.
                
                disk = compute_client.disks.get(managed_disk_id.split('/')[4], managed_disk_id.split('/')[-1])
                # Fetch the Managed Disk using its resource group (extracted from the ID) and name.

                if disk.disk_state != "Attached":
                    # If the Managed Disk is not currently in use:

                    compute_client.snapshots.begin_delete(snapshot.id.split('/')[4], snapshot.name)
                    # Delete the snapshot as the associated disk is inactive.

                    print(f"Deleted snapshot {snapshot.name} as its associated Managed Disk was not attached.")
                    # Log the deletion action to the console.

                    with open(log_file_path, 'a') as log_file:
                        log_file.write(f"Deleted snapshot {snapshot.name} as its associated Managed Disk was not attached.\n")
                        # Record the deletion in the cleanup log file.

            except Exception as e:
                # Handle any exceptions that occur while retrieving or validating the disk:
                
                print(f"Error checking Managed Disk for snapshot {snapshot.name}: {e}")
                # Log the error message to the console.

                with open(log_file_path, 'a') as log_file:
                    log_file.write(f"Error checking Managed Disk for snapshot {snapshot.name}: {e}\n")
                    # Record the error details in the cleanup log file.

    # Final message to indicate cleanup completion.
    final_message = "Cleanup process completed successfully!"

    print(final_message)
    # Print the final message to the console.

    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{final_message}\n")
        # Log the final message in the cleanup log file.

