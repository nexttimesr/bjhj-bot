import discord
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
intent = discord.Intents.default()
intent.members = True
intent.message_content = True

client = discord.Client(intents=intent)

def getSolo():
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/codes'
    params = {
        'count': 2,
        'tournamentId': 7528
    }
    headers = {
        'X-Riot-Token': os.getenv('RIOT')
    }
    data = {
              "mapType": "SUMMONERS_RIFT",
              "metadata": "",
              "pickType": "BLIND_PICK",
              "spectatorType": "ALL",
              "teamSize": 1
            }
    response = requests.post(url, headers=headers, params=params, json=data)
    print(json.loads(response.text))
    return json.loads(response.text)

def getNZ():
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/codes'
    params = {
        'count': 20,
        'tournamentId': 7528
    }
    headers = {
        'X-Riot-Token': os.getenv('RIOT')
    }
    data = {
        "mapType": "SUMMONERS_RIFT",
        "metadata": "",
        "pickType": "TOURNAMENT_DRAFT",
        "spectatorType": "ALL",
        "teamSize": 5
    }
    response = requests.post(url, params=params, headers=headers, json=data)
    return json.loads(response.text)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$'):
        if message.content == '$nz':
            data = getNZ()
            for count, d in enumerate(data):
                code = '{count} Tournament Code: {d}'.format(count=count + 1, d=d)
                await message.channel.send(code)
        elif message.content == '$solo':
            data = getSolo()
            for count, d in enumerate(data):
                code = '{count} Tournament Code: {d}'.format(count=count + 1, d=d)
                await message.channel.send(code)
        else:
            await message.channel.send('这个XBOX烟谁扔的？（错误指令）')
client.run(os.getenv('TOKEN'))
