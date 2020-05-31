import npyscreen, curses, boto3, os

# Boto3 Extra
from botocore.client import Config
from botocore import UNSIGNED

# Import screens
from s3_holmes.src.screens import ConfigScreen, FileExplorerScreen, AWSKeys

class S3Holmes(npyscreen.NPSAppManaged):
    def onStart(self):        
        # Init boto3 client
        self.s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

        self.addForm("MAIN", ConfigScreen, name="S3 Configuration")
        self.addForm("AWSKeys", AWSKeys, name="AWS Keys")
        self.addForm("FileExplorer", FileExplorerScreen, name="S3 Tree", shortcut="^F")