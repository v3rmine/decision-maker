
from os import walk

def getAllFiles(path):
    all_files = []

    for (dirpath, _, filenames) in walk(path):
        all_files.extend([dirpath + '/' + str(x) for x in filenames])
    
    files = [x.replace('\\', '/') for x in all_files]
    print('get ' + str(len(files)) + ' files in ' + path)

    return files