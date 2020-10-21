import subprocess
import os
from background_task import background
import requests
from bs4 import BeautifulSoup
from keras.utils import get_file
import telegram


@background(schedule=2)
def send_message():
    token = "880946633:AAFn_GKcaIrQZoy02V0u1XjABK_jaulDGCo"
    chat_id = "654979499"

    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=chat_id, text="Hello")


@background(schedule=2)
def refresh_simplewiki_db():
    base_url = "https://dumps.wikimedia.org/simplewiki/"
    index = requests.get(base_url).text
    soup_index = BeautifulSoup(index, "html.parser")

    # Find all the links on the page. These links are the snapshot timestamp
    dumps = [a["href"] for a in soup_index.find_all("a") if a.has_attr("href")]

    # Usually the last link is "latest" and the one before that is the latest timestamp
    if "latest" not in dumps[-1]:
        print("Couldn't find the latest dump")
        exit

    dump = dumps[-2]
    dump = "20201001/"

    # Create dump url with the base and the latest timestamp
    dump_url = base_url + dump

    # Retrieve the dump page
    dump_html = requests.get(dump_url).text
    soup_dump = BeautifulSoup(dump_html, "html.parser")

    # Search for SQL files
    files = []
    for file in soup_dump.find_all("li", {"class": "file"}):
        text = file.text
        if "sql" in text:
            files.append((text.split()[0], text.split()[1:]))

    files_to_download = [file[0] for file in files]

    dataset_dir = os.path.join(os.getcwd(), "datasets")
    data_paths = []
    file_info = []

    for file in files_to_download:
        path = os.path.join(dataset_dir, file)

        if not os.path.exists(path):
            data_paths.append(
                get_file(fname=file, origin=dump_url + file, cache_subdir=dataset_dir)
            )
            # Find the file size in MB
            file_size = os.stat(path).st_size / 1e6
            file_info.append((file, file_size))

        else:
            data_paths.append(path)
            file_size = os.stat(path).st_size / 1e6
            file_info.append((file.split("-")[-1], file_size))

    for data_path in data_paths:
        subprocess.call(["gunzip", f"{data_path}"])

    # Start activities on the database
    db_host = os.getenv("DB_HOST", "db")
    admin_usr = os.getenv("ADMIN_USR", "root")
    admin_pwd = os.getenv("ADMIN_PWD", "LocalPassword")
    wiki_db = os.getenv("WIKI_DB", "simplewiki")

    # Drop the db
    drop_db_command = (
        "mysql --host={} --user={} --password={} ".format(
            db_host,
            admin_usr,
            admin_pwd,
        )
        + '-e "DROP DATABASE IF EXISTS {};CREATE DATABASE {};"'.format(wiki_db, wiki_db)
    )
    subprocess.run(
        drop_db_command,
        shell=True,
    )

    # Ingest new data into db
    sql_data_paths = [item[:-3] for item in data_paths]
    for sql_data_path in sql_data_paths:
        with open(sql_data_path) as f:
            command = [
                "mysql",
                "--host={}".format(db_host),
                "--user={}".format(admin_usr),
                "--password={}".format(admin_pwd),
                "--database={}".format(wiki_db),
            ]
            p = subprocess.Popen(
                command, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output, error = p.communicate()  # pylint: disable=unused-variable
            if p.returncode != 0:
                # We can handle this better by sending an email or similar
                print(error)

    os.system("rm datasets/*")
    os.system("rm -rf datasets")
