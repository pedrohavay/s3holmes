from s3_holmes import S3Holmes
import npyscreen

if __name__ == "__main__":
    # Init the main class
    npyscreen.wrapper(S3Holmes().run())