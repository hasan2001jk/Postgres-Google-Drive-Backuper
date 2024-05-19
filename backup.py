import datetime
import os
from pathlib import Path
import pytz

from termcolor import colored
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

DB_HOSTNAME = os.getenv("DB_HOSTNAME", "localhost")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
BACKUP_KEY_PUB_FILE = os.getenv("BACKUP_KEY_PUB_FILE")
TIME_ZONE = os.getenv("TIME_ZONE", "Europe/Moscow")

DB_FILENAME = "/tmp/backup_db.sql.gz.enc"


def say_hello():
    print(colored("Hi! This tool will dump PostgreSQL database, compress \n"
        "and encode it, and then send to Google Drive.\n", "cyan"))


def get_now_datetime_str():
    now = datetime.datetime.now(pytz.timezone(TIME_ZONE))
    return now.strftime('%Y-%m-%d__%H-%M-%S')


def check_key_file_exists():
    if not Path(BACKUP_KEY_PUB_FILE).is_file():
        exit(
            f"\U00002757 Public encrypt key ({BACKUP_KEY_PUB_FILE}) "
            f"not found. If you have no key – you need to generate it. "
            f"You can find help here: "
            f"https://www.imagescape.com/blog/2015/12/18/encrypted-postgres-backups/"
        )


def dump_database():
    print("\U0001F4E6 Preparing database backup started")
    dump_db_operation_status = os.WEXITSTATUS(os.system(
        f"pg_dump -h {DB_HOSTNAME} -U {DB_USER} {DB_NAME} | gzip -c --best | \
        openssl smime -encrypt -aes256 -binary -outform DEM \
        -out {DB_FILENAME} {BACKUP_KEY_PUB_FILE}"
    ))
    if dump_db_operation_status != 0:
        exit(f"\U00002757 Dump database command exits with status "
             f"{dump_db_operation_status}.")
    print("\U0001F510 DB dumped, archived and encoded")


def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/drive'])
    return build('drive', 'v3', credentials=credentials)

def upload_dump_to_drive():
    print("\U0001F4C2 Starting upload to Google Drive")
    drive_service = get_drive_service()
    file_metadata = {
        'name': f'db-{get_now_datetime_str()}.sql.gz.enc',
        'parents': [GOOGLE_DRIVE_FOLDER_ID]  # ID of the folder where you want to upload the file
    }
    print(f"file_metadata: {file_metadata}")
    media = MediaFileUpload(DB_FILENAME, mimetype='application/octet-stream')
    print(f"media: {media}")
    try:
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"\U0001f680 Uploaded, file ID: {file.get('id')}")
    except Exception as e:
        print(f"Error uploading file: {e}")

def remove_temp_files():
    os.remove(DB_FILENAME)
    print(colored("\U0001F44D That's all!", "green"))

if __name__ == "__main__":
    say_hello()
    check_key_file_exists()
    dump_database()
    upload_dump_to_drive()
    remove_temp_files()
