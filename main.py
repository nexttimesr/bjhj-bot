import discord
from dotenv import load_dotenv
import os
import requests
import json
from keep_alive import keep_alive

load_dotenv()
intent = discord.Intents.default()
intent.members = True
intent.message_content = True

client = discord.Client(intents=intent)

def getCodes(type):
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/codes'

    count = 20
    team = 5
    if type == 'solo':
        team = 1
        count = 2
    map_type = "SUMMONERS_RIFT"
    if type == 'aram':
        map_type = "HOWLING_ABYSS"
    pick = "BLIND_PICK"
    if type == 'aram':
        pick = 'ALL_RANDOM'
    elif type == 'nz':
        pick = 'TOURNAMENT_DRAFT'

    params = {
        'count': count,
        'tournamentId': 7528
    }
    headers = {
        'X-Riot-Token': os.getenv('RIOT')
    }
    data = {
              "mapType": map_type,
              "metadata": "",
              "pickType": pick,
              "spectatorType": "ALL",
              "teamSize": team
            }
    response = requests.post(url, headers=headers, params=params, json=data)
    return json.loads(response.text)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$'):
        if message.content == '$nz' or message.content == '$solo' or message.content == '$aram':
            data = getCodes(message.content[1:])
            for count, d in enumerate(data):
                code = '{count} Tournament Code: {d}'.format(count=count + 1, d=d)
                await message.channel.send(code)
        elif message.content == '$ltl':
            await message.channel.send('还有你A了多少下塔')
        elif message.content == '$zl':
            await message.channel.send('https://www.op.gg/summoners/na/meomei')
        elif message.content == '$ls':
            await message.channel.send('打dang不溜')
        else:
            await message.channel.send('这个XBOX烟谁扔的？')


while __name__ == '__main__':
    try:
        keep_alive()
        client.run(os.getenv('TOKEN'))
    except discord.errors.HTTPException as e:
        print(e)
        print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
        os.system('kill 1')

