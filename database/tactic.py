import os

def get_modules(package="tactics"):
    tactics = []
    files = os.listdir(package)

    for file in files:
        if not file.startswith("__"):
            name, ext = os.path.splitext(file)
            if ext == '.py':
                tactics.append(name)
    return tactics