import os

# get a list of all files in a dir
def get_valid_files():
    path = "NATX_2025_11_05/"

    files = os.listdir(path)

    # filter files to just get standard adult fares files. E.g. ignore senior, student, or infant fares
    filtered_files = []
    for file in files:
        if "adult" in file.lower() and "single" in file.lower():
            filtered_files.append(file)

    return filtered_files
