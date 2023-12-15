"""
This module is used to delete commands with Discord.
"""

import requests
import yaml


TOKEN = "INSERT YOUR BOT TOKEN HERE"
APPLICATION_ID = "INSERT_APPLICATION_ID_HERE"
# ID for the command that needs to be deleted from bot.
COMMAND_ID = "INSERT_COMMAND_ID_HERE"

# If you want to delete command globally for bot in all servers, use this URL.
# URL = f"https://discord.com/api/v9/applications/{APPLICATION_ID}/commands/{COMMAND_ID}"

# If you want to delete command only in a specific guild/server, use this URL.
GUILD_ID = "INSERT YOUR GUILD/SERVER ID HERE"

# Guild URL
DEL_URL = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands/{COMMAND_ID}"

headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

# Send the DELETE request for each command
payload = {'name': 'INSERT COMMAND NAME that needs to be deleted.'}
response = requests.delete(DEL_URL, json=payload, headers=headers)
if response.status_code != 200:
    print(response.text)
else:
    print(f"Command deleted: {response.status_code}")