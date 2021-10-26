import discord
from discord.ext import commands
from replit import db
import random

if "Currency" not in db:
    db["Currency"] = {}
if "Shop" not in db:
    db["Shop"] = {}

class Currency(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(
        description = "member must not be a bot.",
        aliases = ["bal"]
    )
    async def balance(self, ctx, *, member: discord.Member = None):
        if member == None:
            member = ctx.author
        if member.bot:
            return await ctx.reply("member must not be a bot.")
        if str(member.id) not in db["Currency"]:
            db["Currency"][str(member.id)] = 0
        await ctx.reply(f"{member.display_name} have ${db['Currency'][str(member.id)]}.")
    
    @commands.command(
        aliases = ["lb"]
    )
    async def leaderboard(self, ctx):
        if str(ctx.author.id) not in db["Currency"]:
            db["Currency"][str(ctx.author.id)] = 0
        await ctx.reply(embed = discord.Embed(
            title = "Leaderboard",
            description = "\n".join(f"{index + 1}. `{self.client.get_user(int(item[0])) or 'invalid-user#0000'}`: ${item[1]}" for index, item in enumerate(sorted(filter(lambda i: i[1] > 0, db["Currency"].items()), key = lambda i: i[1], reverse = True))),
            color = 0xffe5ce
        ).set_footer(
            text = ctx.author.display_name,
            icon_url = ctx.author.avatar_url
        ))
    
    @commands.command(
        description = "cooldown is 1 hour."
    )
    @commands.cooldown(rate = 1, per = 1 * 60 * 60, type = commands.BucketType.user)
    async def work(self, ctx):
        if str(ctx.author.id) not in db["Currency"]:
            db["Currency"][str(ctx.author.id)] = 0
        gain = random.randint(100, 250)
        db["Currency"][str(ctx.author.id)] += gain
        await ctx.reply(f"You worked and gained ${gain}.")
    
    @commands.command(
        description = "cooldown is 1 day."
    )
    @commands.cooldown(rate = 1, per = 24 * 60 * 60, type = commands.BucketType.user)
    async def daily(self, ctx):
        if str(ctx.author.id) not in db["Currency"]:
            db["Currency"][str(ctx.author.id)] = 0
        db["Currency"][str(ctx.author.id)] += 1000
        await ctx.reply("$1000 for your daily reward!")
    
    @commands.command(hidden = True)
    @commands.is_owner()
    async def set(self, ctx, member: discord.Member, amount: int):
        db["Currency"][str(member.id)] = amount
        await ctx.reply(f"{member.display_name}'s balance has been set to ${amount}.")
    
    @commands.group()
    @commands.guild_only()
    async def shop(self, ctx):
        if ctx.invoked_subcommand == None:
            if str(ctx.guild.id) not in db["Shop"]:
                db["Shop"][str(ctx.guild.id)] = {"nothing": 0}
            await ctx.reply(embed = discord.Embed(
                title = f"{ctx.guild.name}'s Shop",
                description = "\n".join(f"{num + 1}. `{i[0]}`: ${i[1]}" for num, i in enumerate(sorted(db["Shop"][str(ctx.guild.id)].items(), key = lambda i: i[1]))),
                color = 0xffe5ce
            ).set_footer(
                text = ctx.author.name,
                icon_url = ctx.author.avatar_url
            ))
    
    @shop.command(
        description = """
You need the Manage Guild permission to use this command.
amount cannot be lower than 0.
        """
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild = True)
    async def add(self, ctx, name: str, price: int):
        if str(ctx.guild.id) not in db["Shop"]:
            db["Shop"][str(ctx.guild.id)] = {"nothing": 0}
        if price >= 0:
            if name not in db["Shop"][str(ctx.guild.id)]:
                db["Shop"][str(ctx.guild.id)][name] = price
                await ctx.reply(f'Item "{name}" added.')
            else:
                await ctx.reply(f'Item named "{name}" is already added.')
        else:
            await ctx.reply("price must be greater or equal to 0.")
    
    @shop.command(
        description = """
You need the Manage Guild permission to use this command.
amount cannot be lower than 0.
        """
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild = True)
    async def edit(self, ctx, item: str, price: int):
        if str(ctx.guild.id) not in db["Shop"]:
            db["Shop"][str(ctx.guild.id)] = {"nothing": 0}
        try:
            if price >= 0:
                db["Shop"][str(ctx.guild.id)][item] = price
                await ctx.reply(f'Item "{item}" edited.')
            else:
                await ctx.reply("price must be greater or equal to 0.")
        except KeyError:
            await ctx.reply(f'No item named "{item}" found.')
    
    @shop.command(
        description = "You need the Manage Guild permission to use this command."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild = True)
    async def remove(self, ctx, *, item: str):
        if str(ctx.guild.id) not in db["Shop"]:
            db["Shop"][str(ctx.guild.id)] = {"nothing": 0}
        try:
            del db["Shop"][str(ctx.guild.id)][item]
            await ctx.reply(f'Item "{item}" removed.')
        except KeyError:
            await ctx.reply(f'No item named "{item}" found.')
    
    @commands.command()
    @commands.guild_only()
    async def buy(self, ctx, *, item: str):
        if str(ctx.author.id) not in db["Currency"]:
            db["Currency"][str(ctx.author.id)] = 0
        if str(ctx.guild.id) not in db["Shop"]:
            db["Shop"][str(ctx.guild.id)] = {"nothing": 0}
        try:
            if db["Currency"][str(ctx.author.id)] >= db["Shop"][str(ctx.guild.id)][item]:
                db["Currency"][str(ctx.author.id)] -= db["Shop"][str(ctx.guild.id)][item]
                await ctx.reply(f"Item has been purchased.")
            else:
                await ctx.reply(f"You're ${db['Shop'][str(ctx.guild.id)][item] - db['Currency'][str(ctx.author.id)]} short.")
        except KeyError:
            await ctx.reply(f'No item named "{item}" found.')

def setup(client):
    client.add_cog(Currency(client))