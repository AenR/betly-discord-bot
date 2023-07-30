#                AAA                                                  RRRRRRRRRRRRRRRRR   
#               A:::A                                                 R::::::::::::::::R  
#              A:::::A                                                R::::::RRRRRR:::::R 
#             A:::::::A                                               RR:::::R     R:::::R
#            A:::::::::A            eeeeeeeeeeee    nnnn  nnnnnnnn      R::::R     R:::::R
#           A:::::A:::::A         ee::::::::::::ee  n:::nn::::::::nn    R::::R     R:::::R
#          A:::::A A:::::A       e::::::eeeee:::::een::::::::::::::nn   R::::RRRRRR:::::R 
#         A:::::A   A:::::A     e::::::e     e:::::enn:::::::::::::::n  R:::::::::::::RR  
#        A:::::A     A:::::A    e:::::::eeeee::::::e  n:::::nnnn:::::n  R::::RRRRRR:::::R 
#       A:::::AAAAAAAAA:::::A   e:::::::::::::::::e   n::::n    n::::n  R::::R     R:::::R
#      A:::::::::::::::::::::A  e::::::eeeeeeeeeee    n::::n    n::::n  R::::R     R:::::R
#     A:::::AAAAAAAAAAAAA:::::A e:::::::e             n::::n    n::::n  R::::R     R:::::R
#    A:::::A             A:::::Ae::::::::e            n::::n    n::::nRR:::::R     R:::::R
#   A:::::A               A:::::Ae::::::::eeeeeeee    n::::n    n::::nR::::::R     R:::::R
#  A:::::A                 A:::::Aee:::::::::::::e    n::::n    n::::nR::::::R     R:::::R
# AAAAAAA                   AAAAAAA eeeeeeeeeeeeee    nnnnnn    nnnnnnRRRRRRRR     RRRRRRR

import interactions
import sqlite3
import yaml
import datetime
import random
from interactions import listen
from interactions import *
import asyncio

#<----------Config---------->
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)
bot = interactions.Client(token=config["token"])

@listen()
async def on_ready():
    user = bot.user
    server_count = len(bot.guilds)
    print(f"Bot is ready. Logged in as {user}.")
    print(f"Bot is available on: {server_count} servers.")
    print(f"Bot latency: {bot.latency:.0f}ms")
    await bot.change_presence(activity=f"Betly! in {len(bot.guilds)} servers. /register first", status=Status.IDLE)
    for guild in bot.guilds:
        print(f"Server Name: {guild.name} (ID: {guild.id})")
#<----------Config---------->

#<----------DB---------->
connection = sqlite3.connect("database.db")
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, discord_id TEXT UNIQUE, username TEXT, money INTEGER DEFAULT 100, exp INTEGER DEFAULT 0, dailydate DATE, banned BOOL DEFAULT 0)")
#<----------/DB---------->

#<----------Register---------->
@interactions.slash_command(
    name="register",
    description="Register with user id",
)
async def get_user_id(ctx: interactions.SlashContext):
    user_id = ctx.user.id

    cursor.execute("SELECT discord_id FROM users WHERE discord_id=?", (str(user_id),))
    existing_user = cursor.fetchone()
    cursor.execute("SELECT banned FROM users WHERE discord_id=?", (str(user_id),))
    banned = cursor.fetchone()
    if existing_user:
        await ctx.send("You are **already** registered to the system.")
    elif banned:
        await ctx.send("You are **banned** from the system.")
        return
    else:
        username = ctx.user.username+"#"+ctx.user.discriminator
        cursor.execute("INSERT INTO users (discord_id, username) VALUES (?, ?)", (str(user_id), username))
        connection.commit()
        await ctx.send(f"User ID: {user_id} **saved** to the database.")
#<----------/Register---------->

#<----------Ban User---------->
@interactions.slash_command(
    name="ban",
    description="Ban a user",
    options=[
        {
            "name": "user",
            "description": "Enter the user's Discord ID",
            "type": 3,
            "required": True
        }
    ]
)
async def ban_user(ctx: interactions.SlashContext, user: str):
    user_id = ctx.user.id
    if (str(user_id) != config["admins"]):
        await ctx.send("You don't have permission to use this command.")
        return

    try:
        user_id = int(user)
    except ValueError:
        await ctx.send("**Invalid** user ID.")
        return

    cursor.execute("UPDATE users SET banned = 1, money = 0, exp = 0 WHERE discord_id = ?", (str(user_id),))
    connection.commit()
    await ctx.send(f"User with ID: {user_id} has been banned.")

#<----------/Ban User---------->

#<----------Set Money---------->
@interactions.slash_command(
    name="set-money",
    description="Set user's money",
    options=[
        {
            "name": "user",
            "description": "Enter the user's Discord ID",
            "type": 3,
            "required": True
        },
        {
            "name": "amount",
            "description": "Enter the new amount of money",
            "type": 4,
            "required": True
        }
    ]
)
async def set_money(ctx: interactions.SlashContext, user: str, amount: int):
    admin_id = ctx.user.id
    if (str(admin_id) != config["admins"]):
        await ctx.send("You don't have permission to use this command.")
        return

    try:
        user_id = int(user)
    except ValueError:
        await ctx.send("**Invalid** user ID.")
        return

    cursor.execute("UPDATE users SET money = ? WHERE discord_id = ?", (amount, str(user_id)))
    connection.commit()
    await ctx.send(f"The money of user with ID: {user_id} has been set to **{amount}**.")
#<----------/Set Money---------->

#<----------Set Experience---------->
@interactions.slash_command(
    name="set-experience",
    description="Set user's experience",
    options=[
        {
            "name": "user",
            "description": "Enter the user's Discord ID",
            "type": 3,
            "required": True
        },
        {
            "name": "amount",
            "description": "Enter the new amount of experience",
            "type": 4,
            "required": True
        }
    ]
)
async def set_experience(ctx: interactions.SlashContext, user: str, amount: int):
    admin_id = ctx.user.id
    if (str(admin_id) != config["admins"]):
        await ctx.send("You don't have permission to use this command.")
        return

    try:
        user_id = int(user)
    except ValueError:
        await ctx.send("**Invalid** user ID.")
        return

    cursor.execute("UPDATE users SET exp = ? WHERE discord_id = ?", (amount, str(user_id)))
    connection.commit()
    await ctx.send(f"The experience of user with ID: {user_id} has been set to **{amount}**.")
#<----------/Set Experience---------->

#<----------Reset Daily---------->
@interactions.slash_command(
    name="reset-daily",
    description="Reset user's daily gift",
    options=[
        {
            "name": "user",
            "description": "Enter the user's Discord ID",
            "type": 3,
            "required": True
        }
    ]
)
async def reset_daily(ctx: interactions.SlashContext, user: str):
    admin_id = ctx.user.id
    if (str(admin_id) != config["admins"]):
        await ctx.send("You don't have permission to use this command.")
        return

    try:
        user_id = int(user)
    except ValueError:
        await ctx.send("**Invalid** user ID.")
        return
    cursor.execute("UPDATE users SET dailydate = ? WHERE discord_id = ?", ('', str(user_id)))
    connection.commit()
    await ctx.send(f"The daily gift of user with ID: {user_id} has been **reset**.")
#<----------/Reset Daily---------->

#<----------Daily Gift---------->
@interactions.slash_command(
    name="daily-gift",
    description="Claim your daily gift."
)
async def dailyGift(ctx: interactions.SlashContext):
    user_id = ctx.user.id
    current_date = datetime.date.today()

    cursor.execute("SELECT banned FROM users WHERE discord_id=?", (str(user_id),))
    banned = cursor.fetchone()
    if banned and banned[0] == 1:
        await ctx.send("You are **banned** from the system.")
        return
    
    cursor.execute("SELECT discord_id FROM users WHERE discord_id=?", (str(user_id),))
    existing_user = cursor.fetchone()
    if not existing_user:
        await ctx.send("You need to **register** before claiming the daily gift. Use the `/register` command to register.")
        return

    cursor.execute("SELECT dailydate FROM users WHERE discord_id=?", (str(user_id),))
    last_claim_date = cursor.fetchone()

    if last_claim_date and last_claim_date[0] == current_date.isoformat():
        embed = interactions.Embed(
            title="Betly Daily Gift",
            color=0xffcc00,
            description=f"You have **already claimed** your daily gift today.")
        await ctx.send(embed=embed)
    else:
        cursor.execute("SELECT money FROM users WHERE discord_id=?", (str(user_id),))
        money = cursor.fetchone()

        if money:
            updated_money = money[0] + config["daily_gift_amount"]
            cursor.execute("UPDATE users SET money=?, dailydate=? WHERE discord_id=?", (updated_money, current_date.isoformat(), str(user_id)))
        else:
            cursor.execute("INSERT INTO users (discord_id, money, dailydate) VALUES (?, ?, ?)", (str(user_id), config["daily_gift_amount"], current_date.isoformat()))

        connection.commit()
        embed = interactions.Embed(
            title="Betly Daily Gift",
            color=0xffcc00,
            description=f"You claimed your daily gift of **{config['daily_gift_amount']}** cukka.")
        await ctx.send(embed=embed)

#<----------/Daily Gift---------->

#<----------Balance---------->
@interactions.slash_command(
    name="balance",
    description="Shows your balance",
)
async def balance(ctx: interactions.SlashContext):
    user_id = ctx.user.id
    cursor.execute("SELECT money FROM users WHERE discord_id=?", (str(user_id),))
    money = cursor.fetchone()

    cursor.execute("SELECT banned FROM users WHERE discord_id=?", (str(user_id),))
    banned = cursor.fetchone()
    if banned and banned[0] == 1:
        await ctx.send("You are **banned** from the system.")
        return

    if money:
        embed = interactions.Embed(
            title="Betly Balance",
            color=0xffcc00,
            description=f"You have: **{money[0]}** cukka.")
        await ctx.send(embed=embed)
    else:
        await ctx.send("User **not found** in the database.")
#<----------/Balance---------->

#<----------Experience---------->
@interactions.slash_command(
    name="experience",
    description="Shows your experience",
)
async def experience(ctx: interactions.SlashContext):
    user_id = ctx.user.id
    cursor.execute("SELECT exp FROM users WHERE discord_id=?", (str(user_id),))
    exp = cursor.fetchone()

    cursor.execute("SELECT banned FROM users WHERE discord_id=?", (str(user_id),))
    banned = cursor.fetchone()
    if banned and banned[0] == 1:
        await ctx.send("You are **banned** from the system.")
        return

    if exp:
        embed = interactions.Embed(
            title="Betly Experience",
            color=0xffcc00,
            description=f"You have: **{exp[0]}** exp.")
        await ctx.send(embed=embed)
    else:
        await ctx.send("User **not found** in the database.")
#<----------/Experience---------->

#<----------Send Money---------->
@interactions.slash_command(
    name="send-money",
    description="Send money to another user.",
    options=[
        {
            "name": "recipient",
            "description": "Enter the recipient's Discord ID",
            "type": 3,
            "required": True
        },
        {
            "name": "amount",
            "description": "Enter the amount of money to send",
            "type": 4,
            "required": True
        }
    ]
)
async def sendMoney(ctx: interactions.SlashContext, recipient: str, amount: int):
    sender_id = ctx.user.id

    try:
        recipient_id = int(recipient)
    except ValueError:
        await ctx.send("**Invalid** recipient ID.")
        return

    cursor.execute("SELECT money FROM users WHERE discord_id=?", (str(sender_id),))
    sender_money = cursor.fetchone()

    if sender_money and sender_money[0] >= amount:
        updated_sender_money = sender_money[0] - amount
        cursor.execute("UPDATE users SET money=? WHERE discord_id=?", (updated_sender_money, str(sender_id)))

        cursor.execute("SELECT money FROM users WHERE discord_id=?", (str(recipient_id),))
        recipient_money = cursor.fetchone()

        if recipient_money:
            updated_recipient_money = recipient_money[0] + amount
            cursor.execute("UPDATE users SET money=? WHERE discord_id=?", (updated_recipient_money, str(recipient_id)))
        else:
            cursor.execute("INSERT INTO users (discord_id, money) VALUES (?, ?)", (str(recipient_id), amount))

        connection.commit()
        embed = interactions.Embed(
            title="Betly Send Money",
            color=0xffcc00,
            description=f"Successfully sent **{amount}** cukka to user with ID: {recipient_id}.")
        await ctx.send(embed=embed)
    else:
        await ctx.send("You **don't have enough money** to send.")
#<----------/Send Money---------->

#<----------Help---------->
@interactions.slash_command(
    name="help",
    description="Help Menu",
    options=[
        {
            "name": "category",
            "description": "Enter the category ('games', 'general' or 'admin')",
            "type": 3,
            "required": False
        }
    ]
)
async def help(ctx: interactions.SlashContext, category: str = None):
    if category == "games":
        await send_games_help(ctx)
    elif category == "admin":
        await send_admin_help(ctx)
    elif category == "general":
        await send_general_help(ctx)
    else:
        embed = interactions.Embed(
            title="Betly Help Menu",
            color=0xffcc00,
            description=f"* `/help general` - Shows general commands\n* `/help games` - Shows game commands\n* `/help admin` - Shows admin commands")
        await ctx.send(embed=embed)

async def send_games_help(ctx: interactions.SlashContext):
    embed = interactions.Embed(
            title="Betly Games Commands",
            color=0xffcc00,
            description=f"* `/play-coinflip` - Play Coin Flip\n* `/play-guess 1-6` - Play Guess Game\n* `/play-same-dice` - Play Same Dice Game\n* `/play-slots` - Play slots\n* `/play-roulette` - Play roulette\n* `/play-rps` - Play Rock Paper Scissors")
    await ctx.send(embed=embed)

async def send_admin_help(ctx: interactions.SlashContext):
    embed = interactions.Embed(
            title="Betly Admin Commands",
            color=0xffcc00,
            description=f"* `/set-money id amount` - Set user's money\n* `/set-experience id amount` - Set user's experience\n* `/ban id` - Ban a user\n* `/reset-daily id` - Reset user's daily gift")
    await ctx.send(embed=embed)

async def send_general_help(ctx: interactions.SlashContext):
    embed = interactions.Embed(
            title="Betly Commands",
            color=0xffcc00,
            description=f"* `/register` - Register with discord id(required)\n* `/daily-gift` - Claim your 50 cukka daily gift\n* `/top-rankings` - Show top rankings\n* `/balance` - Shows your balance\n* `/experience` - Shows your experience\n* `/author` - Learn about my author\n* `/vote` - Vote me on TOP.GG\n* `/help games` - Display games commands\n* `/help admin` - Display admin commands")
    await ctx.send(embed=embed)
#<----------/Help---------->

#<----------Author---------->
@interactions.slash_command(
    name="author",
    description="Learn about my author",
)
async def author(ctx: interactions.SlashContext):
    embed = interactions.Embed(
            title="Betly Author",
            color=0xffcc00,
            description=f"My author: <@535033289346514964>\nMy Support Server: https://discord.gg/QUAxwRTCWv\nMy Website: https://betly.netlify.app/")
    await ctx.send(embed=embed)
#<----------/Author---------->

#<----------Vote---------->
@interactions.slash_command(
    name="vote",
    description="Vote me on TOP.GG",
)
async def author(ctx: interactions.SlashContext):
    embed = interactions.Embed(
            title="Betly Vote",
            color=0xffcc00,
            description=f"You can vote every 12 hours: https://top.gg/bot/1130504469923254362")
    await ctx.send(embed=embed)
#<----------/Vote---------->

#<----------Ranking---------->
def get_top_rankings():
    cursor.execute("SELECT username, money FROM users ORDER BY money DESC LIMIT 10")
    top_rankings = cursor.fetchall()
    return top_rankings

@interactions.slash_command(
    name="top-rankings",
    description="Show top rankings",
)
async def top_rankings(ctx: interactions.SlashContext):
    top_rankings = get_top_rankings()

    if top_rankings:
        embed = interactions.Embed(
            title="Betly Top Rankings",
            color=0xffcc00,
            description="Top 10 richest players:"
        )
        for rank, (username, money) in enumerate(top_rankings, 1):
            embed.add_field(name=f"#{rank} {username}", value=f"Cukka: {money}", inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send("No users found in the database.")
#<----------/Ranking---------->

#<----------Coin Flip---------->
@interactions.slash_command(
    name="play-coinflip",
    description="Play CoinFlip.",
    options=[
        {
            "name": "bet",
            "description": "Enter your bet please",
            "type": 4,
            "required": True
        }
    ]
)
async def enterBet(ctx: interactions.SlashContext, bet: int):
    user_id = ctx.user.id
    cursor.execute("SELECT money FROM users WHERE discord_id=?", (str(user_id),))
    money = cursor.fetchone()

    cursor.execute("SELECT banned FROM users WHERE discord_id=?", (str(user_id),))
    banned = cursor.fetchone()
    if banned and banned[0] == 1:
        await ctx.send("You are **banned** from the system.")
        return

    if money and money[0] >= bet:
        cursor.execute("UPDATE users SET money=money-? WHERE discord_id=?", (bet, str(user_id)))
        connection.commit()

        coin_sides = ["Heads", "Tails"]
        selected_side = "Heads"
        
        coin_flip_message = await ctx.send(f"Flipping the coin")
        for i in range(2):
            await asyncio.sleep(0.5)
            await coin_flip_message.edit(content=f"Flipping the coin{'.' * (i+1)}")

        await asyncio.sleep(0.5)

        # Determine the result
        result = random.choice(coin_sides)
        if result == selected_side:
            winnings = bet * 2
            cursor.execute("UPDATE users SET money=money+? WHERE discord_id=?", (winnings, str(user_id)))
            cursor.execute("UPDATE users SET exp=exp+? WHERE discord_id=?", (2, str(user_id)))
            connection.commit()
            await coin_flip_message.edit(content=f"The coin landed on **{result}**! You won **{winnings}** cukka. And **2** xp.")
        else:
            await coin_flip_message.edit(content=f"The coin landed on **{result}**! You lost **{bet}** cukka.")
    else:
        await ctx.send("You **don't have enough money** to place that bet.")
#<----------/Coin Flip---------->

#<----------Guess---------->
@interactions.slash_command(
    name="play-guess",
    description="Play Guess Game.",
    options=[
        {
            "name": "bet",
            "description": "Enter your bet please",
            "type": 4,
            "required": True
        },
        {
            "name": "guess",
            "description": "Enter your guess please",
            "type": 4,
            "required": True
        }
            ]
)
async def play_guess(ctx: interactions.SlashContext, bet: int, guess: int):
    user_id = ctx.user.id
    cursor.execute("SELECT money FROM users WHERE discord_id=?", (str(user_id),))
    money = cursor.fetchone()

    cursor.execute("SELECT banned FROM users WHERE discord_id=?", (str(user_id),))
    banned = cursor.fetchone()
    if banned and banned[0] == 1:
        await ctx.send("You are **banned** from the system.")
        return

    if money and money[0] >= bet:
        cursor.execute("UPDATE users SET money=money-? WHERE discord_id=?", (bet, str(user_id)))
        connection.commit()

        result = random.randint(1, 6)
        if guess == result:
            winnings = bet * 6
            cursor.execute("UPDATE users SET money=money+? WHERE discord_id=?", (winnings, str(user_id)))
            cursor.execute("UPDATE users SET exp=exp+? WHERE discord_id=?", (6, str(user_id)))
            connection.commit()
            await ctx.send(f"You guessed **correctly**! The number was **{result}**. You won **{winnings}** cukka. And **6** xp.")
        else:
            await ctx.send(f"You guessed **incorrectly**. The number was **{result}**. You lost **{bet}** cukka.")
    else:
        await ctx.send("You **don't have enough money** to place that bet.")
#<----------/Guess---------->

#<----------Same Dice---------->
@interactions.slash_command(
    name="play-same-dice",
    description="Play Same Dice Game.",
    options=[
        {
            "name": "bet",
            "description": "Enter your bet please",
            "type": 4,
            "required": True
        }
            ]
)
async def play_same_dice(ctx: interactions.SlashContext, bet: int):
    user_id = ctx.user.id
    cursor.execute("SELECT money FROM users WHERE discord_id=?", (str(user_id),))
    money = cursor.fetchone()

    cursor.execute("SELECT banned FROM users WHERE discord_id=?", (str(user_id),))
    banned = cursor.fetchone()
    if banned and banned[0] == 1:
        await ctx.send("You are **banned** from the system.")
        return

    if money and money[0] >= bet:
        cursor.execute("UPDATE users SET money=money-? WHERE discord_id=?", (bet, str(user_id)))
        connection.commit()

        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        if dice1 == dice2:
            winnings = bet * 10
            cursor.execute("UPDATE users SET money=money+? WHERE discord_id=?", (winnings, str(user_id)))
            cursor.execute("UPDATE users SET exp=exp+? WHERE discord_id=?", (10, str(user_id)))
            connection.commit()
            await ctx.send(f"First dice was **{dice1}** and second dice was **{dice2}**. You won **{winnings}** cukka. And **10** xp.")
        else:
            await ctx.send(f"First dice was **{dice1}** and second dice was **{dice2}**. You lost **{bet}** cukka.")
    else:
        await ctx.send("You **don't have enough money** to place that bet.")
#<----------/Same Dice---------->

#<----------Slots---------->
# Define the slot machine emojis
slotItems = ["🍒", "🍋", "🍉", "🍇", "💎", "🍀"]

@interactions.slash_command(
    name="play-slots",
    description="Play Slots.",
    options=[
        {
            "name": "bet",
            "description": "Enter your bet please",
            "type": 4,
            "required": True
        }
    ]
)
async def play_slots(ctx: interactions.SlashContext, bet: int):
    user_id = ctx.user.id
    cursor.execute("SELECT money FROM users WHERE discord_id=?", (str(user_id),))
    money = cursor.fetchone()

    cursor.execute("SELECT banned FROM users WHERE discord_id=?", (str(user_id),))
    banned = cursor.fetchone()
    if banned and banned[0] == 1:
        await ctx.send("You are **banned** from the system.")
        return

    if money and money[0] >= bet:
        cursor.execute("UPDATE users SET money=money-? WHERE discord_id=?", (bet, str(user_id)))
        connection.commit()

        # Display the initial slot machine message
        slot_machine_msg = await ctx.send("Spinning the slot machine... 🎰")
        await asyncio.sleep(1)

        # Simulate spinning and update the slot machine message
        for _ in range(3):
            slotMachine = [random.choice(slotItems) for i in range(3)]
            slots = ("-".join(slotMachine))
            await slot_machine_msg.edit(content=f"[{slots}] Spinning the slot machine... 🎰")
            await asyncio.sleep(1)

        # Display the final result
        slotMachine = [random.choice(slotItems) for i in range(3)]
        slots = ("-".join(slotMachine))
        
        if slotMachine[0] == slotMachine[1] == slotMachine[2]:
            winnings = bet * 4
            cursor.execute("UPDATE users SET money=money+? WHERE discord_id=?", (winnings, str(user_id)))
            cursor.execute("UPDATE users SET exp=exp+? WHERE discord_id=?", (4, str(user_id)))
            connection.commit()
            await slot_machine_msg.edit(content=f"[{slots}] You won **{winnings}** cukka. And **4** xp.")
        else:
            await slot_machine_msg.edit(content=f"[{slots}] You lost **{bet}** cukka.")
    else:
        await ctx.send("You **don't have enough money** to place that bet.")
#<----------/Slots---------->

#<----------Roulette---------->
@interactions.slash_command(
    name="play-roulette",
    description="Play Roulette.",
    options=[
        {
            "name": "bet",
            "description": "Enter your bet please",
            "type": 4,
            "required": True
        },
        {
            "name": "guess",
            "description": "Enter your guess (red, black, green, or a number between 1 and 36) please",
            "type": 3,  # Changed the type to 3 for a string input
            "required": True
        }
    ]
)
async def play_roulette(ctx: interactions.SlashContext, bet: int, guess: str):
    user_id = ctx.user.id
    cursor.execute("SELECT money FROM users WHERE discord_id=?", (str(user_id),))
    money = cursor.fetchone()

    cursor.execute("SELECT banned FROM users WHERE discord_id=?", (str(user_id),))
    banned = cursor.fetchone()
    if banned and banned[0] == 1:
        await ctx.send("You are **banned** from the system.")
        return

    if money and money[0] >= bet:
        cursor.execute("UPDATE users SET money=money-? WHERE discord_id=?", (bet, str(user_id)))
        connection.commit()

        result = random.randint(0, 36)
        color = "green" if result == 0 else "red" if result % 2 == 1 else "black"

        # Check if the guess is valid
        valid_guesses = ["red", "black", "green"] + [str(i) for i in range(1, 37)]
        if guess.lower() in valid_guesses:
            if guess.lower() == color or guess == str(result):
                winnings = bet * 36 if guess.lower() == str(result) else bet*2
                cursor.execute("UPDATE users SET money=money+? WHERE discord_id=?", (winnings, str(user_id)))
                cursor.execute("UPDATE users SET exp=exp+? WHERE discord_id=?", (36 if guess.lower() == str(result) else 10, str(user_id)))
                connection.commit()
                await ctx.send(f"You guessed **correctly**! The result was **{color} {result}**. You won **{winnings}** cukka. And **{36 if guess.lower() == str(result) else 10}** xp.")
            else:
                await ctx.send(f"You guessed **incorrectly**. The result was **{color} {result}**. You lost **{bet}** cukka.")
        else:
            await ctx.send("Invalid guess. Please enter 'red', 'black', 'green', or a number between 1 and 36.")
    else:
        await ctx.send("You **don't have enough money** to place that bet.")
#<----------/Roulette---------->

#<----------Rock Paper Scissors---------->
@interactions.slash_command(
    name="play-rps",
    description="Play Rock-Paper-Scissors.",
    options=[
        {
            "name": "bet",
            "description": "Enter your bet please",
            "type": 4,
            "required": True
        },
        {
            "name": "choice",
            "description": "Enter your choice (rock, paper, or scissors) please",
            "type": 3,
            "required": True
        }
    ]
)
async def play_rps(ctx: interactions.SlashContext, bet: int, choice: str):
    user_id = ctx.user.id
    cursor.execute("SELECT money FROM users WHERE discord_id=?", (str(user_id),))
    money = cursor.fetchone()

    cursor.execute("SELECT banned FROM users WHERE discord_id=?", (str(user_id),))
    banned = cursor.fetchone()
    if banned and banned[0] == 1:
        await ctx.send("You are **banned** from the system.")
        return

    choices = ["rock", "paper", "scissors"]
    bot_choice = random.choice(choices)

    if choice.lower() not in choices:
        await ctx.send("Invalid choice. Please enter 'rock', 'paper', or 'scissors'.")
        return

    if money and money[0] >= bet:
        if choice.lower() == bot_choice:
            await ctx.send(f"It's a **tie**! You and the bot both chose {bot_choice}.")
        elif (choice.lower() == "rock" and bot_choice == "scissors") or \
             (choice.lower() == "paper" and bot_choice == "rock") or \
             (choice.lower() == "scissors" and bot_choice == "paper"):
            winnings = bet * 3
            cursor.execute("UPDATE users SET money=money+? WHERE discord_id=?", (winnings, str(user_id)))
            cursor.execute("UPDATE users SET exp=exp+? WHERE discord_id=?", (3, str(user_id)))  # Give some experience points
            connection.commit()
            await ctx.send(f"**Congratulations!** You won **{winnings}** cukka. The bot chose {bot_choice}. You gained **3** xp.")
        else:
            cursor.execute("UPDATE users SET money=money-? WHERE discord_id=?", (bet, str(user_id)))
            connection.commit()
            await ctx.send(f"**You lost!** The bot chose {bot_choice}. You lost **{bet}** cukka.")
    else:
        await ctx.send("You **don't have enough money** to place that bet.")
#<----------/Rock Paper Scissors---------->

bot.start()