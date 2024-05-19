**Comprehensive Guide to Backup and Restore PostgreSQL Database Utilizing Google Drive Storage**

This guide details the use of two Python scripts: `backup.py` and `restore.py` for the purpose of backing up and restoring databases. The `backup.py` script is responsible for creating a **PostgreSQL dump**, which it achieves by zipping and encrypting the specified database. Once encrypted, the dump is uploaded to **Google Drive Storage** for safekeeping. On the other hand, the `restore.py` script locates the most recent dump in **Google Drive Storage**, downloads it, and subsequently unzips and decrypts the data. Once decrypted, the data is then loaded back into the **PostgreSQL** database.

---
$\color{#D29922}\textsf{\Large\&#x26A0;\kern{0.2cm}\normalsize Warning}$ $${\color{red}Please \space note, \space the \space database \space will \space be \space dropped \space before \space the \space backup \space from \space Google \space Drive \space is \space restored.}$$

---


To effectively use both scripts, you'll need:

- A version of Python3.6 or higher,
- The pip packages installed from the `requirements.txt` file,
- The Google Drive API and a Service Account enabled with the appropriate roles and permissions,
- Files with public (`backup_key.pem.pub`) and private (`backup_key.pem`) keys for encrypting and decrypting the dump, which can be generated with openssl:

```bash
openssl req -x509 -nodes -days 1000000 -newkey rsa:4096 -keyout backup_key.pem\\
-subj "/C=US/ST=Illinois/L=Chicago/O=IT/CN=[www.example.com](<http://www.example.com/>)" \\
-out backup_key.pem.pub

```

- A file with the PostgreSQL database password (`~/.pgpass`) set with `chmod 600`, including, for example:

```
localhost:5432:your_database:your_db_user:your_db_user_password

```

- Finally, ensure to check the `check_hostname()` function in the `restore.py` script. This function checks the `hostname` of the current server, serving as a safeguard against potentially dropping database tables on the production server.

## Enabling Google Drive API

To enable the Google Drive API, follow these steps:

1. Go to the Google Cloud Console at `https://console.cloud.google.com/`.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/50e83b83-cec2-4982-a094-79d413055271)

2. Navigate to `APIs & Services`. In the left sidebar, select `Dashboard` under `APIs & Services`.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/521d5f2a-b640-459e-bc2a-5fc6ed18e8d0)
3. Click on `Enable APIs and Services`. Search for `Google Drive API` and enable it for your project.
---
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/3d525188-584e-49eb-ab7c-513d1fb1da22)

---
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/ca4125e9-2695-4ac5-9deb-bf88f63a3862)

---
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/20bb2c9f-665e-44b4-b9c1-563877b9c7b6)

---
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/e708b479-ad7a-490d-8cb5-47e9008ec1cf)

---
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/270ba999-28de-4a60-b0f0-81f48aff42ed)

## Creating Credentials
1. Open the console left side menu and select `IAM & Admin`, then `Service Accounts`.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/dc96cdc6-04e4-4798-8046-32f6b674b313)
2. Click `Create Service Account`.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/0ce91fcd-05a7-468d-979f-cfa997d5fa1a)
4. In the `Service account name` field, enter a name. In the `Service account description` field, enter a description. Click `Create`.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/d71d3f51-5df8-4e96-9ce9-148e82aa680c)
5. Under `Grant this service account access to project`, select the `Role` drop-down list. You should assign it the following roles: `Editor`, `Storage Admin`, `Storage Object Admin`, and `Storage Object Creator`. These roles will allow your service account to perform necessary actions in Google Drive. Click `Continue`.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/8b2a8c55-a39c-4126-a76f-5ea671788e5b)
6. Under `Grant users access to this service account`, in the `User` field, enter your email address. Click `Done`.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/015fb157-885b-48d7-98a9-6fd62de9c51e)
7. Find the email of your new service account in the `Service Accounts` list and click on it.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/d8077ce3-092b-43ec-8f1d-9397d7f41ec7)
8. In the `Keys` section, click `Add Key`, then `Create new key`.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/3bf24d4c-c37b-463c-8966-ed0a8a0ecaf6)
9. For the `Key type`, choose `JSON`. Click `Create`. A **JSON** file that contains your key downloads to your computer.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/7bb9635c-2139-44d9-b394-4cf7335cb1b7)
10. Save this **JSON** file, you will need it to run your scripts. Do not share it with anyone, as it allows access to your **Google Drive**.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/f0d06319-459d-4453-bbdc-08d5e4f12e43)

## Bind Service Account to your personal Google Drive folder
To bind a **service account** from **Google Cloud** to your personal **Google Drive** and gain necessary permissions to upload and delete files, you can follow these steps:
1. **Share Your Google Drive Folder with the Service Account**
    - Open your **Google Drive** and create or navigate to the folder you want to share
      ![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/02d42526-be50-42cc-bfe5-73efeaf34d4c)
    - Click on the folder’s name and then click on the `Share` icon
      ![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/b7f8b256-3da3-42d1-b20b-60ae4cff2671)
    - In the `Add people and groups` section, enter the email address of your Service Account (you can find this on the Service Account's detail page in Google Cloud or in the JSON file which you downloaded in the `email` field) and click `Send`
      ![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/598af03c-0bfa-4266-b0ec-eefe8742f82a)
      ![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/8af70d46-325b-474a-8b46-925ffd2d4686)

## Google Drive Folder ID
To find the **Google Drive** folder **ID**, follow these steps:
1. Open your **Google Drive**.
2. Navigate to the folder for which you need the **ID**.
3. Click on the folder to open it.
4. Look at the **URL** in your web browser's address bar. The long string of characters at the end of the URL is the folder's **ID**.
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/d9aae11f-1e10-46fd-bd99-d8db2cd1b79f)
**(Don't forget to Remove the Query Parameter)**

## BACKUP

Here's how the script works:

1. **Environment Variables**: At the beginning, the script sets up several environment variables, such as the host name of the database (`DB_HOSTNAME`), the database name (`DB_NAME`), the database user (`DB_USER`), the Google Drive folder ID where the backup will be stored (`GOOGLE_DRIVE_FOLDER_ID`), and the file path to the public key used for encryption (`BACKUP_KEY_PUB_FILE`).
2. **Function Definitions**: Several functions are defined for use in the script. These include:
    - `say_hello()`: This function prints a greeting message when the script is run.
    - `get_now_datetime_str()`: This function returns the current date and time as a formatted string.
    - `check_key_file_exists()`: This function checks if the public key file for encryption exists. If it doesn't, the script exits.
    - `dump_database()`: This function uses the `pg_dump` command to create a dump of the PostgreSQL database, compresses the dump using gzip, and then encrypts the compressed dump using openssl. The encrypted dump is then saved to a temporary file.
    - `get_drive_service()`: This function creates and returns a Google Drive service client, which is used to interact with the Google Drive API.
    - `upload_dump_to_drive()`: This function uploads the encrypted database dump to Google Drive. The file metadata (including the file name and the ID of the parent Google Drive folder) and the file content are specified in the request. After the file is uploaded, the function prints the ID of the uploaded file.
    - `remove_temp_files()`: This function removes the temporary file containing the encrypted database dump.
3. **Main Program**: The main part of the script (under `if __name__ == "__main__":`) calls the functions defined above in the correct order. First, it prints a greeting message, checks if the public key file exists, creates a database dump, uploads the dump to Google Drive, and finally removes the temporary file.

## RESTORE
Here's how the script works:

1. **Environment Variables**: The script starts by setting up several environment variables, including the hostname of the database, the database name, the database user, the Google Drive folder ID where the backup is stored, and the file path to the private key used for decryption.
2. **Database Connection**: The script establishes a connection to the PostgreSQL database.
3. **Function Definitions**: The script defines several functions that are used to restore the database:
    - `say_hello()`: Prints a greeting message to the console.
    - `check_hostname()`: Checks the hostname of the current server. The script will stop execution if the hostname does not start with 'loader-' or end with '.local'.
    - `check_key_file_exists()`: Checks if the private key file for decryption exists. If not, the script stops.
    - `get_drive_service()`: Creates and returns a Google Drive service client, which is used to interact with the Google Drive API.
    - `get_last_backup_filename()`: Lists the files in the Google Drive folder and finds the most recent file, returning its name.
    - `download_s3_file(filename)`: Removes any existing file with the same name as the database dump, then downloads the specified file from Google Drive.
    - `unencrypt_database()`: Decrypts the downloaded database dump using openssl.
    - `unzip_database()`: Unzips the decrypted database dump.
    - `clear_database()`: Clears the current database state by dropping all tables.
    - `load_database()`: Loads the unzipped database dump into the PostgreSQL database.
    - `remove_temp_files()`: Removes the temporary file containing the encrypted database dump.
    - `_get_all_db_tables()`: Helper function that returns a list of all table names in the public schema of the database.
    - `_silent_remove_file(filename)`: Helper function that removes a specified file without throwing an error if the file does not exist.
4. **Main Program**: The main part of the script (under `if __name__ == "__main__":`) calls the defined functions in the correct order. It prints a greeting message, checks the hostname and if the private key file exists, downloads the most recent backup file from Google Drive, decrypts and unzips the downloaded file, clears the database, loads the unzipped dump into the database, and finally, removes the temporary file.

## Results

![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/596a2e85-4124-458a-802d-b7f80d5f19cb)
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/fa8d8534-2dd3-47e3-a387-a642d86e2df7)
![image](https://github.com/hasan2001jk/Postgres-Google-Drive-Backuper/assets/64947215/c90b37cf-08c6-44ab-854d-8345a63c74b8)



