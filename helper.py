import os

# * Create a folder if it doesn't exist
# * or overwrite the existing folder


def create_folder(path: str) -> None:
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))
