import discord
from discord.ext import commands
import asyncio
from discord_slash import *
import sqlite3
import time
import os
import sqlite3
from datetime import datetime
import os
from pytube import YouTube
import os
import io
import requests
import datetime
from waitress import serve
import random
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import *
from discord_slash.model import ButtonStyle
from youtubesearchpython import *
import uuid
import threading
from flask import *
db={}
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['FLASK_ENV']="development"
def cookie_auth(resp):
    cookie = resp.cookies.get("ssid")
    if not cookie:
        return False
    if not cookie in users_panel_web:
        return False
    user = users_panel_web[cookie]
    return user
@app.route('/<gid>/skip', methods=["POST"])
def _web_skip(gid):
    user = cookie_auth(request)
    if not user:
        return 'Unauthorized!', 401
    voice = discord.utils.get(client.voice_clients, guild=user.guild)
    if voice:
        if len(playqueue[user.guild.id])>0:
                voice.stop()

    return "OK"
@app.route('/<gid>/loop', methods=["POST"])
def _web_loop(gid):
    user = cookie_auth(request)
    if not user:
        return 'Unauthorized!', 401
    voice = discord.utils.get(client.voice_clients, guild=user.guild)
    if voice:
        if loop_bool[user.guild.id]==True:
            loop_bool[user.guild.id]=False
        else:
            loop_bool[user.guild.id] = True

    return "OK"
@app.route('/<gid>/pause', methods=["POST"])
def _web_pause(gid):
    user = cookie_auth(request)
    if not user:
        return 'Unauthorized!', 401
    voice = discord.utils.get(client.voice_clients, guild=user.guild)
    if voice:
        if voice.is_paused():
            voice.resume()
        else:
            voice.pause()
    return "OK"
@app.route('/<gid>/music_status', methods=["GET"])
def status(gid):
    user = cookie_auth(request)
    if not user:
        return 'Unauthorized!', 401
    voice = discord.utils.get(client.voice_clients, guild=user.guild)
    connected=False
    ispaused=False
    islooped=False
    if voice:
        connected=True
        islooped=loop_bool[user.guild.id]
        ispaused=voice.is_paused()
    resp={"connected":connected,
          "ispaused":ispaused,
          "islooped":islooped}
    return jsonify(resp)
@app.route('/<gid>/playlist', methods=["GET"])
def playlist(gid):
    user=cookie_auth(request)
    if not user:
        return 'Unauthorized!', 401
    guild_id=user.guild.id
    res=playqueue[guild_id]
    return jsonify(res)
@app.route('/<gid>/musicpanel', methods=["GET"])
def index(gid):
    id = request.args.get("id")
    if not id:
        return 'Unauthorized!', 401
    if not id in users_panel_web:
        return 'Unauthorized!', 401
    user=users_panel_web[id]
    icon=user.guild.icon_url
    user_avatar=user.avatar_url
    if not icon:
        icon="data:image/png;base64,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"
    resp = make_response(render_template("index.html",avatar_url=user_avatar, guild_name=str(user.guild.name), user_name=str(user.name), guild_id=f'{str(user.guild.id)}', guild_icon=icon))
    resp.set_cookie('ssid', id, path=f"/{gid}")
    return resp

threading.Thread(target = lambda: serve(app, host='0.0.0.0', port=443)).start()
def getvoice(ctx):
    return discord.utils.get(client.voice_clients, guild=ctx.guild)
async def has_ban(ctx):
    if 'ban_role' in db[ctx.guild.id].keys():
        for role in ctx.author.roles:
            if role.id == int(db[ctx.guild.id]['ban_role']):
                await ctx.reply(":x: You don't have permissions to run this command :x:", hidden=True)
                return True
    return False
def ch_send(ctx):
    if ctx.guild.id in db.keys():
        if "musicch" in db[ctx.guild.id].keys():
            channel= client.get_channel(db[ctx.guild.id]['musicch'])
            return channel
    return ctx.message.channel
async def is_admin(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.reply(":x: You don't have permissions to run this command :x:", hidden=True)
        return False
    return True
def reset_music(guild):
    playqueue[guild.id] =[]
    loop_bool[guild.id] = False
def checkuserperm(message,perm):
    if perm==[]:
        return True
    for permision in message.author.roles.id:
        if permision.id in perm:
            return True
    return False

#play music
async def add_queue(ctx, music):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not ctx.author.voice:
        await ctx.reply(":exclamation: Aby wykonać tą komendę musisz być na kanale głosowym", hidden=True)
        return
    if voice:
        if not voice.channel == ctx.author.voice.channel:
            await ctx.reply(":exclamation: Aby wykonać tą komendę musisz być na tym samym kanale co winbot", hidden=True)
            return

    video_found = VideosSearch(music, limit=1)
    if video_found.result()['result'] == []:
            await ctx.reply(":bangbang: Nie odnaleziono danego utworu ", hidden=True)
            return
    music_data=video_found.result()['result'][0]
    if len(playqueue[ctx.guild.id]) == 0:
        playqueue[ctx.guild.id].append(music_data)
        musicinfo = discord.Embed(title=":musical_note:",
                                  description="Uruchamianie muzyki na kanale " + str(ctx.author.voice.channel),
                                  color=0xcc8400)
        musicinfo.add_field(name="Nazwa utworu", value="["+str(music_data['title'])+"]("+str(music_data['link'])+")", inline=True)
        musicinfo.set_thumbnail(url=music_data['thumbnails'][0]['url'])
        musicinfo.set_footer(text='Komenda wywołana przez: ' + ctx.author.name + '\n@Na licencji P4tkry',
                             icon_url=str(author.avatar_url))
        await ch_send(ctx).send(embed=musicinfo)
        await gotochannel(ctx)
    else:
        playqueue[ctx.guild.id].append(music_data)
        musicinfo = discord.Embed(title=":arrow_heading_up: ", description="Dodano utwór do kolejki", color=0x0073cf)
        musicinfo.add_field(name="Nazwa utworu", value="["+str(music_data['title'])+"]("+str(music_data['link'])+")",
                            inline=False)
        musicinfo.add_field(name="Numer w kolejce", value=str(len(playqueue[ctx.guild.id])),
                            inline=False)
        musicinfo.set_thumbnail(url=music_data['thumbnails'][0]['url'])
        musicinfo.set_footer(text='Komenda wywołana przez: ' + ctx.author.name + '\n@Na licencji P4tkry',
                             icon_url=str(author.avatar_url))
        await ch_send(ctx).send(embed=musicinfo)
async def gotochannel(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    user_voice_channel = ctx.author.voice.channel
    if not voice:
        await user_voice_channel.connect()
    play(ctx)
def play(ctx):
    if not len(playqueue[ctx.guild.id])==0:
        print("play")
        ytmusic = YouTube(playqueue[ctx.guild.id][0]['link']).streams.filter(only_audio=True).first()
        if not os.path.isfile("music/" + str(ytmusic.default_filename)):
            ytmusic.download(filedir+"/music")
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice:
            try:
                voice.play(discord.FFmpegPCMAudio("music/" + str(ytmusic.default_filename)), after=lambda x: next(ctx))
            except:
                pass
def next(ctx):
    global playqueue
    if not len(playqueue[ctx.guild.id])==0:
        if loop_bool[ctx.guild.id]==False:
            del playqueue[ctx.guild.id][0]
        else:
            first=playqueue[ctx.guild.id][0]
            playqueue[ctx.guild.id].append(first)
            del playqueue[ctx.guild.id][0]
        play(ctx)
async def get_queue(ctx):
    voice =getvoice(ctx)
    is_paused=False
    if voice:
        is_paused=voice.is_paused()
    if is_paused:
        playlist_embed = discord.Embed(title=":play_pause:",
                                       description="Kolejka wstrzymana", color=0xfff314)
    elif loop_bool[ctx.guild.id]:
        playlist_embed = discord.Embed(title=":repeat:",
                                       description="Zloopowana kolejka", color=0xfff314)
    else:
        playlist_embed = discord.Embed(title=":twisted_rightwards_arrows:",
                                       description="Informacje o kolejce odtwarzania", color=0xfff314)

    playlist_embed.set_footer(text='@Na licencji P4tkry',
                                  icon_url=str(author.avatar_url))
    number=0
    for muzyka in playqueue[ctx.guild.id]:
        number=number+1
        playlist_embed.add_field(name=str(number), value=f"[```{str(muzyka['title'])}```]({str(muzyka['link'])})", inline=False)

    await ch_send(ctx).send(embed=playlist_embed)


#music functions
async def skip(ctx, number_of_tracks):
    global playqueue
    if number_of_tracks <1:
        await ctx.reply(":warning: Nieprawidłowa liczba utworów do pominięcia", hidden=True)
        return
    pominieto=""
    if number_of_tracks == 1:
        pominieto="Pominięto 1 utwór"
    elif number_of_tracks >1 and number_of_tracks<5:
        pominieto="Pominięto "+str(number_of_tracks)+" utwory"
    elif number_of_tracks > 4 and number_of_tracks < 22:
        pominieto="Pominięto "+str(number_of_tracks)+" utworów"
    elif int(str(number_of_tracks)[-1]) > -1 and int(str(number_of_tracks)[-1]) < 2:
        pominieto="Pominięto "+str(number_of_tracks)+"utworów"
    elif int(str(number_of_tracks)[-1]) > 1 and int(str(number_of_tracks)[-1]) < 5:
        pominieto="Pominięto "+str(number_of_tracks)+"utwory"
    elif int(str(number_of_tracks)[-1]) > 4 and int(str(number_of_tracks)[-1]) < 10:
        pominieto="Pominięto "+str(number_of_tracks)+"utworów"


    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        pozostalo = len(playqueue[ctx.guild.id]) - number_of_tracks
        if pozostalo < 0:
            await ctx.reply(":warning: Nie można pominąć więcej utworów niż jest na liście odtwarzania", hidden=True)
            return
        elif pozostalo == 0:
            skip_embed = discord.Embed(title=":fast_forward:",
                                       description=pominieto,
                                       color=0xFf1919)
            skip_embed.add_field(name="Kolejny utwór", value="Brak kolejnych utworów", inline=True)
            skip_embed.set_footer(text='Komenda wywołana przez: ' + ctx.author.name + '\n@Na licencji P4tkry',
                                  icon_url=str(author.avatar_url))
            await ch_send(ctx).send(embed=skip_embed)
            voice.stop()
        else:
            skip_embed = discord.Embed(title=":fast_forward:",
                                       description=pominieto,
                                       color=0xFf1919)
            print(playqueue)
			skip_embed.add_field(name="Kolejny utwór",
			value="[" + str(playqueue[ctx.guild.id][number_of_tracks]['title']) + "](" + str(playqueue[number_of_tracks]['link']) + ")", inline=True)
            skip_embed.set_thumbnail(url=playqueue[ctx.guild.id][number_of_tracks]['thumbnails'][0]['url'])
            skip_embed.set_footer(text='Komenda wywołana przez: ' + ctx.author.name + '\n@Na licencji P4tkry',
                                  icon_url=str(author.avatar_url))
            await ch_send(ctx).send(embed=skip_embed)
            if number_of_tracks != 1:
                if loop_bool[ctx.guild.id]==False:
                    del playqueue[ctx.guild.id][number_of_tracks-1]
                else:
                    first = playqueue[ctx.guild.id][number_of_tracks-1]
                    playqueue[ctx.guild.id].append(first)
                    del playqueue[ctx.guild.id][number_of_tracks-1]
            voice.stop()


    else:
        await ctx.reply(":warning: Nie można wykonać tej komendy ponieważ winbot nie jest na żadnym kanale głosowym", hidden=True)

async def loop(ctx):
    global loop_bool, loopedmusic
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        if loop_bool[ctx.guild.id] == False:
            loop_bool[ctx.guild.id] = True
            musicinfo = discord.Embed(title=":infinity:",
                                      description="Kolejka została zapętlona",
                                      color=0x24242E)
            musicinfo.set_footer(text='Komenda wywołana przez: ' + ctx.author.name + '\n@Na licencji P4tkry',
                                 icon_url=str(author.avatar_url))
            await ch_send(ctx).send(embed=musicinfo)
        else:
            loop_bool[ctx.guild.id] = False
            musicinfo = discord.Embed(title=":arrow_right_hook:",
                                      description="Wyłączono zapętlanie kolejki",
                                      color=0x24242E)
            musicinfo.set_footer(text='Komenda wywołana przez: ' + ctx.author.name + '\n@Na licencji P4tkry',
                                 icon_url=str(author.avatar_url))
            await ch_send(ctx).send(embed=musicinfo)
    else:
        await ctx.reply(":warning: Nie można wykonać tej komendy ponieważ winbot nie jest na żadnym kanale głosowym",
                    hidden=True)

async def leave(guild):
    voice = discord.utils.get(client.voice_clients, guild=guild)
    if voice:
        await voice.disconnect()
    reset_music(guild)

async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.pause()
    stopmusic = discord.Embed(title=":pause_button:", description="Zatrzymano odtwarzanie", color=0xff0000)
    stopmusic.add_field(name="Zatrzymano", value="Odtwarzanie muzyki zostało zatrzymane", inline=False)
    stopmusic.set_footer(text='Komenda wywołana przez: ' + ctx.author.name + '\n@Na licencji P4tkry',
                         icon_url=str(author.avatar_url))
    return stopmusic

async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.resume()
    stopmusic = discord.Embed(title=":arrow_forward:", description="wznowiono odtwarzanie", color=0xff0000)
    stopmusic.add_field(name="Zatrzymano", value="Odtwarzanie muzyki zostało wznowione", inline=False)
    stopmusic.set_footer(text='Komenda wywołana przez: ' + ctx.author.name + '\n@Na licencji P4tkry',
                         icon_url=str(author.avatar_url))
    return stopmusic

# async def deleteelement(message):
#     if not len(playqueue)==0:
#         try:
#             number=int(str(message.content).split(" ")[1])-1
#         except:
#             await message.channel.send(":exclamation: Błędny argument!!!", delete_after=30)
#             return
#         usunietezplaylisty_embed = discord.Embed(title=":arrow_heading_down:", description="Usunięto z kolejki odtwarzania",
#                                                  color=0x8140f)
#         usunietezplaylisty_embed.add_field(name=str(number+1),
#                                            value="[" + str(playqueue[number][1]) + "](" + str(playqueue[number][0]) + ")",
#                                            inline=False)
#         usunietezplaylisty_embed.set_footer(text='Komenda wywołana przez: ' + message.author.name + '\n@Na licencji P4tkry',
#                                             icon_url=str(author.avatar_url))
#         try:
#             del playqueue[number]
#             voice = discord.utils.get(client.voice_clients, guild=message.guild)
#             if voice:
#                 voice.stop()
#         except:
#             await message.channel.send(":exclamation: Błędny argument!!!", delete_after=30)
#             return
#
#         await ch_send(ctx).send(embed=usunietezplaylisty_embed)
#     else:
#         await message.channel.send(":exclamation: Lista jest pusta!!!", delete_after=30)


def get_data(data, klucze):
    numer = 0
    date = {}
    for key in klucze:
        date[key] = data[numer]
        numer = numer + 1
    return date

async def covidinfo(voidship):
    command=str(voidship).lower()
    if command in ["polska", 'dolnośląskie', 'kujawsko-pomorskie', 'lubelskie', 'lubuskie', 'łódzkie', 'małopolskie', 'mazowieckie', 'opolskie', 'podkarpackie', 'podlaskie', 'pomorskie', 'śląskie', 'świętokrzyskie', 'warmińsko-mazurskie', 'wielkopolskie', 'zachodniopomorskie']:
        if command=="polska":
            command="Cały kraj"
        req = requests.get("https://www.arcgis.com/sharing/rest/content/items/153a138859bb4c418156642b5b74925b/data")
        url_content = req.content
        dane = url_content.decode("cp1250")
        linie_danych = dane.split("\r\n")
        linie_danych = linie_danych[:-1]
        tabela = {}
        klucze = linie_danych[0].split(";")
        linie_danych.pop(0)
        for woj in linie_danych:
            tmp = woj.split(";")
            tabela[tmp[0]] = get_data(tmp, klucze)
        covidembed=discord.Embed(title=":biohazard:", description="Informacje dotyczące covid-19", color=0x4B8DCA)
        covidembed.set_thumbnail(url="https://reliefweb.int/sites/reliefweb.int/files/styles/s/public/topic-icons/covid19-icon_0_0_0.png?itok=024FFUqJ")
        covidembed.add_field(name="Województwo",value=str(tabela[command]['wojewodztwo']), inline=False)
        covidembed.add_field(name="Dane na dzień", value=str(tabela[command]['stan_rekordu_na']), inline=False)
        covidembed.add_field(name="Liczba nowych zachorowań", value=str(tabela[command]['liczba_przypadkow']), inline=False)
        covidembed.add_field(name="Liczba nowych zgonów",value=str(tabela[command]['zgony']), inline=False)
        covidembed.set_footer(text='@Na licencji P4tkry', icon_url=str(author.avatar_url))
        return covidembed

async def versioninfo(message):
    aboutversion = discord.Embed(title=":christmas_tree: ",
                                 description="4.0", color=0xF61E29)
    aboutversion.add_field(name="Nazwa update",
                           value="Świąteczny update",
                           inline=False)
    aboutversion.set_thumbnail(url="https://img.freepik.com/darmowe-wektory/realistyczny-transparent-boze-narodzenie-z-galezi-i-czerwonym-tle_69286-232.jpg?size=626&ext=jpg")
    aboutversion.set_footer(text='@Na licencji P4tkry',
                            icon_url=str(author.avatar_url))
    await message.channel.send(embed=aboutversion)

async def deletemsg(message):
    try:
        await message.delete()
    except:
        pass

def generate_music_panel(ctx):
    for user in users_panel_web.keys():
        if users_panel_web[user].id==ctx.author.id and users_panel_web[user].guild.id==ctx.guild.id:
            return user
    pid=uuid.uuid4().hex
    while pid in users_panel_web:
        pid = uuid.uuid4().hex
    users_panel_web[pid] = ctx.author
    return pid
#set variables for code
domain="https://winbot.p4tkry.pl"
users_panel_web={}
filedir=os.getcwd()
client = commands.Bot(command_prefix='!', intents=discord.Intents().all())
slash= SlashCommand(client, sync_commands=True)
musicplaying=""
playqueue={}
loop_bool={}
#author id
patkryid=444547466180689920
@client.event
async def on_ready():
    global author
    print("conected")
    await client.change_presence(activity=discord.Game(name="!help"))
    author = await client.fetch_user(patkryid)
    for guild in client.guilds:
        playqueue[guild.id]=[]
        loop_bool[guild.id]=False
        if not guild.id in db.keys():
            db[guild.id]={}

@client.event
async def on_guild_join(guild):
    print(guild)
    playqueue[guild.id] = []
    loop_bool[guild.id] = False
    if not guild.id in db.keys():
        db[guild.id] = {}




@slash.slash(name="ping",description="ICMP winbot")
async def _ping(ctx: SlashContext):
    start_time = time.time()
    msg = await ctx.reply("```Pinging winbot with 32 bytes of data:```",delete_after=30.0)
    end_time=time.time()
    await msg.edit(content=f"```Pinging winbot with 32 bytes of data:\nReply from winbot: bytes=32 time={round((end_time-start_time)*100)}ms```", delete_after=30.0)

@slash.slash(name="play",description="play music", options=[create_option(name="music",description="music name or url address to youtube video.", option_type=3, required=True)])
async def _play(ctx: SlashContext, music: str):
    if await has_ban(ctx) == False:
        await ctx.reply("done :sunglasses:", delete_after=0.1)
        await add_queue(ctx, music)

@slash.slash(name="skip",description="skip music", options=[create_option(name="number_of_tracks",description="how many songs to skip.", option_type=4, required=False)])
async def _skip(ctx: SlashContext, number_of_tracks: int = 1):
    if await has_ban(ctx) == False:
        await ctx.reply("done :sunglasses:", delete_after=0.1)
        await skip(ctx, number_of_tracks)

@slash.slash(name="loop",description="loop music")
async def _loop(ctx: SlashContext):
    if await has_ban(ctx) == False:
        await ctx.reply("done :sunglasses:", delete_after=0.1)
        await loop(ctx)

@slash.slash(name="queue",description="shows queue")
async def _queue(ctx: SlashContext):
    if await has_ban(ctx) == False:
        await ctx.reply("done :sunglasses:", delete_after=0.1)
        await get_queue(ctx)
@slash.slash(name="covid", description="covid info of day from Poland",
             options=[create_option(
                 name="voivodeship",
                 description="Select a voivodeship from which information about Covid can be obtained.",
                 option_type= 3,
                 required=True,
                 choices=[
                create_choice(
                    name="polska",
                    value="polska"
                  ),
                create_choice(
                    name="dolnośląskie",
                    value="dolnośląskie"
                  ),
                create_choice(
                    name="kujawsko-pomorskie",
                    value="kujawsko-pomorskie"
                  ),
                create_choice(
                    name="lubelskie",
                    value="lubelskie"
                  ),
                create_choice(
                    name="lubuskie",
                    value="lubuskie"
                  ),
                create_choice(
                    name="łódzkie",
                    value="łódzkie"
                  ),
                create_choice(
                    name="małopolskie",
                    value="małopolskie"
                  ),
                create_choice(
                    name="mazowieckie",
                    value="mazowieckie"
                  ),
                create_choice(
                    name="opolskie",
                    value="opolskie"
                  ),
                create_choice(
                    name="podkarpackie",
                    value="podkarpackie"
                  ),

                create_choice(
                    name="podlaskie",
                    value="podlaskie"
                  ),
                create_choice(
                    name="pomorskie",
                    value="pomorskie"
                  ),
                create_choice(
                    name="śląskie",
                    value="śląskie"
                  ),
                create_choice(
                    name="świętokrzyskie",
                    value="świętokrzyskie"
                  ),
                create_choice(
                    name="warmińsko-mazurskie",
                    value="warmińsko-mazurskie"
                  ),
                create_choice(
                    name="wielkopolskie",
                    value="wielkopolskie"
                  ),
                create_choice(
                    name="zachodniopomorskie",
                    value="zachodniopomorskie"
                  )
                 ])])
async def _covidinfo(ctx: SlashContext, voivodeship: str):
    if await has_ban(ctx) == False:
        await ctx.reply(embed=await covidinfo(voivodeship))
@slash.slash(name="leave",description="kick Winbot from voice channel")
async def _leave(ctx: SlashContext):
    if await has_ban(ctx) == False:
        await ctx.reply("done :sunglasses:", delete_after=0.1)
        await leave(ctx.guild)
@slash.slash(name="pause",description="pause music")
async def _leave(ctx: SlashContext):
    if await has_ban(ctx) == False:
        await ctx.reply("done :sunglasses:", delete_after=0.1)
        await ch_send(ctx).send(embed=await pause(ctx))
@slash.slash(name="resume",description="resume music")
async def _resume(ctx: SlashContext):
    if await has_ban(ctx) == False:
        await ctx.reply("done :sunglasses:", delete_after=0.1)
        await ch_send(ctx).send(embed=await resume(ctx))
@slash.slash(name="music_panel",description="open winbot panel on web")
async def _getweb(ctx: SlashContext):
    if await has_ban(ctx) == False:
        buttons = [
            manage_components.create_button(
                style=ButtonStyle.URL,
                label="Open panel",
                url=f"{domain}/{str(ctx.guild.id)}/musicpanel?id={str(generate_music_panel(ctx))}"
            ),
        ]
        button = manage_components.create_actionrow(*buttons)
        await ctx.reply('Winbot panel',components=[button],hidden=True)

@slash.slash(name="set_info_channel",description="set winbot information channel", options=[create_option(name="channel", description="channel to send winbot informations", option_type=7, required=True)])
async def _set_winbot_channel(ctx: SlashContext, channel):
    if await has_ban(ctx) == False:
        if await is_admin(ctx) == True:
            if type(channel) == discord.TextChannel:
                db[ctx.guild.id]['musicch'] = channel.id

                await ctx.reply(f":wrench: **successfully** set channel {channel.mention} as informational for winbot.", hidden=True)
            else:
                await ctx.reply(":warning: Channel must be a text channel :warning:", hidden=True)

@slash.slash(name="set_ban_role",description="set the role for which winbot commands will not be supported", options=[create_option(name="role", description="ban role", option_type=8, required=True)])
async def _set_winbot_ban_role(ctx: SlashContext, role):
    if await has_ban(ctx) == False:
        if await is_admin(ctx) == True:
            db[ctx.guild.id]['ban_role']=role.id
            await ctx.reply(f":wrench: **successfully** set {role.mention} as a ban role for winbot.", hidden=True)

# @client.event
# async def on_voice_state_update(member, before, after):
#     voice = discord.utils.get(client.voice_clients, guild=member.guild)
#     if voice:
#         if before.channel != None and after.channel == None:
#             if voice.channel.id == before.channel.id:
#                 channel = client.get_channel(voice.channel.id)
#                 members=channel.members
#                 if len(members)==1:
#                     await asyncio.sleep(60*5)
#                     await voice.disconnect()
#                     reset_music()


#WEB SECTION


client.run(os.environ['KEY'])




