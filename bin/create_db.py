import os
import subprocess
import urllib.request

with open(".env") as file:
    for line in file:
        print(line)

REQUIRED_ENV_VARS = (
    "AZ_GROUP",
    "AZ_LOCATION",
    "POSTGRES_SERVER_NAME",
    "POSTGRES_ADMIN_USER",
    "POSTGRES_ADMIN_PASSWORD",
    "APP_DB_NAME",
)

missing = []
for v in REQUIRED_ENV_VARS:
    if v not in os.environ:
        missing.append(v)
if missing:
    print("Required Environment Variables Unset:")
    print("\t" + "\n\t".join(missing))
    print("Exiting.")
    exit()

# Ref: https://docs.microsoft.com/en-us/azure/mysql/quickstart-create-mysql-server-database-using-azure-cli
create_server_command = [
    "az",
    "mysql",
    "server",
    "create",
    "--resource-group",
    os.getenv("AZ_GROUP"),
    "--location",
    os.getenv("AZ_LOCATION"),
    "--name",
    os.getenv("HOST_NAME"),
    "--admin-user",
    os.getenv("ADMIN_USR"),
    "--admin-password",
    os.getenv("ADMIN_PWD"),
    "--sku-name",
    "GP_Gen5_2",
]

create_server = input("Create PostgreSQL server? [y/n]: ")
if create_server == "y":
    print("Creating MySQL server...")
    subprocess.check_call(create_server_command)