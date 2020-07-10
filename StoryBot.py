import discord
from discord.ext import commands
import random
import DNDBotAPI
import mysql.connector
import os
import subprocess
import json


with open('config.json') as json_file:
    data = json.load(json_file)
    #token = str(data['config'][0]['token'])
    token = str(data['token'])
    prefix = str(data['prefix'])


cnx = mysql.connector.connect(user='root', passwd='1234',
                              host='127.0.0.1',
                              database='discordbot',
                              auth_plugin='mysql_native_password')

cursor = cnx.cursor()




client = commands.Bot(command_prefix = prefix)

isBotOn = True

current_story = ""
current_story_name = ""
created_by = ""
author_id = ""

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def generate_random_hex_color():
    r = random.randint(0,254)
    g = random.randint(0,254)
    b = random.randint(0,254)
    return int(rgb_to_hex((r, g, b)), 16)

# -----------------------------------------------------
# - Purpose: Allows the user to create a custom story object
# - Parameters: 
# -     ctx = context (aut defined by program)
# -     userstory = the text that the user inputs to create the story to be modified
# -     storyname = the name of the story object
# -----------------------------------------------------

story_description = "This command allows you to create a story with a name and a description"
story_help = "[Story Name] [Story Description]" 
@client.command(aliases=['story'], description=story_description, help=story_help)
async def create_story(ctx, name, description):

    global current_story
    global current_story_name
    global created_by
    global author_id

    #Gets the users ID and stores it into userid
    author_id = ctx.message.author.id
    author_avatar = ctx.message.author.avatar_url
    author = str(ctx.message.author)
    current_story = description
    current_story_name = name

    cursor.execute(f"INSERT INTO userstories VALUES ('{current_story_name}', {author_id}, '{description}');")
    cnx.commit()
    #Starting the embed
    embed=discord.Embed(title=f'Story Name: {current_story_name}', description=description, color=generate_random_hex_color())
    embed.set_author(icon_url=author_avatar, name=f'Author: {author}')
    embed.set_footer(text="Text for later lol")
    await (ctx.send(embed=embed))


story_description = 'This command creates a story'
@client.command(aliases=['insertsomething'], description=story_description)
async def insert(ctx, changetext, storynamecheck):
    global current_story
    global current_story_name

    #Checking to see if the name matches the actual thing
    if (storynamecheck == current_story_name):
        new_story = current_story.split()
        for x in (range(0, len(new_story))):

            if (new_story[x].__contains__("Noun")):
                new_story.remove("Noun")
                new_story.insert(x, changetext)
                current_story = ' '.join(new_story)
                await(ctx.send(current_story))
                break

            elif (new_story[x].__contains__("Adjective")):
                new_story.remove("Adjective")
                new_story.insert(x, changetext)
                current_story = ' '.join(new_story)
                await(ctx.send(current_story))
                break

            elif (new_story[x].__contains__("Verb")):
                new_story.remove("Verb")
                new_story.insert(x, changetext)
                current_story = ' '.join(new_story)
                await(ctx.send(current_story))
                break

userid_description = "shows the users guild ID"
@client.command(aliases=['user'], description=userid_description)
async def current_story(ctx):
    global current_story
    global current_story_name
    await(ctx.send(current_story_name + ": " + current_story))

@client.command(aliases=['emb'])
async def test_embed(ctx, test, description):
    embed = discord.Embed(title=test, description=description)
    await (ctx.send(embed=embed))

client.run(token)