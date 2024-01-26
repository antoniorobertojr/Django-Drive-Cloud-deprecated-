# Django Drive Cloud

Sets up a Django solution similar to Google Drive, but using AWS infrastructure. It utilizes Django Rest Framework for file and folder management functionalities like upload, share, and unshare. The architecture leverages ECS with Fargate for scalable container management, RDS for reliable database services, and ECR for efficient Docker image storage.

## Installation

1. **Configure AWS CLI** 
Ensure AWS CLI is installed and configured with the necessary access credentials and default region:
```
aws configure
```
2. **Clone the Repository**
Clone the project repository to your local machine.
```
mkdir django-drive-cloud
cd django-drive-cloud
git clone https://github.com/juniormach96/Django-Drive-Cloud .
```

3. **Create and Activate Python Virtual Environment**
Create a Python virtual environment and activate it.
```
python3 -m venv .venv
source .venv/bin/activate
```
4. **Install Required Python Packages**
Install the necessary Python packages using pip.
```
pip install -r infrastructure/requirements-pulumi.txt
```
5. **Configure Environment Variables**
Rename the example environment file and update it with your specific values.
```
mv infrastructure/.env-example infrastructure/.env
```
6. **Edit infrastructure/.env with your desired configurations**
7. **Set Up Pulumi Configuration**
Run the setup script to configure Pulumi with the variables you've declared.
```
python3 infrastructure/setup.py
```
8. **Initialize Infrastructure**
Deploy the infrastructure using Pulumi.
```
pulumi up
```

## How it Works

### Network Stack

The network stack is essential for ensuring secure and efficient communication in cloud architecture. Here's a breakdown of its structure:

#### Virtual Private Cloud (VPC)

- **AWS VPC (`app_vpc`)**: A virtual network created with a CIDR block of `172.31.0.0/16`.

#### Subnets

- **Public Subnet (`app_vpc_subnet`)**: A subnet with the block `172.31.0.0/20` within the VPC.

#### Route Table and Internet Gateway

- **Internet Gateway (`app_gateway`)**: Connects the VPC to the internet, enabling communication with external networks.
- **Route Table (`app_routetable`)**: Directs network traffic from the subnet to the internet gateway, routing all traffic (`0.0.0.0/0`) externally.

### Elastic Container Registry (ECR)

- **ECR Repository (`app_ecr_repo`)**: A Docker container registry for the two Docker images.

#### Lifecycle Policy

- **ECR Lifecycle Policy (`app_lifecycle_policy`)**: Automates the removal of old images.

### Load Balancer

- **Load Balancer (`django_balancer`)**: Distributes incoming traffic across multiple targets in the ECS.
- **Listener (`django_listener`)**: Monitors for connection requests on TPC protocol and port 80, directing them to the target group.

### Database Component

#### MySQL Database

- **RDS Instance (`mysql_rds_server`)**: A managed relational database service hosting the MySQL database.

#### Subnet Group for RDS

- **Subnet Group (`app_database_subnetgroup`)**: Associate the RDS with two subnets (`app_vpc_subnet` and `extra_rds_subnet`)

### Elastic Container Service (ECS) with Fargate

#### ECS Cluster

- **ECS Cluster (`app_cluster`)**: Hosts the application and database tasks or services in a logically grouped environment.

#### Fargate

- **Serverless Compute Engine**: Runs the containers without the need to manage servers or clusters.

#### Execution and Task Roles

- **Execution Role (`app_exec_role`)**: Grants ECS permissions to pull images from ECR and store logs in CloudWatch.
- **Task Role (`app_task_role`)**: Provides tasks with specific permissions to access AWS resources (RDS, ECR, CloudWatch)

#### Task Definitions

- **Database Setup Task (`django_database_task_definition`)**: Configures a Django container to set up the database, overriding the default command with `setupDatabase.sh`.
- **Main Server Task (`django_site_task_definition`)**: Runs the Django application.

### CloudWatch Logs

- **Log Group (`django_log_group`)**: Collects and stores logs from ECS services, aiding in monitoring and troubleshooting.
