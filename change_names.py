import os

# Define the base path where the folders are located
base_path = "searches"

# Loop through the folders
for i in range(1, 9):
    folder_name = str(i)
    folder_path = os.path.join(base_path, folder_name)

    # Check if the folder exists
    if os.path.exists(folder_path):
        # Rename the folder
        new_folder_name = f"sec{i}_results"
        new_folder_path = os.path.join(base_path, new_folder_name)
        os.rename(folder_path, new_folder_path)

        # Loop through the JSON files in the folder
        for j in range(1, 9):
            file_name = f"{j}.json"
            file_path = os.path.join(new_folder_path, file_name)

            # Check if the file exists
            if os.path.exists(file_path):
                # Rename the file
                new_file_name = f"outline_{j}.json"
                new_file_path = os.path.join(new_folder_path, new_file_name)
                os.rename(file_path, new_file_path)
