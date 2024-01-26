import os
import subprocess

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def set_pulumi_config(key, env_var_name, secret=False):
    value = os.getenv(env_var_name)
    print(env_var_name)
    if value is None:
        raise ValueError(f"Environment variable {env_var_name} not set")
    command = ["pulumi", "config", "set", key, value]
    if secret:
        command.append("--secret")
    subprocess.run(command, check=True)


def main():
    aws_region = os.getenv("AWS_REGION")
    if aws_region is not None:
        set_pulumi_config("aws:region", "AWS_REGION")

    set_pulumi_config("sql-admin-name", "SQL_ADMIN_NAME")
    set_pulumi_config("sql-admin-password", "SQL_ADMIN_PASSWORD", secret=True)
    set_pulumi_config("sql-user-name", "SQL_USER_NAME")
    set_pulumi_config("sql-user-password", "SQL_USER_PASSWORD", secret=True)
    set_pulumi_config("django-admin-name", "DJANGO_ADMIN_NAME")
    set_pulumi_config("django-admin-password", "DJANGO_ADMIN_PASSWORD", secret=True)
    set_pulumi_config("django-secret-key", "SECRET_KEY", secret=True)


if __name__ == "__main__":
    main()
