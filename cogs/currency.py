import discord
from discord.ext import commands
import json
import random

class Currency(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(aliases = ["bal"])
    async def balance(self, ctx, *, member: discord.Member = None):
        if member == None:
            member = ctx.author
        with open("balance.json") as file:
            balance = json.load(file)
        if str(member.id) not in balance:
            balance[str(member.id)] = {"wallet": 0, "bank": 0}
        await ctx.reply(embed = discord.Embed(
            title = f"{member.name}'s Balance",
            description = f"""
Wallet: ${balance[str(member.id)]['wallet']}
Bank: ${balance[str(member.id)]['bank']}
""",
            color = 0xffe5ce
        ), mention_author = False)
        with open("balance.json", "w") as file:
            json.dump(balance, file, indent = 4)
    
    @commands.command(aliases = ["dep"])
    async def deposit(self, ctx, amount: str):
        with open("balance.json") as file:
            balance = json.load(file)
        if str(ctx.author.id) not in balance:
            balance[str(ctx.author.id)] = {"wallet": 0, "bank": 0}
        if amount.lower() == "all":
            amount = balance[str(ctx.author.id)]["wallet"]
        else:
            amount = int(amount)
        if amount > 0:
            if balance[str(ctx.author.id)]["wallet"] >= amount:
                balance[str(ctx.author.id)]["wallet"] -= amount
                balance[str(ctx.author.id)]["bank"] += amount
                await ctx.reply(f"${amount} has been deposited.", mention_author = False)
            else:
                await ctx.reply(f"You are ${balance[str(ctx.author.id)]['wallet'] - amount} short.", mention_author = False)
        else:
            await ctx.reply("Provide a valid amount greater than 0.")
        with open("balance.json", "w") as file:
            json.dump(balance, file, indent = 4)
    
    @commands.command(aliases = ["with"])
    async def withdraw(self, ctx, amount: str):
        with open("balance.json") as file:
            balance = json.load(file)
        if str(ctx.author.id) not in balance:
            balance[str(ctx.author.id)] = {"wallet": 0, "bank": 0}
        if amount.lower() == "all":
            amount = balance[str(ctx.author.id)]["bank"]
        else:
            amount = int(amount)
        if amount > 0:
            if balance[str(ctx.author.id)]["bank"] >= amount:
                balance[str(ctx.author.id)]["bank"] -= amount
                balance[str(ctx.author.id)]["wallet"] += amount
                await ctx.reply(f"${amount} has been withdrawn.", mention_author = False)
            else:
                await ctx.reply(f"You are ${balance[str(ctx.author.id)]['bank'] - amount} short.", mention_author = False)
        else:
            await ctx.reply("Provide a valid amount greater than 0.", mention_author = False)
        with open("balance.json", "w") as file:
            json.dump(balance, file, indent = 4)
    
    @commands.command()
    @commands.cooldown(rate = 1, per = 30 * 60, type = commands.BucketType.user)
    async def give(self, ctx, member: discord.Member, amount: str):
        with open("balance.json") as file:
            balance = json.load(file)
        if str(ctx.author.id) not in balance:
            balance[str(ctx.author.id)] = {"wallet": 0, "bank": 0}
        if amount.lower() == "all":
            amount = balance[str(ctx.author.id)]["wallet"]
        else:
            amount = int(amount)
        if str(member.id) not in balance:
            balance[str(member.id)] = {"wallet": 0, "bank": 0}
        if amount > 0:
            if balance[str(ctx.author.id)]["wallet"] >= amount:
                if amount == balance[str(ctx.author.id)]["wallet"]:
                    message = await ctx.reply(f"Are you sure you want to give all of your money to **{member.name}**?", mention_author = False)
                    await message.add_reaction("✅")
                    await message.add_reaction("❎")
                    try:
                        reaction, user = await self.client.wait_for("reaction_add", check = lambda reaction, user: str(reaction.emoji) in ("✅", "❎") and reaction.message == message and user == ctx.author, timeout = 20)
                        if str(reaction.emoji) == "✅":
                            await message.delete()
                        elif str(reaction.emoji) == "❎":
                            return await message.delete()
                    except asyncio.TimeoutError:
                        return await message.delete()
                balance[str(ctx.author.id)]["wallet"] -= amount
                balance[str(member.id)]["wallet"] += amount
                await ctx.reply(f"You gave **{member.name}** ${amount}.", mention_author = False)
            else:
                await ctx.reply(f"You are ${balance[str(ctx.author.id)]['wallet'] - amount} short.", mention_author = False)
        else:
            await ctx.reply("Provide a valid amount greater than 0.", mention_author = False)
        with open("balance.json", "w") as file:
            json.dump(balance, file, indent = 4)
    
    @commands.command()
    @commands.cooldown(rate = 1, per = 2 * 60 * 60, type = commands.BucketType.user)
    async def work(self, ctx):
        with open("balance.json") as file:
            balance = json.load(file)
        if str(ctx.author.id) not in balance:
            balance[str(ctx.author.id)] = {"wallet": 0, "bank": 0}
        gain = random.randint(100, 500)
        balance[str(ctx.author.id)]["wallet"] += gain
        await ctx.reply(f"You worked and gained ${gain}.", mention_author = False)
        with open("balance.json", "w") as file:
            json.dump(balance, file, indent = 4)
    
    @commands.command()
    async def rob(self, ctx, *, member: discord.Member):
        await ctx.reply("No.", mention_author = False)
    
    @commands.command()
    async def gamble(self, ctx, amount: str):
        with open("balance.json") as file:
            balance = json.load(file)
        if str(ctx.author.id) not in balance:
            balance[str(ctx.author.id)] = {"wallet": 0, "bank": 0}
        if amount.lower() == "all":
            amount = balance[str(ctx.author.id)]["wallet"]
        else:
            amount = int(amount)
        if amount > 0:
            if balance[str(ctx.author.id)]["wallet"] >= amount:
                p1 = random.randint(2, 12)
                p2 = random.randint(2, 12)
                if p1 > p2:
                    balance[str(ctx.author.id)]["wallet"] += amount
                    await ctx.reply(f"You won ${amount}!\n{p1} | {p2}", mention_author = False)
                elif p1 < p2:
                    balance[str(ctx.author.id)]["wallet"] -= amount
                    await ctx.reply(f"You lost ${amount}.\n{p1} | {p2}", mention_author = False)
                else:
                    await ctx.reply(f"Tie?\n{p1} | {p2}", mention_author = False)
            else:
                await ctx.reply(f"You are ${balance[str(ctx.author.id)]['wallet'] - amount} short.", mention_author = False)
        else:
            await ctx.reply("Provide a valid amount greater than 0.", mention_author = False)
        with open("balance.json", "w") as file:
            json.dump(balance, file, indent = 4)

def setup(client):
    client.add_cog(Currency(client))