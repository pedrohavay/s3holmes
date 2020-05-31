"""The Python Module that contains all screens"""
import npyscreen
import curses
import os
import urllib
import botocore
import time

from s3_holmes.src.widgets import FileExplorerWidget, AskAWSKeysWidget
from s3_holmes.src.values import LOGO, HELP_CONFIG


class ConfigScreen(npyscreen.ActionForm):
    def __init__(self, *args, **kwargs):
        # Init parent class
        super().__init__(*args, **kwargs)

        # Define help
        self.help = HELP_CONFIG

        # Init help
        self.draw_title_and_help()

    def create(self):
        # Show splash screen
        npyscreen.notify(LOGO, wide=True)
        time.sleep(1)  # Wait 1 second

        # URL Field
        self.url = self.add(npyscreen.TitleText, name="Target:")

        # AWS Keys optional
        self.profile = self.add(
            AskAWSKeysWidget, max_height=4, value=[0, ],
            name="Use AWS Keys?", values=["No", "Yes"],
            scroll_exit=True, rely=4)

        # Reload screen, because of splash screen
        self.refresh()

    def activate(self):
        # Transform to editable
        self.edit()

    def aws_configure(self, hidden):
        self.parentApp.switchForm("AWSKeys")
        pass

    def on_ok(self):
        # Sound
        curses.beep()

        # Go to FileExplorer
        self.parentApp.switchForm("FileExplorer")

    def test(self,  *args, **keywords):
        self.set_editing(self.url)
        self.refresh()


class AWSKeys(npyscreen.ActionForm):
    CANCEL_BUTTON_TEXT = "Back"
    OK_BUTTON_TEXT = "Save"

    def create(self):
        # AWS Key
        self.key = self.add(npyscreen.TitleText, name="AWS Key:")
        self.secret = self.add(npyscreen.TitleText, name="AWS Secret:")
        self.region = self.add(npyscreen.TitleText, name="Region:")

    def active(self):
        # Transform to editable
        self.edit()

        # Define file explorer Screen as next
        self.parentApp.setNextForm("MAIN")

    def on_ok(self):
        # Sound
        curses.beep()

        # Check if is missed some field
        if (self.key.value == "" or self.secret.value == "" or self.region.value == ""):
            # Open pop up
            npyscreen.notify_confirm("All fields are required.")
        else:
            # Return to config screen
            self.parentApp.switchForm("MAIN")

    def on_cancel(self):
        # Get config screen context
        self.config = self.parentApp.getForm('MAIN')

        # Modify select value
        self.config.profile.set_value([0, ])

        # Return to config screen
        self.parentApp.switchForm("MAIN")


class FileExplorerScreen(npyscreen.FormBaseNewExpanded):
    """File Explorer Screen Class

    This class contains all logic to list, download, find...
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Init attributes
        self.prefix = ""
        self.bucket = ""
        self.__files = []

        # Get s3 instance
        self.__s3 = self.parentApp.s3

    def create(self):
        self.FileExplorer = self.add(FileExplorerWidget, name="/")

    def activate(self):
        # Get before screen instance
        self.URLForm = self.parentApp.getForm("MAIN")

        # Get Bucket URL or No
        if "." in self.URLForm.url.value:
            # Adding https:// to URL
            if 'https://' not in self.URLForm.url.value and 'http://' not in self.URLForm.url.value:
                self.URLForm.url.value = f"https://{self.URLForm.url.value}"

            # Parsing URL
            url = urllib.parse.urlparse(self.URLForm.url.value)
            self.bucket = url.hostname.split('.')[0]
        else:
            # Normal Value
            self.bucket = self.URLForm.url.value

        # Get objects
        self.load_objects("")

        # Transform to selectable
        self.edit()

    def load_objects(self, prefix):
        # First, check if is a file
        if prefix in self.__files:
            # Show confirm dialog
            confirm_download = npyscreen.notify_yes_no(
                prefix, title="Do you want to download this file?")

            # Get value
            if (confirm_download):
                # Call the method
                self.download_file(prefix)

            # Keep in the same folder
            return

        # Set attribute
        if prefix != "" and prefix != "Parent Directory":
            self.prefix = prefix

        if prefix == "Parent Directory ←":
            # Get parent folder
            parent_folder = os.path.dirname(self.prefix[:-1]) + "/"

            if parent_folder == "/":
                parent_folder = ""

            # Set prefix
            self.prefix = parent_folder

        if prefix == "":
            self.FileExplorer.name = "/"
            self.FileExplorer.update()
        else:
            self.FileExplorer.name = self.prefix
            self.FileExplorer.update()

        # Clear values
        self.FileExplorer.values = []
        self.update()

        # Get objects
        objects = None

        try:
            objects = self.__s3.list_objects(
                Bucket=self.bucket, Prefix=self.prefix, Delimiter="/")
        except botocore.exceptions.ClientError as e:
            # Init error message
            error_text = "An error ocurred while listing the bucket.."

            # Check error type
            if e.response['Error']['Code'] == "404":
                error_text = "The S3 bucket does not exist."
            elif e.response['Error']['Code'] == "403":
                error_text = "Forbidden Operation."

            # Show error message
            npyscreen.notify_confirm(error_text, 'Download File Error')

            # Return to config screen
            self.parentApp.switchForm("MAIN")

            # Stop method
            return

        # Get folders
        folders = []

        if 'CommonPrefixes' in objects.keys():
            folders = [v['Prefix'] for v in objects['CommonPrefixes']]

        # Get files
        self.__files = []

        if 'Contents' in objects.keys():
            self.__files = [v['Key'] for v in objects['Contents']]

        # Init tree
        tree = None

        # Set Values
        if prefix == "":
            tree = [*folders, *self.__files]
        else:
            tree = ["Parent Directory ←", *folders, *self.__files]

        # Remove duplicated folder in list
        if self.prefix in tree:
            tree.remove(self.prefix)

        # Update Values
        self.FileExplorer.values = tree
        self.FileExplorer.update()

    def download_file(self, prefix):
        try:
            # Get arguments
            current_path = str(os.getcwd())
            filename = str(prefix).rsplit("/", maxsplit=1)[-1]

            # Open Pop up
            npyscreen.notify("Downloading...")

            # Download the file
            self.__s3.download_file(
                self.bucket, prefix, f"{current_path}/{filename}")
        except botocore.exceptions.ClientError as e:
            # Init error message
            error_text = "An error ocurred while downloading the file."

            # Check error type
            if e.response['Error']['Code'] == "404":
                error_text = "The object does not exist."
            elif e.response['Error']['Code'] == "403":
                error_text = "Forbidden Operation."

            # Show error message
            npyscreen.notify_confirm(error_text, 'Download File Error')

    def update(self):
        pass
