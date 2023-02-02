from flask import Flask
from threading import Thread
import discord
from dotenv import load_dotenv
import os
import requests
import json
import openai

app = Flask(__name__)
app.env = "development"

load_dotenv()

intent = discord.Intents.default()
intent.members = True
intent.message_content = True

client = discord.Client(intents=intent)


def get_code(game_type):
    url = 'https://americas.api.riotgames.com/lol/tournament/v4/codes'
    count = 1
    team = 5
    if game_type == 'solo':
        team = 1
    map_type = "SUMMONERS_RIFT"
    if game_type == 'aram':
        map_type = "HOWLING_ABYSS"
    pick = "BLIND_PICK"
    if game_type == 'aram':
        pick = 'ALL_RANDOM'
    elif game_type == 'nz':
        pick = 'TOURNAMENT_DRAFT'

    params = {'count': count, 'tournamentId': os.getenv('ID')}
    headers = {'X-Riot-Token': os.getenv('RIOT')}
    data = {
        "mapType": map_type,
        "metadata": "",
        "pickType": pick,
        "spectatorType": "ALL",
        "teamSize": team
    }
    response = requests.post(url, headers=headers, params=params, json=data)
    return json.loads(response.text)


def generate_image(prompt):
    openai.organization = "org-D0jecI2YDT8MaOLwmOPYST4J"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.Model.list()
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    image_url = response['data'][0]['url']
    return image_url


def generate_text(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.6,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1
    )
    return response.get('choices')[0].get('text')


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    try:
        if message.author == client.user:
            return

        if message.content.startswith('$'):
            content = message.content
            if content == '$nz' or content == '$solo' or content == '$aram':
                data = get_code(content[1:])[0]
                await message.channel.send('Tournament Code: {d}'.format(d=data))
            elif content.startswith('$image '):
                if len(content) <= 8:
                    await message.channel.send('Prompt too short!')
                    return
                prompt = content[7:]
                data = generate_image(prompt)
                await message.channel.send(data)
            elif content.startswith('$text '):
                if len(content) < 7:
                    await message.channel.send('Prompt too short!')
                    return
                prompt = content[6:]
                data = generate_text(prompt)
                if len(data) > 2000:
                    left = 0
                    right = 1900
                    while right < len(data):
                        await message.channel.send(data[left:right])
                        left += 1900
                        right += 1900
                    await message.channel.send(data[left:])
                else:
                  await message.channel.send(data)
            elif content == '$ltl':
                await message.channel.send('还有你A了多少下塔')
            elif content == '$zl':
                await message.channel.send('https://www.op.gg/summoners/na/meomei')
            elif content == '$ls':
                await message.channel.send('打dang不溜')
            elif content == '$help':
                await message.channel.send(
                    '$help: list all available commands\n$text <prompt>: generate text based on prompt\n$image '
                    '<prompt>: generate image based on text (prompt)\n$nz: 5v5 Tournament Draft\n$solo: 1v1 Blind '
                    'Pick \n$aram: ARAM\n$ls, $ltl, $zl '
                )
            else:
                await message.channel.send('这个XBOX烟谁扔的？')
    except Exception as e:
        print(e)
        await message.channel.send('出了点错')


def run():
    def start():
        client.run(os.getenv('TOKEN'))
    t = Thread(target=start)
    t.start()


