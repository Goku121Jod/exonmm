main.py

import discord from discord.ext import commands from discord.ui import View, Button import random import string import json

Load config

with open("config.json") as f: config = json.load(f)

TOKEN = config["token"] CATEGORY_ID = config["category_id"] PREFIX = "$"

intents = discord.Intents.all() bot = commands.Bot(command_prefix=PREFIX, intents=intents)

def generate_random_id(length=36): return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_litecoin_address(): try: with open("ltcaddy.txt", "r") as f: addresses = [line.strip() for line in f if line.strip()] return random.choice(addresses) except Exception: return "No LTC address available"

@bot.event async def on_ready(): print(f"Bot is ready as {bot.user}")

Wait for developer ID message

ticket_sessions = {}

@bot.event async def on_message(message): if message.author.bot: return

# Check if in a ticket and waiting for developer ID
if message.channel.id in ticket_sessions and ticket_sessions[message.channel.id]["awaiting_dev_id"]:
    try:
        dev_id = int(message.content.strip())
        guild = message.guild
        dev_user = await bot.fetch_user(dev_id)
        await message.channel.set_permissions(dev_user, read_messages=True, send_messages=True)

        # Respond with embedded messages
        await send_middleman_embeds(message.channel, message.author.mention, dev_user)

        ticket_sessions[message.channel.id]["awaiting_dev_id"] = False
    except Exception as e:
        await message.channel.send(embed=discord.Embed(description="❌ Invalid Developer ID.", color=discord.Color.red()))
    return

await bot.process_commands(message)

@bot.command() @commands.has_permissions(administrator=True) async def start(ctx): if ctx.channel.category_id != CATEGORY_ID: return

random_code = generate_random_id()
await ctx.send(random_code)

embed = discord.Embed(description="Please send the **Developer ID** of the user you are dealing with.\nType `cancel` to cancel the deal.", color=discord.Color.blue())
await ctx.send(embed=embed)

ticket_sessions[ctx.channel.id] = {"awaiting_dev_id": True}

class RoleSelectView(View): def init(self, msg): super().init(timeout=None) self.msg = msg self.buyer = None self.seller = None

@discord.ui.button(label="Sending", style=discord.ButtonStyle.blurple)
async def sending(self, interaction: discord.Interaction, button: Button):
    self.buyer = interaction.user
    await self.update_message(interaction)

@discord.ui.button(label="Receiving", style=discord.ButtonStyle.green)
async def receiving(self, interaction: discord.Interaction, button: Button):
    self.seller = interaction.user
    await self.update_message(interaction)

@discord.ui.button(label="Reset", style=discord.ButtonStyle.danger)
async def reset(self, interaction: discord.Interaction, button: Button):
    self.buyer = None
    self.seller = None
    await self.update_message(interaction, reset=True)

async def update_message(self, interaction, reset=False):
    embed = discord.Embed(title="Role Selection",
                          description="Please select one of the following buttons that corresponds to your role in this deal. Once selected, both users must confirm to proceed.\n\n**Sending Litecoin ( Buyer )**\n{}\n\n**Receiving Litecoin ( Seller )**\n{}".format(
                              self.buyer.mention if self.buyer else "None",
                              self.seller.mention if self.seller else "None"),
                          color=discord.Color.dark_gold())
    await self.msg.edit(embed=embed, view=self)
    await interaction.response.defer()

async def send_middleman_embeds(channel, author_mention, dev_user): # 1. Added to ticket embed1 = discord.Embed(description=f"{author_mention} added {dev_user.mention} to the ticket!", color=discord.Color.blurple()) await channel.send(embed=embed1)

# 2. Welcome Message
embed2 = discord.Embed(title="Crypto MM",
                       description="Welcome to our automated cryptocurrency Middleman system! Your cryptocurrency will be stored securely till the deal is completed. The system ensures the security of both users, by securely storing the funds until the deal is complete and confirmed by both parties.",
                       color=discord.Color.blue())
embed2.set_footer(text="Created by: Exploit")
await channel.send(embed=embed2)

# 3. Warning Message
embed3 = discord.Embed(title="Please Read!",
                       description="Please check deal info, confirm your deal and discuss about tos and warranty of that product. Ensure all conversations related to the deal are done within this ticket. Failure to do so may put you at risk of being scammed.",
                       color=discord.Color.red())
await channel.send(embed=embed3)

# 4. Role Selection
embed4 = discord.Embed(title="Role Selection",
                       description="Please select one of the following buttons that corresponds to your role in this deal. Once selected, both users must confirm to proceed.\n\n**Sending Litecoin ( Buyer )**\nNone\n\n**Receiving Litecoin ( Seller )**\nNone",
                       color=discord.Color.dark_gold())
msg = await channel.send(embed=embed4)
await msg.edit(view=RoleSelectView(msg))

bot.run(TOKEN)

