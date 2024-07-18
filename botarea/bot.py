import os
import asyncio
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands

active_reminders_remind = {}
active_reminders_remindl = {}

# Load environment variables from a .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    raise ValueError("No token found. Please ensure that the .env file contains the DISCORD_TOKEN variable.")

# Check if user has administrator permissions
def acheck(ctx):
    return ctx.author.guild_permissions.administrator

# Generate a random number between 1 and i
def rnum(i):
    return random.randint(1, i)

# Send a reminder to a user after a certain time
async def send_reminder(user, reminder, time, user_id, command_name):
    await asyncio.sleep(time)
    await user.send(f"Reminder: {reminder}")

    # Remove the completed reminder from the correct active_reminders list
    if command_name == 'remind':
        active_reminders_to_check = active_reminders_remind
    elif command_name == 'remindl':
        active_reminders_to_check = active_reminders_remindl
    else:
        return

    if user_id in active_reminders_to_check:
        active_user_reminders = active_reminders_to_check[user_id]
        active_user_reminders[:] = [r for r in active_user_reminders if r['reminder'] != reminder]

intents = discord.Intents.default()
intents.typing = True
intents.message_content = True  

bot = commands.Bot(command_prefix=';', intents=intents)
cmd = ";"  # Command prefix

@bot.event
async def on_ready():
    print(f"Logged in as a bot {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send("sike")

# Custom help command
bot.remove_command('help')
@bot.command()
async def help(ctx, command_name: str = None):
    if command_name is None:
        command_list = "\n".join([f";{cmd.name}" for cmd in bot.commands])
        await ctx.send(f"Available commands:\n{command_list}\nUse `{cmd}help command_name` to get help on a specific command.")
    else:
        help_messages = {
            "remind": "Set a one-time reminder. Usage: `;remind time reminder_text`",
            "remindl": "Set a recurring reminder. Usage: `;remindl time reminder_text`",
            "end": "End a reminder. Usage: `;end command_name index`",
            "roll": "Roll dice. Usage: `;roll NdM [extra]`",
            "tnt": "Purge messages in the channel. Usage: `;tnt num_messages`"
        }
        await ctx.send(help_messages.get(command_name, "Invalid command name. Please specify a valid command or use `;help` to see the list of available commands."))

# Set a one-time reminder
@bot.command()
async def remind(ctx, time: str, *, reminder: str):
    try:
        time = int(time)
        if time <= 0:
            await ctx.send("Please provide a positive time value.")
            return

        await ctx.send("Sure, reminder set")
        user_id = ctx.author.id
        if user_id not in active_reminders_remind:
            active_reminders_remind[user_id] = []

        task = asyncio.create_task(send_reminder(ctx.author, reminder, time, user_id, 'remind'))
        active_reminders_remind[user_id].append({
            'command': 'remind',
            'reminder': reminder,
            'task': task
        })

    except ValueError:
        await ctx.send("Invalid time format. Please provide a positive integer for time.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Set a recurring reminder
@bot.command()
async def remindl(ctx, time: str, *, reminder: str):
    try:
        time = int(time)
        if time <= 0:
            await ctx.send("Please provide a positive time value.")
            return

        await ctx.send("Sure, reminder set")

        async def send_repeated_reminders():
            user = ctx.author
            while True:
                await asyncio.sleep(time)
                await user.send(f"Reminder: {reminder}")

        user_id = ctx.author.id
        if user_id not in active_reminders_remindl:
            active_reminders_remindl[user_id] = []

        task = asyncio.create_task(send_repeated_reminders())
        active_reminders_remindl[user_id].append({
            'command': 'remindl',
            'reminder': reminder,
            'task': task
        })

    except ValueError:
        await ctx.send("Invalid time format. Please provide a positive integer for time.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# End a reminder
@bot.command()
async def end(ctx, command_name: str, index: int = None):
    try:
        user_id = ctx.author.id
        if command_name == 'remind':
            active_reminders_to_check = active_reminders_remind
        elif command_name == 'remindl':
            active_reminders_to_check = active_reminders_remindl
        else:
            await ctx.send("Invalid command name. Please specify 'remind' or 'remindl'.")
            return

        if user_id in active_reminders_to_check:
            if not active_reminders_to_check[user_id]:
                await ctx.send(f"Index of active {command_name} reminders is empty.")
                return
            if index is None:
                await ctx.send(f"Index of active {command_name} reminders:\n" + "\n".join([f"{i}: {reminder['reminder']}" for i, reminder in enumerate(active_reminders_to_check[user_id])]))
                return
            if 0 <= index < len(active_reminders_to_check[user_id]):
                active_reminders_to_check[user_id][index]['task'].cancel()
                await ctx.send(f"{command_name.capitalize()} reminder ended.")
                del active_reminders_to_check[user_id][index]
            else:
                await ctx.send("Invalid reminder index. Please provide a valid index.")
        else:
            await ctx.send(f"You don't have any active {command_name} reminders to end.")

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Roll dice
@bot.command()
async def roll(ctx, exp: str, extra: int = 0):
    try:
        numr, nums = map(int, exp.split('d'))
        if nums in [4, 6, 8, 10, 12, 20, 100]:
            if numr <= 0 or nums <= 0:
                await ctx.send("Please provide valid values for rolls and sides.")
                return
            results = [rnum(nums) for _ in range(numr)]
            total = sum(results) + extra
            await ctx.send(f'Results: {" ".join(map(str, results))}\nTotal: {total}')
        else:
            await ctx.send("That's some weird dice you want there just use a random number generator but here anyways")
            if numr <= 0 or nums <= 0:
                await ctx.send("Please provide valid values for rolls and sides.")
                return
            results = [rnum(nums) for _ in range(numr)]
            total = sum(results) + extra
            await ctx.send(f'Results: {" ".join(map(str, results))}\nTotal: {total}')
    except (ValueError, commands.BadArgument):
        await ctx.send("Invalid dice expression format. Please use the format ';roll NdM [extra]', where N is the number of rolls, M is the number of sides on the die, and [extra] is an optional value to add or subtract.")

# Purge messages in the channel (admin only)
@bot.command()
@commands.has_permissions(administrator=True)
async def tnt(ctx, num_messages: int = 0, severity: str = None):
    if severity == "yes" and num_messages == -1:
        await ctx.channel.purge()
    else:
        await ctx.channel.purge(limit=num_messages + 1)

bot.run(TOKEN)
