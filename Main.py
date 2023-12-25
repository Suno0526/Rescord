# Import libraries:
import discord as Discord;
import json as JSON;
import os as OS;

from datetime import datetime as DateTime;
from discord.ext import commands as Commands;


# Open our JSON data:
with open("Information.json", "r") as Data:
    Data = JSON.load(Data)

Debug = Data["Debug"]


# Create some global variables:
Client = Commands.Bot(command_prefix = ";", intents = Discord.Intents.all(), help_command = None)


# Let the world know we're ready:
@Client.event
async def on_ready():
    print("Ready!")


# Create some commands:
@Client.command()
async def help(Context : Commands.Context):
    Embed = Discord.Embed(title = "Help",
                          description = "Here's a list of commands you can use with this bot.",
                          color = Discord.Color.random())

    Embed.add_field(name = "save", value = "Saves your server's JSON to our database.", inline = False)
    Embed.add_field(name = "restore", value = "Restores your server using JSON from our database.", inline = False)
    Embed.add_field(name = "delete", value = "Deletes your server's JSON from our database.", inline = False)

    await Context.send(embed = Embed)

@Client.command()
async def save(Context : Commands.Context):
    Embed = Discord.Embed(title = "JSON Recovery",
                          description = "Your entire server has been backed up by a 1:1 JSON file. \n* To restore it, please run **;restore** or **;recover**.",
                          color = Discord.Color.random())
    
    Guild = Context.guild

    try:
        OS.remove("./Servers/{Guild.id}.json")

    except FileNotFoundError:
        pass

    Server = {
        "Created" : DateTime.now().strftime('%Y-%m-%d %H:%M:%S'),

        "Inactive-Channel" : Guild.afk_channel,
        "Inactive-Timeout" : Guild.afk_timeout,

        "System-Messages" : Guild.system_channel,
    
        "Template-Description" : Guild.description,
        "Template-Title" : Guild.name,

        "Send-Welcome-Messages" : Guild.system_channel_flags.join_notifications,
        "Send-Boost-Messages" : Guild.system_channel_flags.premium_subscriptions,

        "Name" : Guild.name,
        "ID" : Guild.id,
        
        "Channels" : [],
        "Voice-Channels" : [],
        "Roles" : [],
        "Categories" : []
    }

    with open(f"./Servers/{Guild.id}.json", "w") as Storage:
        JSON.dump(Server, Storage, indent = 4)

    for Channel in Guild.channels:
        if isinstance(Channel, Discord.TextChannel):
            Server["Channels"].append({
                "Name" : Channel.name,
                "ID" : Channel.id,
                "Type" : Channel.type,
                "Position" : Channel.position,
                "Category" : Channel.category,
                "NSFW" : Channel.is_nsfw(),
                "Slowmode" : Channel.slowmode_delay,
                "Topic" : Channel.topic
            })

        elif isinstance(Channel, Discord.VoiceChannel):
            Server["Voice-Channels"].append({
                "Name" : Channel.name,
                "ID" : Channel.id,
                "Type" : Channel.type,
                "Position" : Channel.position,
                "Category" : Channel.category,
                "Bitrate" : Channel.bitrate,
                "User-Limit" : Channel.user_limit
            })

    for Role in Guild.roles:
        Bot = Guild.get_member(Client.user.id)

        if Bot.guild_permissions.administrator == True:
            if Role.position < Bot.top_role.position:
                    try:
                        if Role.name != "@everyone":
                            Server["Roles"].append({
                                "Name" : Role.name,
                                "ID" : Role.id,
                                "Position" : Role.position,
                                "Hoisted" : Role.hoist,
                                "Mentionable" : Role.mentionable
                            })

                    except:
                        if Role.name != "@everyone":
                            await Context.send(f"**{Role.name}** is managed by an integration.")

    for Category in Guild.categories:
        Server["Categories"].append({
            "Name" : Category.name,
            "ID" : Category.id,
            "Position" : Category.position
        })

    JSON.dump(Server, open(f"./Servers/{Guild.id}.json", "w"), indent = 4)

    await Context.send(embed = Embed, file = Discord.File(f"./Servers/{Guild.id}.json"))

@Client.command()
async def restore(Context : Commands.Context):
    try:
        with open(f"./Servers/{Context.guild.id}.json", "r") as Storage:
                Server = JSON.load(Storage)

        Guild = Context.guild

        for Channel in Guild.channels:
            await Channel.delete()

        Bot = Guild.get_member(Client.user.id)
        for Role in Guild.roles:
            if Role.position < Bot.top_role.position:
                try:
                    await Role.delete()

                except:
                    if Role.name != "@everyone":
                        print(f"**{Role.name}** is managed by an integration.")

        for Category in Guild.categories:
            await Category.delete()

        for Channel in Server["Channels"]:
            await Guild.create_text_channel(name = Channel["Name"],
                                            position = Channel["Position"],
                                            category = Guild.get_channel(Channel["Category"]),
                                            nsfw = Channel["NSFW"],
                                            slowmode_delay = Channel["Slowmode"],
                                            topic = Channel["Topic"])

        for Channel in Server["Voice-Channels"]:
            await Guild.create_voice_channel(name = Channel["Name"],
                                                position = Channel["Position"],
                                                category = Guild.get_channel(Channel["Category"]),
                                                bitrate = Channel["Bitrate"],
                                                user_limit = Channel["User-Limit"])

        for Role in Server["Roles"]:
            await Guild.create_role(name = Role["Name"],
                                    hoist = Role["Hoisted"],
                                    mentionable = Role["Mentionable"])

        for Category in Server["Categories"]:
            await Guild.create_category(name = Category["Name"],
                                            position = Category["Position"])

        await Guild.edit(afk_channel = Guild.get_channel(Server["Inactive-Channel"]),
                            afk_timeout = Server["Inactive-Timeout"],
                            system_channel = Guild.get_channel(Server["System-Messages"]),
                            description = Server["Template-Description"],
                            name = Server["Template-Title"],
                            system_channel_flags = Discord.SystemChannelFlags(join_notifications = Server["Send-Welcome-Messages"],
                                                                                premium_subscriptions = Server["Send-Boost-Messages"]))

        Embed = Discord.Embed(title = "JSON Recovery",
                                description = "Your server has been restored using JSON from our database.",
                                color = Discord.Color.random())

        await Context.author.send(embed = Embed)

    except FileNotFoundError:
        Embed = Discord.Embed(title = "JSON Recovery",
                              description = "There is no backup for this server.",
                              color = Discord.Color.random())

        await Context.send(embed = Embed)

@Client.command()   
async def delete(Context : Commands.Context):
    try:
        Embed = Discord.Embed(title = "JSON Recovery",
                              description = "Your server's JSON has been deleted from our database.",
                              color = Discord.Color.random())

        OS.remove(f"./Servers/{Context.guild.id}.json")

        await Context.send(embed = Embed)

    except FileNotFoundError:
        Embed = Discord.Embed(title = "JSON Recovery",
                              description = "There is no backup for this server.",
                              color = Discord.Color.random())

        await Context.send(embed = Embed)

if Debug == True:
    @Client.command()
    async def clear(Context : Commands.Context):
        Guild = Context.guild

        for Channel in Guild.channels:
            await Channel.delete()

    @Client.command()
    async def purge(Context : Commands.Context):
        Channel = Context.channel

        await Channel.purge(limit = 1000)


# Load our instance depending on what we chose:
Client.run(Data["Token"])
