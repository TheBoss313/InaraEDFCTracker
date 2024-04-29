import requests
import dotenv
import os

dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))
application_id = str(os.getenv("DISCORD_APP_ID"))
url = f"https://discord.com/api/v10/applications/{application_id}/commands"

# This is an example CHAT_INPUT or Slash Command, with a type of 1
json = {
    "name": "findcmdr",
    "type": 1,
    "description": "Searches for CMDRs by name.",
    "options": [
        {
            "name": "name",
            "description": "Commander name.",
            "type": 3,
            "required": True,
        },
    ]
}

# For authorization, you can use either your bot token
headers = {
    "Authorization": f"Bot {token}"
}

r = requests.post(url, headers=headers, json=json)

