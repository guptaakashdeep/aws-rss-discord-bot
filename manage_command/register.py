"""
This module is used to register commands with Discord.
"""

import requests
import yaml


TOKEN = "INSERT YOUR BOT TOKEN HERE"
APPLICATION_ID = "INSERT_APPLICATION_ID_HERE"

# If you want to register command globally for bot in all servers, use this URL.
# URL = f"https://discord.com/api/v9/applications/{APPLICATION_ID}/commands"

# If you want to register command only in a specific guild/server, use this URL.
GUILD_ID = "INSERT YOUR GUILD/SERVER ID HERE"
# Guild URL
URL = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands"


with open("discord_commands.yaml", "r", encoding="utf-8") as file:
    yaml_content = file.read()

commands = yaml.safe_load(yaml_content)
headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

# Send the POST request for each command
for command in commands:
    response = requests.post(URL, json=command, headers=headers)
    command_name = command["name"]
    if response.status_code != 200:
        print(response.text)
    else:
        print(f"Command {command_name} created: {response.status_code}")