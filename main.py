import interactions
import requests
import json
from interactions.ext.tasks import IntervalTrigger, create_task
from dataclasses import dataclass
import re
import os

bot = interactions.Client(token=os.environ.get("TOKEN"),
                          intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

emojiblockerbool = False

necro_auctions_all = []

blacklisted = []

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
    price: int
    type: int
    num_admin_souls: int
    num_hypixel_souls: int
    num_tank_souls: int
    string_representation: str
      
    def __lt__(self, other):
        
      return self.price < other.price
 

trusted_dealers = ["FearedIce"]

def get_auctions(user: str):

    uuid_url = "https://api.mojang.com/users/profiles/minecraft/{username}".format(username=user)

    response = requests.get(uuid_url)

    uuid = response.json().get("id")

    auctions_url = "https://api.hypixel.net/skyblock/auction?key=" + os.environ.get("API_KEY") + "&player={thing_uuid}".format(
        thing_uuid=uuid)

    auctions_response = requests.get(auctions_url)

    auctions = auctions_response.json().get("auctions")

    return auctions

def convert_to_dataclass(auctions):

    keywords = ["eaper", "ummoning", "ecromancer"]

    dealers = []
    necroauctions = []
    lore = []
    price = []

    if (auctions):

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

            a = Auction("", "", "", 0, 0, 0, 0, "")

            item_name = necroauctions[i]
            item_lore = lore[i]
            item_price = price[i]

            souls = []

            if "hypixel" in item_lore:

                for i in range(item_lore.count("hypixel")):

                    souls.append("hypixel")

                    a.num_hypixel_souls += 1

            for admin_name in admin_names:

                if admin_name in item_lore:

                    for i in range(item_lore.count(admin_name)):
                      
                        souls.append(admin_name)
                        
                        a.num_admin_souls += 1
                        
            if "Tank" in item_lore:

                for i in range(item_lore.count("Tank")):

                    souls.append("Tank Zombie")

                    a.num_tank_souls += 1
                        
            a.dealer = dealers[i]
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

            auctions_list.append(a)
    
    auctions_list.sort()
    
    for temp_auction in auctions_list:
    
        final_souls_string += temp_auction.string_representation
        final_souls_string += "\n\n"

    return auctions_list, final_souls_string

def get_requested_auctions(type_soul, num_souls):

    good_auctions = []

    for auction in necro_auctions_all:

        if type_soul == 1:

            if num_souls == auction.num_admin_souls:

                good_auctions.append(auction)

        elif type_soul == 2:

            if num_souls == auction.num_hypixel_souls:

                good_auctions.append(auction)
        else:

            if num_souls == 1:
              
                if 1 <= auction.num_tank_souls and auction.num_tank_souls <= 3:
                
                    good_auctions.append(auction)
            
            elif num_souls == 2:
              
                if 4 <= auction.num_tank_souls and auction.num_tank_souls <= 6:
                
                    good_auctions.append(auction)
            
            elif num_souls == 3:
              
                if 7 <= auction.num_tank_souls and auction.num_tank_souls <= 8:
                
                    good_auctions.append(auction)
            
    
    good_auctions.sort()

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

button_tank = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Tank Souls",
        custom_id="button_tank"
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

button_tank_1 = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="1-3",
        custom_id="button_tank_1"
)

button_tank_2 = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="4-6",
        custom_id="button_tank_2"
)

button_tank_3 = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="6-8",
        custom_id="button_tank_3"
)

row_souls = interactions.ActionRow(
    components=[button_admin, button_hypixel, button_tank]
)

row_admin_numbers = interactions.ActionRow(
    components=[button_admin_1, button_admin_2, button_admin_3]
)
row_hypixel_numbers = interactions.ActionRow(
    components=[button_hypixel_1, button_hypixel_2, button_hypixel_3]
)
row_tank_numbers = interactions.ActionRow(
    components=[button_tank_1, button_tank_2, button_tank_3]
)

@bot.command(
    name="add_dealer",
    description="add a trusted dealer to the list",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
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

    embed = interactions.Embed(title="Dealer {dealer_name} added!".format(dealer_name=dealer), description="Their name will now show up in searches", color=0x911ef5)

    await ctx.send(embeds=embed)

@bot.command(
    name="find_auactions",
    description="Find auctions that match specified requirements",
)

async def create_menu(ctx: interactions.CommandContext):
    embed = interactions.Embed(title="Soul AH Finder", description="What kind of souls do you want?", color=0x911ef5)
    await ctx.send(embeds=[embed], components=row_souls, ephemeral=True)

@bot.component("button_admin")
async def button_response(ctx):
    embed = interactions.Embed(title="Soul AH Finder", description="How many Admin Souls do you want?", color=0x911ef5)
    await ctx.send(embeds=[embed], components=row_admin_numbers, ephemeral=True)

@bot.component("button_hypixel")
async def button_response(ctx):
    embed = interactions.Embed(title="Soul AH Finder", description="How many Hypixel Souls do you want?", color=0x911ef5)
    await ctx.send(embeds=[embed], components=row_hypixel_numbers, ephemeral=True)

@bot.component("button_tank")
async def button_response(ctx):
    embed = interactions.Embed(title="Soul AH Finder", description="How many Tank Souls do you want?", color=0x911ef5)
    await ctx.send(embeds=[embed], components=row_tank_numbers, ephemeral=True)

@bot.component("button_admin_1")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(1, 1)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str, color=0x911ef5)
    await ctx.send(embeds=[embed], ephemeral=True)

@bot.component("button_admin_2")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(1, 2)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str, color=0x911ef5)
    await ctx.send(embeds=[embed], ephemeral=True)

@bot.component("button_admin_3")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(1, 3)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str, color=0x911ef5)
    await ctx.send(embeds=[embed], ephemeral=True)

@bot.component("button_hypixel_1")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(2, 1)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str, color=0x911ef5)
    await ctx.send(embeds=[embed], ephemeral=True)

@bot.component("button_hypixel_2")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(2, 2)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str, color=0x911ef5)
    await ctx.send(embeds=[embed], ephemeral=True)

@bot.component("button_hypixel_3")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(2, 3)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str, color=0x911ef5)
    await ctx.send(embeds=[embed], ephemeral=True)

@bot.component("button_tank_1")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(3, 1)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str, color=0x911ef5)
    await ctx.send(embeds=[embed], ephemeral=True)

@bot.component("button_tank_2")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(3, 2)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str, color=0x911ef5)
    await ctx.send(embeds=[embed], ephemeral=True)

@bot.component("button_tank_3")
async def button_response(ctx):
    requested_auctions = get_requested_auctions(3, 3)
    requested_str = join_auction_list(requested_auctions)
    embed = interactions.Embed(title="**Matching Auctions**", description=requested_str, color=0x911ef5)
    await ctx.send(embeds=[embed], ephemeral=True)


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
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
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

    embed = interactions.Embed(title="**Admin Added!**", description="The admin {admin_name} was added to the list".format(admin_name=admin), color=0x911ef5)

    await ctx.send(embeds=[embed], ephemeral=True)


@bot.command(
    name="list_admins",
    description="list admins currently in the list of admins",
)
async def list_admins(ctx: interactions.CommandContext):

    admin_str = ""

    for admin in admin_names:

        admin_str += admin + ", "

    admin_str = admin_str[:-2]

    embed = interactions.Embed(title="**The Admins in the list are...**", description=admin_str, color=0x911ef5)

    await ctx.send(embeds=[embed], ephemeral=True)

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

    embed_loading = interactions.Embed(title="Loading....", description="Please Wait", color=0x911ef5,)

    auctions = get_auctions(user)

    if not auctions:

        embed = interactions.Embed(title="This user currently has no necromancy-related auctions",
                                   description="Maybe try again later?", color=0x911ef5)

        await ctx.send(embeds=embed, ephemeral=True)

        return

    await ctx.send(embeds=embed_loading, ephemeral=True)

    necro_auctions, final_souls_string = convert_to_dataclass(auctions)

    if(necro_auctions):

        final_embed = interactions.Embed(title="**Necromancy-Related Auctions of {userthingy}:**"
                                             .format(userthingy=user), description=final_souls_string, color=0x911ef5,)

        await ctx.send(embeds=final_embed, ephemeral=True)

    else:

        embed = interactions.Embed(title="This user currently has no necromancy-related auctions",
                                       description="Maybe try again later?", color=0x911ef5)

        await ctx.send(embeds=embed, ephemeral=True)

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
                               .format(health=hp, dmg=damage, mana=manacost, manamin=manacostmin), color=0x911ef5)

    await ctx.send(embeds=[embed])

    common_costs_embed = interactions.Embed(title="**Common Mana Costs**", description="**Admin Soul** (15m HP 225k Damage):\n\n　**Raw Mana Cost**: 4650.0\n\n　**With Max Reduction**: 1246.2\n\n\n**Hypixel** (75m HP 750k DMG)\n\n　**Raw Mana Cost**: 15750.0\n\n　**With Max Reduction**: 4221.0", color=0x911ef5)

    await ctx.send(embeds=[common_costs_embed])

# ------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.command(
    name="add_blacklisted_word",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    description="Add a blacklisted word to the index",
    options = [
        interactions.Option(
            name="word",
            description="The word you want to add",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def add_blacklisted_word(ctx: interactions.CommandContext, word : str):

    blacklisted.append(word)

    embed = interactions.Embed(title="{word_thing} added to the blacklist!".format(word_thing=word), description="Toggle the blacklist by using /toggleable_blacklist", color=0x911ef5)

    await ctx.send(embeds=[embed], ephemeral=True)

@bot.command(
    name="toggleable_blacklist",
    description="Toggles the blacklist for words",
)
async def emojiblocker(ctx: interactions.CommandContext):

    global emojiblockerbool

    if emojiblockerbool:

        emojiblockerbool = False;

    else:

        emojiblockerbool = True;

    if emojiblockerbool:
        embed = interactions.Embed(title="**Blacklist Turned On**", description="no more cringe", color=0x911ef5)
        await ctx.send(embeds=[embed], ephemeral=True)
    else:
        embed = interactions.Embed(title="**Blacklist Turned Off**", description="cringe", color=0x911ef5)
        await ctx.send(embeds=[embed], ephemeral=True)

# -----------------------------------------------------------------------------------------------------------------------------------------------------

# @bot.event(name="on_message_create")
# async def on_message_create(message: interactions.Message):

#     if emojiblockerbool:

#         if blacklisted:

#             for word in blacklisted:

#                 if word in message.content:

#                     await message.delete()

# ------------------------------------------------------------------------------------------------------------------------------------------------------

button_souls = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Souls",
        custom_id="button_souls"
)

button_mana_cost = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Mana Cost",
        custom_id="button_mana_cost"
)

button_slayer_guides = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Slayer Guides",
        custom_id="button_guides"
)

button_more_soul = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="More Soul Info",
        custom_id="button_more_soul"
)

row_faq = interactions.ActionRow(
    components=[button_souls, button_mana_cost, button_slayer_guides, button_more_soul]
)

@bot.command(
    name="faq",
    description="Frequently Asked Questions",
)
async def faq(ctx: interactions.CommandContext):

    embed = interactions.Embed(title="Faq", description="Please select a section to learn more about\n\nIf you still have any questions, feel free to ask them in #questions-and-advice!", color=0x911ef5)

    await ctx.send(embeds=[embed], components=row_faq)

@bot.component("button_souls")
async def button_response(ctx):

    soul_str_1 = "**How do I know if a Soul is from Mastermode or not?**\n\n Download the #soul-checker-mod by installing forge for 1.8.9 (https://files.minecraftforge.net/net/minecraftforge/forge/index_1.8.9.html) and putting the mod into your mods folder in .minecraft.\n"
    soul_str_2 = "If you start Minecraft, any Mastermode Souls will have a blue text saying MASTERMODE SOUL behind them. Their respective item in the auction house will also have colored background:\n"
    soul_str_3 = "Green: The weapon has only Mastermode Souls\n"
    soul_str_4 = "Orange: The weapon has at least one not Mastermode Soul\n\n\n"

    soul_str_5 = "**How are souls obtained?**\n\n"
    soul_str_6 = "The basic principle behind souls is that depending on the level of their respective mob, they have a chance to drop their soul if you either kill them with a necromancer weapon (Reaper Scythe/Necromancer Sword) or have a Summoning Ring in your inventory.\n"
    soul_str_7 = "Those souls can then be picked up with the item.\n Both Admin Souls and Hypixel Soul are obtained from a rare (around 1% spawnrate) room in M1.\n Tank Zombies are always from M3."

    final_soul_faq_str = soul_str_1 + soul_str_2 + soul_str_3 + soul_str_4 + soul_str_5 + soul_str_6 + soul_str_7

    embed = interactions.Embed(title="Soul Guides", description=final_soul_faq_str, color=0x911ef5)
    await ctx.send(embeds=[embed])

@bot.component("button_mana_cost")
async def button_response(ctx):

    soul_str_1 = "**How do I calculate mana cost and what does max reduction mean?**\n\n Mana cost can easily be calculated with the formula: Damage / 50 + Health / 100,000 The bot in mana-cost-check will do this for you.\n"
    soul_str_2 = "Max reduction is achieved by having\n1. Ultimate Wise 5 on your Necromancer Weapon, which grants a 50% reduction of mana cost (This is why a Summoning Ring should not be used to summon souls as it can not be enchanted with Ultimate Wise 5)\n"
    soul_str_3 = "2. Wise Dragon Armor's full set bonus makes all your abilities cost .67 of its original cost, so you use 33% less mana.\n"
    soul_str_4 = "3. Lastly the Epic and Legendary Sheep pet reduces the cost of your abilities by 20% at level 100.\n"
    soul_str_5 = "This gives a formula of mana cost x 0.5 x 0.66 x 0.8 or mana cost x 0.26.\nMAKE SURE YOU HAVE THESE THINGS OTHERWISE SPAWNING YOUR SOUL WILL BE EXPONENTIONELLY MORE EXPENSIVE\n\n\n"


    soul_str_6 = "**How do I spawn my soul?**\n\n In the Mana and Summoning Guides category are multiple guides on general mana knowledge as well as how to summon 1.\n1 Admin soul #summoning-1-admin\n2. 2 Admin souls #summoning-2–admins \n3. Hypixel #summoning-hypixel\n4. Tank Zombies #summoning-tanks\n\n"
    soul_str_7 = "There is usually a cheap method, which is harder to pull off and a easier, but more expensive method."

    final_soul_faq_str = soul_str_1 + soul_str_2 + soul_str_3 + soul_str_4 + soul_str_5 + soul_str_6 + soul_str_7

    embed = interactions.Embed(title="Mana Cost Guides", description=final_soul_faq_str, color=0x911ef5)
    await ctx.send(embeds=[embed])

@bot.component("button_guides")
async def button_response(ctx):

    soul_str_1 = "**Which soul do I get?**\n\n 1 Admin is good enough for all Slayer Bosses besides Revenant T5 and Voidgloom T3+\n2 Admins can do all Slayer bosses besides Revenant T5 and Voidgloom T4\n1 Hypixel can do all Slayer bosses besides Voidgloom T4\n1 M6 Giant/Golem can do ALL slayer bosses. He shreds through them\nUsing souls or for Blaze Slayer T2+ is not recommended as it has max health damage which kills them fast"

    soul_str_2 = "\n\n\n**How do I avoid dying to voidgloom while AFKing using Admins?**\n\nYou need:\n1. Goblin Armor\n2. Wither Cloak sword and any item with UW5 on it\n3. A god potion\nIf you get hit you loose 10% max mana with wither cloak on (20%*0.5) which is 10, as your max mana is 100. Your base mana regen is 2 and god pot adds 8. So you regen 10mana/s and loose 1 per hit. This allows you to basically never take damage, unless there is enough Nukebi Heads to deal damage to you more than once per second."


    final_soul_faq_str = soul_str_1 + soul_str_2

    embed = interactions.Embed(title="Slayer Guides", description=final_soul_faq_str, color=0x911ef5)
    await ctx.send(embeds=[embed])

@bot.component("button_more_soul")
async def button_response(ctx):

    soul_str_1 = "**Should I use Souls in Dungeons?**\n\nNo, they die extremely fast as there is a lot of max health damage in dungeons like lava or (mini-)bosses."
    soul_str_2 = "\n\n**What happens if my Soul dies?**\n\nIf it dies, the soul will be removed from your sword and you'll need to get a new one."
    soul_str_3 = "\n\n**How do I regenerate my Soul?**\n\nOnly possible way is to despawning them and then resummon."
    soul_str_4 = "\n\n**How do the Necromancer Tools work?**\n\n**If you kill a mob with a Necromancer Sword/Reaper Scythe or while having a Summoning Ring in your inventory it has a chance to drop a soul depending on its levels which can be picked up. Any soul that was stored in them can be summoned for an according mana cost. You cannot transfer souls, deleting them works by Shift + RIght Click and then clicking the soul you wish to remove."

    final_soul_faq_str = soul_str_1 + soul_str_2 + soul_str_3 + soul_str_4

    embed = interactions.Embed(title="Slayer Guides", description=final_soul_faq_str, color=0x911ef5)
    await ctx.send(embeds=[embed])

bot.start()
