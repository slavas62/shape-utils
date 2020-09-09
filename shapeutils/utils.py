import StringIO
import shutil
import tempfile
import zipfile

class tempdir():
    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        return self.dir
    
    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.dir, True)

class InMemoryZip(zipfile.ZipFile):
    def __init__(self, compression=zipfile.ZIP_STORED, allowZip64=False):
        self.file = StringIO.StringIO()
        zipfile.ZipFile.__init__(self, self.file, mode='w', compression=compression, allowZip64=allowZip64)
        
    def read(self):
        self.file.seek(0)
        return self.file.read()
