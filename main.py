import discord
from discord.ext import commands, tasks
from webserver import keep_alive
import os
import datetime
import json
import asyncio
import random

class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
    async def send_bot_help(self, mapping):
        await self.get_destination().send(embed = discord.Embed(
            description = "**Cogs**\n" + "\n".join(f"{num + 1}. `{cog.qualified_name}`" for num, cog in enumerate(filter(lambda i: i != None, mapping))) + "\n\n**Commands**\n" + "\n".join(f"{num + 1}. {f'`{command.name}`' if command.enabled else f'~~`{command.name}`~~'} {str() if command.brief == None else command.brief}" for num, command in enumerate(filter(lambda command: command.hidden == False, mapping[None]))),
            color = 0xffe5ce
        ))
    async def send_cog_help(self, cog):
        await self.get_destination().send(embed = discord.Embed(
            title = cog.qualified_name,
            description = "\n".join(f"{num + 1}. {f'`{command.name}`' if command.enabled else f'~~`{command.name}`~~'} {str() if command.brief == None else command.brief}" for num, command in enumerate(filter(lambda command: command.hidden == False, cog.get_commands()))),
            color = 0xffe5ce
        ))
    async def send_command_help(self, command):
        await self.get_destination().send(embed = discord.Embed(
            title = command.name + (str() if command.aliases == [] else f"/{'/'.join(command.aliases)}") + " " + command.signature,
            description = (str() if command.help == None else command.help),
            color = 0xffe5ce
        ).set_footer(
            text = "<> is required, [] is optional."
        ))

client = commands.Bot(
    command_prefix = "s!",
    help_command = HelpCommand(),
    owner_id = 738038222797406308,
    activity = discord.Game("Python"),
    intents = discord.Intents.all()
)
client.help_command.help = "Shows this message"
client.load_extension("cogs.currency")

#Events
@client.event
async def on_ready():
    print(f"Online since {datetime.date.today()}")
    global ready
    ready = datetime.datetime.today()

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        try:
            await ctx.reply(f"You are on cooldown. Try again in <t:{int((datetime.datetime.today().timestamp() + error.retry_after) - (datetime.datetime.today().timestamp() + error.retry_after) % 1)}:R>", mention_author = False)
        except discord.Forbidden:
            if ctx.author.dm_channel == None:
                await ctx.author.create_dm()
            await ctx.author.dm_channel.send(f"> {ctx.channel.mention}: {ctx.message.content}\nYou are on cooldown. Try again in <t:{int((datetime.datetime.today().timestamp() + error.retry_after) - (datetime.datetime.today().timestamp() + error.retry_after) % 1)}:R>")
    else:
        try:
            await ctx.reply(error, mention_author = False)
        except discord.Forbidden:
            if ctx.author.dm_channel == None:
                await ctx.author.create_dm()
            await ctx.author.dm_channel.send(f"> {ctx.channel.mention}: {ctx.message.content}\n{error}")

@client.event
async def on_guild_join(guild):
    user = client.get_user(client.owner_id)
    if user.dm_channel == None:
        await user.create_dm()
    await user.dm_channel.send(f"Added to {guild.name}.")

@client.event
async def on_guild_remove(guild):
    user = client.get_user(client.owner_id)
    if user.dm_channel == None:
        await user.create_dm()
    await user.dm_channel.send(f"Removed from {guild.name}.")

@client.event
async def on_member_join(member):
    user = client.get_user(client.owner_id)
    if user.dm_channel == None:
        await user.create_dm()
    await user.dm_channel.send(f"{member.name} added to {member.guild.name}.")

@client.event
async def on_member_remove(member):
    user = client.get_user(client.owner_id)
    if user.dm_channel == None:
        await user.create_dm()
    await user.dm_channel.send(f"{member.name} removed from {member.guild.name}.")

#Miscellaneous Commands
@client.command(aliases = ["eval"])
async def evaluate(ctx, *, content: str):
    await ctx.reply(eval(content), mention_author = False)

@client.command()
async def say(ctx, *, content: str):
    if ctx.message.reference == None:
        await ctx.send(
            content.format(author = ctx.author, channel = ctx.channel, guild = ctx.guild),
            allowed_mentions = discord.AllowedMentions(everyone = False)
        )
    else:
        await ctx.message.reference.resolved.reply(
            content.format(author = ctx.author, channel = ctx.channel, guild = ctx.guild),
            allowed_mentions = discord.AllowedMentions(everyone = False),
            mention_author = False
        )

@client.command()
@commands.bot_has_permissions(manage_webhooks = True)
async def echo(ctx, *, message: str):
    webhook = None
    for temp in await ctx.channel.webhooks():
        if temp.token != None:
            webhook = temp
    if webhook == None:
        webhook = await ctx.channel.create_webhook(name = "Echo")
    if ctx.message.reference == None or ctx.message.reference.resolved == None:
        await webhook.send(message, username = ctx.author.display_name, avatar_url = ctx.author.avatar_url)
    else:
        if ctx.message.reference.resolved.author.id == webhook.id:
            await webhook.edit_message(ctx.message.reference.resolved.id, content = message)
        else:
            await webhook.send(message, username = ctx.author.display_name, avatar_url = ctx.author.avatar_url)
    await ctx.message.delete()

@client.command()
async def embed(ctx, title: str, description: str, url: str = ""):
    embed = discord.Embed(
        title = title,
        description = description,
        color = 0xffe5ce
    )
    if url != "":
        embed.set_image(
            url = url
        )
    elif ctx.message.attachments != []:
        embed.set_image(
            url = ctx.message.attachments[0].url
        )
    await ctx.send(embed = embed)

@client.command()
async def invite(ctx):
    await ctx.reply(embed = discord.Embed(
        title = "Invite",
        description = f"[Invite {client.user.name} to your server]({discord.utils.oauth_url(client.user.id, permissions = discord.Permissions(permissions = 805432326))})",
        color = 0xffe5ce
    ).set_footer(
        text = ctx.author.name,
        icon_url = ctx.author.avatar_url
    ), mention_author = False)

#Information Commands
@client.command(aliases = ["member"])
@commands.bot_has_permissions(attach_files = True)
async def user(ctx, *, user: discord.User = None):
    if user == None:
        user = ctx.author
    try:
        member = await ctx.guild.fetch_member(user.id)
        await ctx.reply(embed = discord.Embed(
            title = "Member Info",
            url = f"https://discord.com/users/{member.id}",
            description = f"""
Nick: {member.nick}
Name: {member.name}
Tag: #{member.discriminator}
ID: {member.id}
Bot? {"Yes" if member.bot else 'No'}
Roles: {len(member.roles) - 1}
Created at: <t:{int(member.created_at.timestamp() - member.created_at.timestamp() % 1)}:F>
Joined at: <t:{int(member.joined_at.timestamp() - member.joined_at.timestamp() % 1)}:F>
Avatar URL: [Link]({member.avatar_url})
""",
            color = 0xffe5ce
        ).set_image(
            url = member.avatar_url
        ).set_footer(
            text = ctx.author.name,
            icon_url = ctx.author.avatar_url
        ), mention_author = False)
    except discord.NotFound:
        await ctx.reply(embed = discord.Embed(
            title = "User Info",
            description = f"""
Name: {user.name}
Tag: #{user.discriminator}
ID: {user.id}
Bot? {"Yes" if user.bot else 'No'}
Created at: <t:{int(user.created_at.timestamp() - user.created_at.timestamp() % 1)}:F>
Avatar URL: [Link]({user.avatar_url})
""",
            color = 0xffe5ce
        ).set_image(
            url = user.avatar_url
        ).set_footer(
            text = ctx.author.name,
            icon_url = ctx.author.avatar_url
        ), mention_author = False)

@client.command(aliases = ["server"])
@commands.bot_has_permissions(attach_files = True)
async def guild(ctx, *, guild: discord.Guild = None):
    if guild == None:
        guild = ctx.guild
    await ctx.reply(embed = discord.Embed(
        title = "Server Info",
        description = f"""
Name: {guild.name}
ID: {guild.id}
Members: {len(list(filter(lambda member: member.bot == False, guild.members)))} humans, {len(list(filter(lambda member: member.bot, guild.members)))} bots, {guild.member_count} total
Channels: {len(guild.text_channels)} text, {len(guild.voice_channels)} voice
Roles: {len(guild.roles) - 1}
Owner: {guild.owner.mention} ({guild.owner})
Created at: <t:{int(guild.created_at.timestamp() - guild.created_at.timestamp() % 1)}:F>
Icon URL: [Link]({guild.icon_url})
""",
        color = 0xffe5ce
    ).set_image(
        url = guild.icon_url
    ).set_footer(
        text = ctx.author.name,
        icon_url = ctx.author.avatar_url
    ), mention_author = False)

@client.command(aliases = ["emote"])
@commands.bot_has_permissions(attach_files = True)
async def emoji(ctx, *, emoji: discord.Emoji):
    await ctx.reply(embed = discord.Embed(
        title = "Emoji Info",
        description = f"""
Name: {emoji.name}
ID: {emoji.id}
Animated? {"Yes" if emoji.animated else 'No'}
Created at: <t:{int(emoji.created_at.timestamp() - emoji.created_at.timestamp() % 1)}:F>
URL: [Link]({emoji.url})
""",
        color = 0xffe5ce
    ).set_image(
        url = emoji.url
    ).set_footer(
        text = ctx.author.name,
        icon_url = ctx.author.avatar_url
    ), mention_author = False)

#Moderation Commands
@client.command()
@commands.guild_only()
@commands.has_guild_permissions(kick_members = True)
@commands.bot_has_guild_permissions(kick_members = True)
async def kick(ctx, user: discord.User, *, reason: str = "no reason"):
    await ctx.guild.kick(user = user, reason = f"By {ctx.author.name} for {reason}.")
    await ctx.reply(f"{user.name} has been kicked for {reason}.", mention_author = False)

@client.command()
@commands.guild_only()
@commands.has_guild_permissions(ban_members = True)
@commands.bot_has_guild_permissions(ban_members = True)
async def ban(ctx, user: discord.User, *, reason: str = "no reason"):
    await ctx.guild.ban(user = user, reason = f"By {ctx.author.name} for {reason}.", delete_message_days = 0)
    await ctx.reply(f"{user.name} has been banned for {reason}.", mention_author = False)

@client.command()
@commands.guild_only()
@commands.has_guild_permissions(ban_members = True)
@commands.bot_has_guild_permissions(ban_members = True)
async def unban(ctx, user: discord.User, *, reason: str = "no reason"):
    await ctx.guild.unban(user = user, reason = f"By {ctx.author.name} for {reason}.")
    await ctx.reply(f"{user.name} has been unbanned for {reason}.", mention_author = False)

@client.command()
@commands.guild_only()
@commands.has_guild_permissions(manage_roles = True)
@commands.bot_has_guild_permissions(manage_roles = True)
async def role(ctx, role: discord.Role, *, member: discord.Member = None):
    if member == None:
        member = ctx.author
    if ctx.author.top_role.position < role.position:
        if ctx.author != ctx.guild.owner:
            return await ctx.reply(f"Your highest role is not high enough.", mention_author = False)
    if role in member.roles:
        await member.remove_roles(role, reason = f"By {ctx.author.name}")
        await ctx.reply(f"Removed {role.mention} from {member.mention}.", allowed_mentions = discord.AllowedMentions(roles = False), mention_author = False)
    else:
        await member.add_roles(role, reason = f"By {ctx.author.name}")
        await ctx.reply(f"Added {role.mention} to {member.mention}.", allowed_mentions = discord.AllowedMentions(roles = False), mention_author = False)

@client.command()
@commands.guild_only()
@commands.has_permissions(manage_messages = True)
@commands.bot_has_permissions(manage_messages = True, read_message_history = True)
async def purge(ctx, limit: str):
    if limit.lower() == "all":
        limit = len(await ctx.channel.history(limit = None).flatten())
    else:
        limit = int(limit)
    purge = await ctx.channel.purge(limit = limit + 1)
    await ctx.send(f"Purged {len(purge) - 1} messages.", delete_after = 5)

#Private Commands
@client.command(hidden = True)
@commands.check(lambda ctx: ctx.author.id == client.owner_id)
async def doc(ctx, *, search: str = ""):
    if search == "":
        await ctx.reply("https://discordpy.readthedocs.io/en/stable/", mention_author = False)
    else:
        await ctx.reply(f"https://discordpy.readthedocs.io/en/stable/search.html?q={search.replace(' ', '+')}", mention_author = False)

@client.command(hidden = True)
@commands.check(lambda ctx: ctx.author.id == client.owner_id)
async def bot(ctx):
    await ctx.reply(embed = discord.Embed(
        title = "Bot Info",
        description = f"""
Serving: {len(client.guilds)} guilds, {len(list(filter(lambda user: user.bot == False, client.users)))} users
Latency: {int(client.latency * 1000 - client.latency * 1000 % 1)}ms
Uptime: <t:{int(ready.timestamp() - ready.timestamp() % 1)}:R>
Version: {discord.__version__}
""",
        color = 0xffe5ce
    ).set_footer(
        text = ctx.author.name,
        icon_url = ctx.author.avatar_url
    ), mention_author = False)

@client.command(hidden = True)
@commands.check(lambda ctx: ctx.author.id == client.owner_id)
async def leave(ctx, *, guild: discord.Guild = None):
    if guild == None:
        guild = ctx.guild
    await ctx.message.add_reaction("✅")
    await ctx.message.add_reaction("❎")
    try:
        reaction, user = await client.wait_for("reaction_add", check = lambda reaction, user: reaction.message == ctx.message and str(reaction.emoji) in ["✅", "❎"] and user == ctx.author, timeout = 10)
        if str(reaction.emoji) == "✅":
            await ctx.message.remove_reaction("✅", client.user)
            await ctx.message.remove_reaction("❎", client.user)
            await guild.leave()
        elif str(reaction.emoji) == "❎":
            await ctx.message.remove_reaction("✅", client.user)
            await ctx.message.remove_reaction("❎", client.user)
    except asyncio.TimeoutError:
        await ctx.message.remove_reaction("✅", client.user)
        await ctx.message.remove_reaction("❎", client.user)

keep_alive()
client.run(os.environ["token"])