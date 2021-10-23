import discord
from discord.ext import commands
from webserver import keep_alive
from replit import db
import datetime
import asyncio
import random
import os

if "Prefix" not in db:
    db["Prefix"] = {}

class MinimalHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        for page in self.paginator.pages:
            await self.get_destination().send(embed = discord.Embed(
                title = "Help!",
                description = page,
                color = 0xffe5ce
            ))

async def get_prefix(client, message):
    if message.guild == None:
        return "s!"
    elif str(message.guild.id) not in db["Prefix"]:
        db["Prefix"][str(message.guild.id)] = "s!"
    return db["Prefix"][str(message.guild.id)]

client = commands.Bot(
    command_prefix = get_prefix,
    activity = discord.Game("Python"),
    help_command = MinimalHelpCommand(),
    owner_id = 881772996614819941,
    allowed_mentions = discord.AllowedMentions(
        everyone = False,
        replied_user = False,
        roles = False
    ),
    intents = discord.Intents(
        emojis = True,
        guilds = True,
        members = True,
        messages = True,
        reactions = True
    )
)
client.load_extension("cogs.currency")

#Events
@client.event
async def on_connect():
    print("Connected")

@client.event
async def on_ready():
    print("Ready")
    client.launch_time = datetime.datetime.utcnow()
    await client.get_user(client.owner_id).send(f"Online since <t:{int(client.launch_time.timestamp())}:d> <t:{int(client.launch_time.timestamp())}:T>")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        try:
            try:
                await ctx.reply(f"You are on cooldown. Try again <t:{int(datetime.datetime.utcnow().timestamp() + error.retry_after)}:R>")
            except discord.HTTPException:
                await ctx.send(f"> {ctx.message}\nYou are on cooldown. Try again <t:{int(datetime.datetime.utcnow().timestamp() + error.retry_after)}:R>")
        except discord.Forbidden:
            await ctx.author.send(f"> {ctx.channel.mention}: {ctx.message.content}\nYou are on cooldown. Try again <t:{int(datetime.datetime.utcnow().timestamp() + error.retry_after)}:R>")
    elif isinstance(error, commands.NotOwner):
        try:
            try:
                await ctx.reply(f'Command "{ctx.command.name}" is not found')
            except discord.HTTPException:
                await ctx.send(f'> {ctx.message.content}\nCommand "{ctx.command.name}" is not found')
        except discord.Forbidden:
            await ctx.author.send(f'> {ctx.channel.mention}: {ctx.message.content}\nCommand "{ctx.command.name}" is not found')
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.CommandNotFound):
        try:
            try:
                await ctx.reply(error)
            except discord.HTTPException:
                await ctx.send(f"> {ctx.message}\n{error}")
        except discord.Forbidden:
            await ctx.author.send(f"> {ctx.channel.mention}: {ctx.message.content}\n{error}")
    else:
        try:
            try:
                await ctx.reply(error)
            except discord.HTTPException:
                await ctx.send(f"> {ctx.message}\n{error}")
        except discord.Forbidden:
            await ctx.author.send(f"> {ctx.channel.mention}: {ctx.message.content}\n{error}")
        ctx.command.reset_cooldown(ctx)

@client.event
async def on_guild_join(guild):
    await client.get_user(client.owner_id).send(f"Added to {guild.name}.")

@client.event
async def on_guild_remove(guild):
    await client.get_user(client.owner_id).send(f"Removed from {guild.name}.")

#Miscellaneous Commands
@client.command(
    brief = "Solves an equation",
    help = "Math Operators: +, -, ×, ÷, ^, %"
)
async def math(ctx, *, content: str):
    if commands.is_owner():
        await ctx.reply(embed = discord.Embed(
            title = "Evaluation Result",
            description = eval(content),
            color = 0xffe5ce
        ).set_footer(
            text = ctx.author.display_name,
            icon_url = ctx.author.avatar_url
        ))
    else:
        content = "".join(filter(lambda i: i in "9876543210+-×÷^%", content))
        content = content.replace("^", "**").replace("÷", "/").replace("×", "*")
        await ctx.reply(f"`{float(eval(content))}`")

@client.command()
async def reverse(ctx, *, content):
    await ctx.reply(content[::-1])

@client.command()
async def poll(ctx, title, *options):
    var = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟")
    message = await ctx.send(embed = discord.Embed(
        title = f"Poll: {title}",
        description = "\n".join(f"{i + 1}. `{name}`" for i, name in filter(lambda i: i[0] < 10, enumerate(options))),
        color = 0xffe5ce
    ).set_footer(
        text = ctx.author.display_name,
        icon_url = ctx.author.avatar_url
    ))
    for i in range(len(options)):
        if i > 9:
            break
        await message.add_reaction(var[i])

@client.command(
    brief = "Converts into binary"
)
async def binary(ctx, *, content):
    await ctx.reply(" ".join(format(ord(i), '08b') for i in content))
                                    
@client.command()
async def say(ctx, *, content: str):
    if ctx.message.reference == None:
        await ctx.send(content.format(author = ctx.author, channel = ctx.channel, guild = ctx.guild))
    else:
        await ctx.message.reference.resolved.reply(content.format(author = ctx.author, channel = ctx.channel, guild = ctx.guild))

@client.command(
    brief = "Creates an equation"
)
async def equation(ctx):
    num1 = random.randint(-9, 9)
    opt = random.choice(("+", "-", "*"))
    num2 = random.randint(-9, 9)
    reply = await ctx.reply(f"{num1} {opt.replace('*', '×')} {num2} = ?")
    def check(message):
        try:
            int(message.content)
        except ValueError:
            return False
        else:
            return message.author == ctx.author and message.channel == ctx.channel
    try:
        message = await client.wait_for("message", check = check, timeout = 10)
        if int(message.content) == eval(f"{num1} {opt} {num2}"):
            await message.reply("Correct!")
        else:
            await message.reply(f"Wrong! It was {eval(f'{num1} {opt} {num2}')}")
    except asyncio.TimeoutError:
        await reply.edit(content = f"You didn't reply in time. It was {eval(f'{num1} {opt} {num2}')}")

@client.command(
    description = """
Type Fizzbuzz if the number shown is divisable by 3 and 5
else type Fizz if it's divisable by 3
else type Buzz if it's divisable by 5
else type the number shown
    """
)
async def fizzbuzz(ctx):
    reply = await ctx.reply("Starting...", mention_author = True)
    await asyncio.sleep(3)
    attempt = 1
    while True:
        number = random.randint(1, attempt * 5)
        await reply.edit(content = f"{number} = Fizzbuzz/Fizz/Buzz/{number}?")
        try:
            message = await client.wait_for("message", check = lambda message: message.author == ctx.author and message.channel == ctx.channel and not message.content.startswith("s!"), timeout = 10)
            if message.content.lower() == ("fizzbuzz" if number % 3 == 0 and number % 5 == 0 else "fizz" if number % 3 == 0 else "buzz" if number % 5 == 0 else str(number)):
                await reply.edit(content = "Correct!")
                await asyncio.sleep(3)
                attempt += 1
            else:
                await reply.edit(content = "Wrong!")
                break
            await message.delete()
        except asyncio.TimeoutError:
            await reply.edit(content = "You didn't reply in time.")
            break
    await asyncio.sleep(3)
    await reply.edit(content = f"Congrats! you managed to reach up to {attempt} attempts!")

@client.command(
    brief = "Rock Paper Scissors!",
    description = "Bot requires Add Reactions permission(s) to run this command.",
    help = """
 - Rock & Rock: Tie
 - Rock & Paper: Lose
 - Rock & Scissors: Win
 - Paper & Rock: Win
 - Paper & Paper: Tie
 - Paper & Scissors: Lose
 - Scissors & Rock: Lose
 - Scissors & Paper: Win
 - Scissors & Scissors: Tie
    """
)
@commands.bot_has_permissions(add_reactions = True)
async def rps(ctx, member: discord.Member = None):
    if member == None:
        member = client.user
    if member == ctx.author:
        return await ctx.reply("You can't play against yourself.")
    moves = ("🪨", "📄", "✂️")
    try:
        message = await ctx.reply("Choose a move by reacting to one of the reactions down below:")
        for emoji in moves:
            await message.add_reaction(emoji)
        reaction, user = await client.wait_for("reaction_add", check = lambda reaction, user: str(reaction.emoji) in moves and reaction.message == message and user == ctx.author, timeout = 30)
        await message.delete()
        p1 = moves.index(str(reaction.emoji))
        if member.bot:
            p2 = random.randint(0, 2)
        else:
            message = await ctx.send(f"{member.mention} Choose a move by reacting to one of the reactions down below:")
            for emoji in moves:
                await message.add_reaction(emoji)
            reaction, user = await client.wait_for("reaction_add", check = lambda reaction, user: str(reaction.emoji) in moves and reaction.message == message and user == member, timeout = 30)
            await message.delete()
            p2 = moves.index(str(reaction.emoji))
        if p1 - p2 in (-2, 1):
            await ctx.reply(f"{ctx.author.display_name} wins!\n\n{ctx.author.display_name}: {moves[p1]} | {member.display_name}: {moves[p2]}")
        elif p1 - p2 in (-1, 2):
            await ctx.reply(f"{member.display_name} wins!\n\n{ctx.author.display_name}: {moves[p1]} | {member.display_name}: {moves[p2]}")
        else:
            await ctx.reply(f"It's a tie!\n\n{ctx.author.display_name}: {moves[p1]} | {member.display_name}: {moves[p2]}")
    except asyncio.TimeoutError:
        await message.edit(content = "You didn't reply in time.")

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
    await ctx.reply("<https://Senjibot.senjienji.repl.co/invite>")

#Informational Commands
@client.command(
    aliases = ["member"]
)
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
Bot? {'Yes' if member.bot else 'No'}
Roles: {len(member.roles) - 1}
Created at: <t:{int(member.created_at.timestamp())}:F>
Joined at: <t:{int(member.joined_at.timestamp())}:F>
Avatar URL: [Link]({member.avatar_url})
            """,
            color = 0xffe5ce
        ).set_image(
            url = member.avatar_url
        ).set_footer(
            text = ctx.author.name,
            icon_url = ctx.author.avatar_url
        ))
    except discord.NotFound:
        await ctx.reply(embed = discord.Embed(
            title = "User Info",
            description = f"""
Name: {user.name}
Tag: #{user.discriminator}
ID: {user.id}
Bot? {'Yes' if user.bot else 'No'}
Created at: <t:{int(user.created_at.timestamp())}:F>
Avatar URL: [Link]({user.avatar_url})
            """,
            color = 0xffe5ce
        ).set_image(
            url = user.avatar_url
        ).set_footer(
            text = ctx.author.name,
            icon_url = ctx.author.avatar_url
        ))

@client.command(
    aliases = ["server"]
)
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
Created at: <t:{int(guild.created_at.timestamp())}:F>
Icon URL: [Link]({guild.icon_url})
        """,
        color = 0xffe5ce
    ).set_image(
        url = guild.icon_url
    ).set_footer(
        text = ctx.author.name,
        icon_url = ctx.author.avatar_url
    ))

@client.command(
    aliases = ["emote"]
)
@commands.bot_has_permissions(attach_files = True)
async def emoji(ctx, *, emoji: discord.Emoji):
    await ctx.reply(embed = discord.Embed(
        title = "Emoji Info",
        description = f"""
Name: {emoji.name}
ID: {emoji.id}
Animated? {'Yes' if emoji.animated else 'No'}
Created at: <t:{int(emoji.created_at.timestamp())}:F>
URL: [Link]({emoji.url})
        """,
        color = 0xffe5ce
    ).set_image(
        url = emoji.url
    ).set_footer(
        text = ctx.author.name,
        icon_url = ctx.author.avatar_url
    ))

@client.command()
async def bot(ctx):
    await ctx.reply(embed = discord.Embed(
        title = "Bot Info",
        description = f"""
In: {len(client.guilds)} guilds
Latency:
 - Client: {int(client.latency * 1000)}ms
 - API: {int((datetime.datetime.utcnow() - ctx.message.created_at).total_seconds() * 1000)}ms
Uptime: <t:{int(client.launch_time.timestamp())}:R>
Version: {discord.__version__}
        """,
        color = 0xffe5ce
    ).set_footer(
        text = ctx.author.name,
        icon_url = ctx.author.avatar_url
    ))

#Moderation Commands
@client.command(
    description = "You need the Kick Members permissions to use this command."
)
@commands.guild_only()
@commands.has_guild_permissions(kick_members = True)
@commands.bot_has_guild_permissions(kick_members = True)
async def kick(ctx, user: discord.User, *, reason: str = "no reason"):
    await ctx.guild.kick(user = user, reason = f"By {ctx.author.name} for {reason}.")
    await ctx.reply(f"{user.name} has been kicked for {reason}.")

@client.command(
    description = "You need the Ban Members permission to use this command."
)
@commands.guild_only()
@commands.has_guild_permissions(ban_members = True)
@commands.bot_has_guild_permissions(ban_members = True)
async def ban(ctx, user: discord.User, *, reason: str = "no reason"):
    await ctx.guild.ban(user = user, reason = f"By {ctx.author.name} for {reason}.", delete_message_days = 0)
    await ctx.reply(f"{user.name} has been banned for {reason}.")

@client.command(
    description = "You need the Ban Members permission to use this command."
)
@commands.guild_only()
@commands.has_guild_permissions(ban_members = True)
@commands.bot_has_guild_permissions(ban_members = True)
async def unban(ctx, user: discord.User, *, reason: str = "no reason"):
    await ctx.guild.unban(user = user, reason = f"By {ctx.author.name} for {reason}.")
    await ctx.reply(f"{user.name} has been unbanned for {reason}.")

@client.command()
@commands.guild_only()
async def prefix(ctx, prefix = None):
    if prefix == None:
        await ctx.reply(f"My current prefix is `{db['Prefix'][str(ctx.guild.id)]}`.")
    elif commands.has_guild_permissions(manage_guild = True):
        db["Prefix"][str(ctx.guild.id)] = prefix
        await ctx.reply(f"Prefix has been set to `{db['Prefix'][str(ctx.guild.id)]}`.")

@client.command(
    description = "You need the Manage Roles permission to use this command."
)
@commands.guild_only()
@commands.has_guild_permissions(manage_roles = True)
@commands.bot_has_guild_permissions(manage_roles = True)
async def role(ctx, role: discord.Role, *, member: discord.Member = None):
    if member == None:
        member = ctx.author
    if ctx.author.top_role.position < role.position and ctx.author != ctx.guild.owner:
        return await ctx.reply(f"Your highest role is not high enough.")
    if role in member.roles:
        await member.remove_roles(role, reason = f"By {ctx.author.name}")
        await ctx.reply(f"Removed {role.mention} from {member.mention}.")
    else:
        await member.add_roles(role, reason = f"By {ctx.author.name}")
        await ctx.reply(f"Added {role.mention} to {member.mention}.")

@client.command(
    description = "You need the Manage Messages permission to use this command."
)
@commands.guild_only()
@commands.has_permissions(manage_messages = True)
@commands.bot_has_permissions(manage_messages = True, read_message_history = True)
async def purge(ctx, limit: str):
    if limit.lower() in ("all", "max", "maximum"):
        limit = len(await ctx.channel.history(limit = None).flatten())
    else:
        limit = int(limit)
    purge = await ctx.channel.purge(limit = limit + 1)
    await ctx.send(f"Purged {len(purge) - 1} messages.", delete_after = 5)

#Private Commands
@client.command(hidden = True)
@commands.is_owner()
async def doc(ctx, *, search: str = ""):
    if search == "":
        await ctx.reply("https://discordpy.readthedocs.io/en/stable/")
    else:
        await ctx.reply(f"https://discordpy.readthedocs.io/en/stable/search.html?q={search.replace(' ', '+')}")

@client.command(hidden = True)
@commands.is_owner()
async def invites(ctx, *, guild: discord.Guild):
    try:
        invites = await guild.invites()
    except discord.Forbidden:
        await ctx.reply(f"Not enough permission.")
    else:
        await ctx.author.send("\n".join(invite.url for invite in invites) or "No invites.")

@client.command(hidden = True)
@commands.is_owner()
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