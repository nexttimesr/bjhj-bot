from threading import Thread
import discord
from flask import Flask
from discord.ext import commands
from discord import FFmpegPCMAudio
from dotenv import load_dotenv
import os
import requests
import json
import openai
from transformers import GPT2TokenizerFast
from keep_alive import keep_alive

# app = Flask(__name__)

load_dotenv()

intent = discord.Intents.default()
intent.members = True
intent.message_content = True

client = commands.Bot(command_prefix='$', intents=intent, help_command=None)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.command(pass_context = True)
async def uyuki(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        source = FFmpegPCMAudio('static/sounds/uyuki.m4a')
        player = voice.play(source)
    else:
        await ctx.send("You are not in a channel.")

@client.command(pass_context = True)
async def leave(ctx):
    if ctx.author.voice:
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("You are not in a channel.")

@client.command(pass_context = True)
async def pause(ctx):
    voice = ctx.voice_client
    if not voice or not voice.is_playing():
        await ctx.send("No audio is playing.")
    elif voice.is_paused():
        return
    voice.pause()


@client.command(pass_context = True)
async def unpause(ctx):
    voice = ctx.voice_client
    if not voice or not voice.is_paused():
        await ctx.send("No audio is paused.")
    elif voice.is_playing():
        return
    voice.resume()

@client.command(pass_context = True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    voice.stop()



@client.command()
async def nz(ctx):
    data = get_code(nz)
    await ctx.channel.send('Tournament Code: {d}'.format(d=data))

@client.command()
async def solo(ctx):
    data = get_code(solo)
    await ctx.channel.send('Tournament Code: {d}'.format(d=data))


@client.command()
async def aram(ctx):
    data = get_code(aram)
    await ctx.channel.send('Tournament Code: {d}'.format(d=data))


def get_code(game_type):
    url = 'https://americas.api.riotgames.com/lol/tournament/v5/codes'
    count = 1
    team = 1 if game_type == "solo" else 5
    map_type = "HOWLING_ABYSS" if game_type == "aram" else "SUMMONERS_RIFT"
    pick = "TOURNAMENT_DRAFT" if game_type == "nz" else "BLIND_PICK"

    params = {'count': count, 'tournamentId': os.getenv('ID')}
    headers = {'X-Riot-Token': os.getenv('RIOT'), "Origin": "https://developer.riotgames.com"}
    data = {
        "mapType": map_type,
        "metadata": "",
        "pickType": pick,
        "spectatorType": "ALL",
        "teamSize": team
    }
    response = requests.post(url, headers=headers, params=params, json=data)
    return json.loads(response.text)[0]


@client.command()
async def image(ctx, *, prompt):
    openai.organization = "org-D0jecI2YDT8MaOLwmOPYST4J"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.Model.list()
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    image_url = response['data'][0]['url']
    await ctx.message.channel.send(image_url)


@client.command()
async def text(ctx, *, prompt):
    print(prompt)
    openai.api_key = os.getenv("OPENAI_API_KEY")

    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    encoded = tokenizer.encode(prompt)
    tokens = 4000 - len(encoded)
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.6,
        max_tokens=tokens,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1
    )
    data = response.get('choices')[0].get('text')
    if len(data) > 2000:
        left = 0
        right = 1900
        while right < len(data):
            await ctx.message.channel.send(data[left:right])
            left += 1900
            right += 1900
        await ctx.message.channel.send(data[left:])
    else:
        await ctx.message.channel.send(data)



@client.event
async def on_message(message):
    try:
        if message.author == client.user:
            return
        if message.content.startswith('$'):
            content = message.content
            if content == '$ltl':
                await message.channel.send('还有你A了多少下塔')
            elif content == '$zl':
                await message.channel.send('https://www.op.gg/summoners/na/meomei')
            elif content == '$ls':
                await message.channel.send('打dang不溜')
            elif content == '$help':
                await message.channel.send(
                    '$help: list all available commands\n$uyuki: play audio\n$pause: pause audio\n$unpause: unpause audio\n$stop: stop audio\n$leave: leave channel\n$text <prompt>: generate text based on prompt\n$image '
                    '<prompt>: generate image based on text (prompt)\n$nz: 5v5 Tournament Draft\n$solo: 1v1 Blind '
                    'Pick \n$aram: ARAM\n$ls, $ltl, $zl '
                )
    except Exception as e:
        print(e)
        await message.channel.send('出了点错')
    await client.process_commands(message)

if __name__ == '__main__':
    keep_alive()
    client.run(os.getenv('TOKEN'))