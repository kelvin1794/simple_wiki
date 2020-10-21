FROM tiangolo/uwsgi-nginx:latest

# Indicate where uwsgi.ini lives
ENV UWSGI_INI uwsgi.ini

WORKDIR /app

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends default-mysql-client

# Using pip:
COPY requirements.txt /app
RUN python3 -m pip install -r requirements.txt

ADD . /app

RUN export $(grep -v '^#' .env | xargs) && python3 manage.py makemigrations -noinput && python3 manage.py migrate --noinput && python3 manage.py collectstatic --noinput
RUN rm .env

# When deployed to Azure, the app runs with GID 1000 and we
# will have to creat such user in etc/passwd
# Otherwise, pyodbc will throw an error
ARG USERNAME=finex_app_service
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# ssh
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
    && apt-get install -y --no-install-recommends dialog \
    && apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "$SSH_PASSWD" | chpasswd 

COPY sshd_config /etc/ssh/

EXPOSE 8000 2222
