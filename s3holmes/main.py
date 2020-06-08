import npyscreen, curses, os

# Import screens
from s3holmes.src.screens import ConfigScreen, FileExplorerScreen, AWSKeys

class S3Holmes(npyscreen.NPSAppManaged):
    def onStart(self):        
        # Init boto3 client
        self.addForm("MAIN", ConfigScreen, name="S3 Configuration")
        self.addForm("AWSKeys", AWSKeys, name="AWS Keys")
        self.addForm("FileExplorer", FileExplorerScreen, name="S3 Tree", shortcut="^F")