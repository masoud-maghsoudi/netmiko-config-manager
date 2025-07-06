"""
This script deploy configurateions declared in config.yml file on
Cisco devices dclared in same config.yml file.

Author: Masoud Maghsoudi
Github: https://github.com/masoud-maghsoudi
Email:  masoud_maghsoudi@yahoo.com
"""

import os
from datetime import datetime
from getpass import getpass
from netmiko import ConnectHandler, exceptions
from yaml import safe_load


def load_configuration() -> dict:
    """Loads list of devices from config.yml file

    Returns:
        dict: loaded parameters from config file
    """
    params = {}
    file_path = os.path.dirname(__file__)
    with open(os.path.join(file_path, "config.yml"), "r", encoding="utf-8") as file:
        config = safe_load(file)
        params["devices"] = sorted(config["device_list"])
        params["configs"] = sorted(config["configs"])
        return params


def backup_config(device_ip: str) -> None:
    """Backup running configuration to file

    Args:
        device (str): Device IP address
    """
    conn_handler = {
        "device_type": "cisco_ios",
        "ip": device_ip,
        "username": USERNAME,  # pylint: disable=E0606
        "password": PASSWORD,  # pylint: disable=E0606
    }
    net_connect = ConnectHandler(**conn_handler)
    directory = "config_backup_files"
    if not os.path.isdir(directory):
        os.makedirs(directory)
    filename = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{conn_handler['ip']}-backup.config"
    with open(os.path.join(directory, filename), "w", encoding="utf-8") as file:
        backup = net_connect.send_command("show running-config")
        file.write(backup)


def write_startup_config(device_ip: str) -> None:
    """Writes running-config to startup-config

    Args:
        device (str): Device IP address
    """
    conn_handler = {
        "device_type": "cisco_ios",
        "ip": device_ip,
        "username": USERNAME,
        "password": PASSWORD,
    }
    net_connect = ConnectHandler(**conn_handler)
    try:
        command = net_connect.send_command("write memory")
        print(command)
    except exceptions.ReadTimeout:
        print("FTP config write timeout error")


def write_configs(data: dict) -> None:
    """Writes configs provided in dictionary for each device

    Args:
        data (dict): key: device IP address, value: list of configs
    """
    for key, value in data.items():
        backup_config(key)
        conn_handler = {
            "device_type": "cisco_ios",
            "ip": key,
            "username": USERNAME,
            "password": PASSWORD,
        }
        net_connect = ConnectHandler(**conn_handler)
        command = net_connect.send_config_set(value)
        print(command)
        write_startup_config(key)


# MAIN function
if __name__ == "__main__":

    NOTICE = """    ###############################################################################
    #                                                                             #
    #     NOTICE: You are changing the configration on Cisco devices based on     #
    #        configuration and devices declarted in config.yml file               #
    #                                                                             #
    #      Please do not proceed if you do not know the effects of deplying       #
    #                     configurations you are applying.                        #
    #                                                                             #
    ###############################################################################"""
    print(NOTICE)
    # REPORT_TYPE = input(
    #     "Which type of report do you prefer? [xlsx/csv] (Default: xlsx)"
    # ).strip()
    USERNAME = input("Please enter the username for devices: ").strip()
    PASSWORD = getpass(prompt="Please enter password for devices: ")

    CONFIGS = load_configuration()
    device_data = {}

    for device in CONFIGS["devices"]:
        device_data[device] = CONFIGS["configs"]

    write_configs(device_data)
