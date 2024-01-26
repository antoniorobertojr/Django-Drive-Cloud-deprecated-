FROM ubuntu:18.04

WORKDIR /

EXPOSE 80

# Install necessary packages
RUN apt-get update && \
    apt-get install -y gcc python3-dev python3-pip mysql-client-core-5.7 libmysqlclient-dev dos2unix

# Add and install Python requirements
COPY requirements-backend.txt /backend/requirements-backend.txt
RUN pip3 install -r /backend/requirements-backend.txt

# Add application code
COPY . /backend

# Convert line endings and make script executable
# ADD ./setupDatabase.sh /backend/setupDatabase.sh
RUN dos2unix /backend/setupDatabase.sh && chmod +x /backend/setupDatabase.sh

CMD ["python3", "/backend/manage.py", "runserver", "0.0.0.0:80"]
