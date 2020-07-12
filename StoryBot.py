import discord
from discord.ext import commands
import random
import DNDBotAPI
import mysql.connector
import os
import subprocess
import json
import asyncio


with open('config.json') as json_file:
    data = json.load(json_file)
    token = str(data['token'])
    prefix = str(data['prefix'])


cnx = mysql.connector.connect(user='root', passwd='1234',
                              host='127.0.0.1',
                              database='discordbot',
                              auth_plugin='mysql_native_password')

cursor = cnx.cursor()

client = commands.Bot(command_prefix = prefix)

isBotOn = True

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

STORY_DESCRIPTION = '''This command allows you to create a story with a name and a description. 
                       You need to have a changable word. ex: Noun, Adj, Verb'''

STORY_HELP = "[Story Name] [Story Description]" 
@client.command(aliases=['story'], description=STORY_DESCRIPTION, help=STORY_HELP)
async def create_story(ctx, story_name, story_draft):

    author_id = ctx.message.author.id
    author_avatar = ctx.message.author.avatar_url
    author = str(ctx.message.author)
    noun_count = 0
    verb_count = 0
    adj_count = 0
    can_create_embed = False
    split_draft = story_draft.split()
    embed_color = generate_random_hex_color()

    for x in (range(0, len(split_draft))):


        if (split_draft[x].__contains__("Noun")):
            can_create_embed = True
            noun_count += 1

        elif (split_draft[x].__contains__("Adjective")):

            can_create_embed = True
            adj_count += 1

        elif (split_draft[x].__contains__("Verb")):

            can_create_embed = True
            verb_count += 1

    if (can_create_embed == True):
        
        #SQL Statements to insert the values into the database
        cursor.execute(f'''INSERT INTO createdstories
            VALUES ('{story_name}', '{story_draft}', '{author}', '{author_id}', '{author_avatar}', '{embed_color}');''')
        cnx.commit()

        #Starting the embed
        embed=discord.Embed(title=f'Story Name: {story_name}', description=story_draft, color=embed_color)
        embed.set_author(icon_url=author_avatar, name=f'Author: {author}')
        embed.set_footer(text=f"Nouns: {noun_count}, Adjectives: {adj_count}, Verbs: {verb_count}")
        await (ctx.send(embed=embed))

    else:
        await(ctx.send(f'The story: |{story_name}| does not contain a changeable word...'))
        pass


# -----------------------------------------------------
# - Purpose: Retrieves the most recent story created in the database
# - Parameters: 
# -     ctx = context (aut defined by program)
# -----------------------------------------------------

LAST_STORY = "Gets the last story that was created in the Database"
@client.command(aliases=['last'], description=LAST_STORY)
async def last_story(ctx):

    cursor.execute("SELECT * FROM createdstories;")
    story_table = cursor.fetchall()
    total_stories = len(story_table) - 1

    story_name = story_table[total_stories][0]
    story_draft = story_table[total_stories][1]
    author = story_table[total_stories][2]
    author_id = story_table[total_stories][3]
    author_avatar = story_table[total_stories][4]
    embed_color = int(story_table[total_stories][5])

    embed = discord.Embed(title=f'Story Name: {story_name}', description="Story: " + story_draft, color=embed_color)
    embed.set_author(icon_url=author_avatar, name=f'Author: {author}')
    embed.set_footer(text="The recent recorded story")
    await (ctx.send(embed=embed))


# -----------------------------------------------------
# - Purpose: Lists the current stories
# - Parameters: 
# -     ctx = context (aut defined by program)
# -----------------------------------------------------

@client.command(aliases=['list'])
async def list_stories(ctx):

    cursor.execute("SELECT * FROM createdstories;")
    story_table = cursor.fetchall()
    total_stories = len(story_table)

    if (total_stories < 10):
        value = -1
        for x in range(0, total_stories):
            value+=1
            story_name = story_table[value][0]
            story_draft = story_table[value][1]
            author = story_table[value][2]
            author_id = story_table[value][3]
            author_avatar = story_table[value][4]
            embed_color = int(story_table[value][5])

            embed = discord.Embed(title=f'Story Name: {story_name}', description="Story: " + story_draft, color=embed_color)
            embed.set_author(icon_url=author_avatar, name=f'Author: {author}')
            embed.set_footer(text=f"{value} story in the list")
            await (ctx.send(embed=embed))

    elif (total_stories > 10):
        value = random.randint(0, total_stories-10)
        for x in range(0, 10):
            value+=1
            story_name = story_table[value][0]
            story_draft = story_table[value][1]
            author = story_table[value][2]
            author_id = story_table[value][3]
            author_avatar = story_table[value][4]
            embed_color = int(story_table[value][5])
            
            embed = discord.Embed(title=f'Story Name: {story_name}', description="Story: " + story_draft, color=embed_color)
            embed.set_author(icon_url=author_avatar, name=f'Author: {author}')
            embed.set_footer(text=f"{value} story in the list")
            await (ctx.send(embed=embed))

# -----------------------------------------------------
# - Purpose: Allows the user to modify the stories inserted into the database
# - Parameters: 
# -     ctx = context (aut defined by program)
# -     story_name = the name of the story
# -----------------------------------------------------

@client.command(aliases=['modify'])
async def modify_story(ctx, story_name):

        is_valid = False
        valid_drafts = []

        cursor.execute("SELECT StoryName FROM createdstories;")
        db_drafts = cursor.fetchall()

        draft_index = 0
        for x in range(0, len(db_drafts)):
            valid_drafts.append(db_drafts[x][0])
            if db_drafts[x][0] == story_name:
                draft_index = x
                break


        if valid_drafts.__contains__(story_name):
            await ctx.send(f'{story_name} is considered a valid story name')
            is_valid = True

        else:
            await ctx.send(f'{story_name} is not considered a valid story name')
            
        
        if (is_valid == True):
            cursor.execute("SELECT StoryDraft FROM createdstories;")
            story_drafts = cursor.fetchall()
            await ctx.send(f'Story description: {story_drafts[draft_index][0]}')

            splited = story_drafts[draft_index][0].split()
            for x in (range(0, len(splited))):

                if (splited[x].__contains__("Noun")):
                    splited.remove("Noun")
                    await ctx.send(f'Enter the Noun...')

                    def check(m):
                        return m.content

                    try:
                        message = await client.wait_for('message', timeout=10.0, check=check)
                        input = '{.content}'.format(message)
                        print(input)
                        
                    except asyncio.TimeoutError:
                        await ctx.send("You took too long...")
                    else:
                        await ctx.send(f"You entered: {input}")
                        splited.insert(x, input)
        
                elif (splited[x].__contains__("Adjective")):
                    splited.remove("Adjective")
                    await ctx.send(f'Enter the Adjective...')

                    def check(m):
                        return m.content

                    try:
                        message = await client.wait_for('message', timeout=10.0, check=check)
                        input = '{.content}'.format(message)
                        print(input)
                        
                    except asyncio.TimeoutError:
                        await ctx.send("You took too long...")
                    else:
                        await ctx.send(f"You entered: {input}")
                        splited.insert(x, input)

                elif (splited[x].__contains__("Verb")):
                    splited.remove("Verb")
                    await ctx.send(f'Enter the Verb...')

                    def check(m):
                        return m.content

                    try:
                        message = await client.wait_for('message', timeout=10.0, check=check)
                        input = '{.content}'.format(message)
                        
                    except asyncio.TimeoutError:
                        await ctx.send("You took too long...")
                    else:
                        await ctx.send(f"You entered: {input}")
                        splited.insert(x, input)
                    
        finalized = ' '.join(splited)
        await ctx.send(finalized)

client.run(token)