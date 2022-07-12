import interactions
import requests
import json
from interactions.ext.tasks import IntervalTrigger, create_task
from dataclasses import dataclass

bot = interactions.Client(token="OTk1NDM3OTY5MDgxMTIyOTY2.GbG0jJ.FymuTjUO79vTIgGymRXROqNIdnHfRUKJzX2jPM",
                          intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

emojiblockerbool = False

necro_auctions_all = []

dealers = ["FearedIce"]

@create_task(IntervalTrigger(30))

async def update_auctions():

    for dealer in trusted_dealers:

        auctions = get_auctions(dealer)

        global necro_auctions_all

        necro_auctions_all, final_str = convert_to_dataclass(auctions)

update_auctions.start()

def safe_num(num):
    if isinstance(num, str):
        num = float(num)
    return float('{:.3g}'.format(abs(num)))

def format_number(num):
    num = safe_num(num)
    sign = ''

    metric = {'T': 1000000000000, 'B': 1000000000, 'M': 1000000, 'K': 1000, '': 1}

    for index in metric:
        num_check = num / metric[index]

        if(num_check >= 1):
            num = num_check
            sign = index
            break

    return f"{str(num).rstrip('0').rstrip('.')}{sign}"

@dataclass
class Auction:
    dealer: str
    item_name: str
    price: str
    type: int
    num_admin_souls: int
    num_hypixel_souls: int
    string_representation: str

trusted_dealers = ["FearedIce"]

def get_auctions(user: str):

    uuid_url = "https://api.mojang.com/users/profiles/minecraft/{username}".format(username=user)

    response = requests.get(uuid_url)

    uuid = response.json().get("id")

    # api_key = f2dd5a2a-b66b-466e-80fb-32e93829781d

    auctions_url = "https://api.hypixel.net/skyblock/auction?key=f2dd5a2a-b66b-466e-80fb-32e93829781d&player={thing_uuid}".format(
        thing_uuid=uuid)

    auctions_response = requests.get(auctions_url)

    auctions = auctions_response.json().get("auctions")

    return auctions

def convert_to_dataclass(auctions):

    keywords = ["eaper", "ummoning", "ecromancer"]

    if (auctions):

        dealers = []
        necroauctions = []
        lore = []
        price = []

        for auction in auctions:

            for keyword in keywords:

                if keyword in auction.get("item_name"):

                    username_url = "https://api.mojang.com/user/profiles/{uuid}/names".format(uuid=auction.get("auctioneer"))

                    response = requests.get(username_url)

                    username = response.json()[-1].get("name")

                    dealers.append(username)
                    necroauctions.append(auction.get("item_name"))
                    lore.append(auction.get("item_lore"))
                    price.append(auction.get("starting_bid"))

    auctions_list = []
    final_souls_string = ""

    if necroauctions:

        for i in range(len(necroauctions)):

            a = Auction("", "", "", 0, 0, 0, "")

            item_name = necroauctions[i]
            item_lore = lore[i]
            item_price = price[i]

            souls = []

            if "hypixel" in item_lore:

                for i in range(item_lore.count("hypixel")):

                    souls.append(admin_name)

                    a.num_hypixel_souls += 1

            for admin_name in admin_names:

                if admin_name in item_lore:

                    for i in range(item_lore.count(admin_name)):

                        souls.append(admin_name)

            a.dealer = dealers[i]
            a.num_admin_souls = len(souls)
            a.item_name = item_name
            a.price = item_price

            if "eaper" in item_name:
                a.type = 1
            else:
                a.type = 2

            souls_string = "**{item_name}**".format(item_name=item_name)

            if "Ultimate Wise V" in item_lore:
                souls_string += " (With **Ultimate Wise V**)"

            item_price_condensed = format_number(item_price)

            souls_string += " - Price: {price}".format(price=item_price_condensed)

            souls_string += "\n"

            for soul in souls:
                souls_string += "\n　{soulhaha}".format(soulhaha=soul)

            a.string_representation = souls_string

            final_souls_string += souls_string
            final_souls_string += "\n\n"

            auctions_list.append(a)

    return auctions_list, final_souls_string

def get_requested_auctions(type_soul, num_souls):

    good_auctions = []

    for auction in necro_auctions_all:

        if type_soul == 1:

            if num_souls == auction.num_admin_souls:

                good_auctions.append(auction)

        else:

            if num_souls == auction.num_hypixel_souls_souls:

                good_auctions.append(auction)

    return good_auctions

def join_auction_list(good_auctions):

    good_string = ""

    for auction in good_auctions:

        good_string += "**Dealer: {good_dealer}**\n\n".format(good_dealer = auction.dealer)
        good_string += auction.string_representation + "\n\n"

    return good_string

# ------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.event
async def on_ready():

    print("online!")

# ------------------------------------------------------------------------------------------------------------------------------------------------------

button_admin = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Admin Souls",
        custom_id="button_admin"
)

button_hypixel = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Hypixel Souls",
        custom_id="button_hypixel"
)

button_admin_1 = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="1",
        custom_id="button_admin_1"
)

button_admin_2 = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="2",
        custom_id="button_admin_2"
)

button_admin_3 = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="3",
        custom_id="button_admin_3"
)

button_hypixel_1 = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="1",
        custom_id="button_hypixel_1"
)

button_hypixel_2 = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="2",
        custom_id="button_hypixel_2"
)

button_hypixel_3 = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="3",
        custom_id="button_hypixel_3"
)

row_souls = interactions.ActionRow(
    components=[button_admin, button_hypixel]
)

row_admin_numbers = interactions.ActionRow(
    components=[button_admin_1, button_admin_2, button_admin_3]
)
row_hypixel_numbers = interactions.ActionRow(
    components=[button_hypixel_1, button_hypixel_2, button_hypixel_3]
)

@bot.command(
    name="add_dealer",
    description="add a trusted dealer to ",
    options=[
        interactions.Option(
            name="dealer",
            description="The Minecraft Username of the Trusted Dealer",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def add_dealer(ctx: interactions.CommandContext, dealer: str):

    global dealers

    dealers.append(dealer)

    embed = interactions.Embed(title="Dealer {dealer_name} added!".format(dealer_name=dealer), description="Their name will now show up in searches")

    await ctx.send(embeds=embed)

@bot.command(
    name="add_button",
    description="add a ah button to find auctions",
)

async def create_menu(ctx: interactions.CommandContext):
    embed = interactions.Embed(title="Soul AH Finder", description="What kind of souls do you want?")
    await ctx.send(embeds=[embed], components=row_souls)

@bot.component("button_admin")
async def button_response(ctx):
    embed = interactions.Embed(title="Soul AH Finder", description="How many Admin Souls do you want?")
    await ctx.send(embeds=[embed], components=row_admin_numbers)

@bot.component("button_hypixel")
async def button_response(ctx):
    embed = interactions.Embed(title="Soul AH Finder", description="How many Hypixel Souls do you want?")
    await ctx.send(embeds=[embed], components=row_hypixel_numbers)

@bot.component("button_admin_1")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(1, 1)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str)
    await ctx.send(embeds=[embed])

@bot.component("button_admin_2")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(1, 2)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str)
    await ctx.send(embeds=[embed])

@bot.component("button_admin_3")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(1, 3)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str)
    await ctx.send(embeds=[embed])

@bot.component("button_hypixel_1")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(2, 1)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str)
    await ctx.send(embeds=[embed])

@bot.component("button_hypixel_2")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(2, 2)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str)
    await ctx.send(embeds=[embed])

@bot.component("button_hypixel_3")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(2, 3)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str)
    await ctx.send(embeds=[embed])


# ------------------------------------------------------------------------------------------------------------------------------------------------------

admin_names = ["Rezzus", "AgentKid", "CryptKeeper", "Thorlon", "Plancke",
                               "Hcherndon", "DevSlashNull", "codename_B", "aPunch", "DeprecatedNether", "Jayavarmen",
                               "ZeroErrors", "Zumulus", "Nitroholic", "OrangeMarshall", "ConnorLinfoot",
                               "Externalizable",
                               "Relenter", "Dctr", "Minikloon", "Slikey", "PxlPanda", "Riari", "SteampunkStein",
                               "Xael_Thomas", "NinjaCharlieT", "Don Pireso", "ChiLynn", "PJoke1", "JamieTheGeek",
                               "Fr0z3n",
                               "Luckykessie", "RobityBobity", "mooTV", "Otium", "NoxyD", "BingMo", "Propzie", "Roddan",
                               "Winghide",
                               "BuddhaCat", "Sylent", "LadyBleu", "Cecer", "Bloozing", "Ob111", "Likaos", "skyerzz", "Revengee", "onah"]

@bot.command(
    name="add_admin",
    description="add an admin to the list",
    options = [
        interactions.Option(
            name="admin",
            description="The username of the admin",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def add_admin(ctx: interactions.CommandContext, admin: str):

    admin_names.append(admin)

    embed = interactions.Embed(title="**Admin Added!**", description="The admin {admin_name} was added to the list".format(admin_name=admin))

    await ctx.send(embeds=embed)


@bot.command(
    name="list_admins",
    description="list admins currently in the list of admins",
)
async def list_admins(ctx: interactions.CommandContext):

    admin_str = ""

    for admin in admin_names:

        admin_str += admin + ", "

    admin_str = admin_str[:-2]

    embed = interactions.Embed(title="**The Admins in the list are...**", description=admin_str)

    await ctx.send(embeds=embed)

@bot.command(
    name="necroauctions",
    description="Show the auctions of a user",
    options = [
        interactions.Option(
            name="user",
            description="The name of the user",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def necroauctions(ctx: interactions.CommandContext, user: str):

    embed_loading = interactions.Embed(title="Loading....", description="Please Wait")

    auctions = get_auctions(user)

    if not auctions:

        embed = interactions.Embed(title="This user currently has no necromancy-related auctions",
                                   description="Maybe try again later?", color=0x00ff00)

        await ctx.send(embeds=embed)

        return

    await ctx.send(embeds=embed_loading)

    necro_auctions, final_souls_string = convert_to_dataclass(auctions)

    if(necro_auctions):

        final_embed = interactions.Embed(title="**Necromancy-Related Auctions of {userthingy}:**"
                                             .format(userthingy=user), description=final_souls_string)

        await ctx.send(embeds=final_embed)

    else:

        embed = interactions.Embed(title="This user currently has no necromancy-related auctions",
                                       description="Maybe try again later?", color=0x00ff00)

        await ctx.send(embeds=embed)

# ----------------------------------------------------------------------------------------------------

@bot.command(
    name="manacostcalculator",
    description="Calculates the mana cost given HP and Damage",
    options = [
        interactions.Option(
            name="hp",
            description="The amount of HP your desired mob has",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="damage",
            description="The amount of damage your desired mob has",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def manacostcalculator(ctx: interactions.CommandContext, hp : str, damage: str):

    if(hp.endswith('m')):

        hp = int(hp[:-1]) * 1000000

    elif (hp.endswith('k')):

        hp = int(hp[:-1]) * 1000

    if (damage.endswith('m')):

        damage = int(damage[:-1]) * 1000000

    elif (damage.endswith('k')):

        damage = int(damage[:-1]) * 1000

    manacost = damage/50 + hp/100000

    manacostmin = manacost * 0.268

    embed = interactions.Embed(title="**Mana Cost Calculation**",
                               description="**Summon Stats**:\n\n　**HP**: {health}\n\n　**Damage**: {dmg}\n\n\n**Mana Cost**:\n\n　**Raw Mana Cost**: {mana}\n\n　**With Max Reduction**: {manamin}"
                               .format(health=hp, dmg=damage, mana=manacost, manamin=manacostmin))

    await ctx.send(embeds=[embed])

    common_costs_embed = interactions.Embed(title="**Common Mana Costs**", description="**Admin Soul** (15m HP 225k Damage):\n\n　**Raw Mana Cost**: 4650.0\n\n　**With Max Reduction**: 1246.2\n\n\n**Hypixel** (75m HP 750k DMG)\n\n　**Raw Mana Cost**: 15750.0\n\n　**With Max Reduction**: 4221.0")

    await ctx.send(embeds=[common_costs_embed])

# ------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.command(
    name="emojiblocker",
    description="Toggles the emoji blocker",
)
async def emojiblocker(ctx: interactions.CommandContext):

    global emojiblockerbool

    if emojiblockerbool:

        emojiblockerbool = False;

    else:

        emojiblockerbool = True;

    if emojiblockerbool:
        embed = interactions.Embed(title="**Emoji Blocker Turned On**", description="no more cringe")
        await ctx.send(embeds=[embed])
    else:
        embed = interactions.Embed(title="**Emoji Blocker Turned Off**", description="cringe")
        await ctx.send(embeds=[embed])

# ------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.event(name="on_message_create")
async def on_message_create(message: interactions.Message):

    blacklisted = ["bob"]

    if emojiblockerbool:

        for word in blacklisted:

            if word in message.content:

                await message.delete()


bot.start()