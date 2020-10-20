import os


class FileReader:

    def __init__(self):
        pass

    def get(self, filepath, cookies):
        '''
        Returns a binary string of the file contents, or None.
        '''
        try:
            # Try opening file to see if it exists
            f = open(filepath, "rb")
            contents = f.read()
            return contents
        except:
            return None

    def head(self, filepath, cookies):
        '''
        Returns the size to be returned, or None.
        '''
        try:
            # Try opening file to see if it exists
            size = os.path.getsize(filepath)
            return size
        except:
            return None
