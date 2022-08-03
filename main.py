import nbt
import io
import base64
import interactions
import requests
import BotComponents
import json
from interactions.ext.tasks import IntervalTrigger, create_task
from dataclasses import dataclass
import re
import os

bot = interactions.Client(token=os.environ.get("TOKEN"),
                          intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

admin_names = ["Rezzus", "AgentKid", "CryptKeeper", "Thorlon", "Plancke",
               "Hcherndon", "DevSlashNull", "codename_B", "aPunch", "DeprecatedNether", "Jayavarmen",
               "ZeroErrors", "Zumulus", "Nitroholic", "OrangeMarshall", "ConnorLinfoot",
               "Externalizable",
               "Relenter", "Dctr", "Minikloon", "Slikey", "PxlPanda", "Riari", "SteampunkStein",
               "Xael_Thomas", "NinjaCharlieT", "Don Pireso", "ChiLynn", "PJoke1", "JamieTheGeek",
               "Fr0z3n",
               "Luckykessie", "RobityBobity", "mooTV", "Otium", "NoxyD", "BingMo", "Propzie", "Roddan",
               "Winghide",
               "BuddhaCat", "Sylent", "LadyBleu", "Cecer", "Bloozing", "Ob111", "Likaos", "skyerzz", "Revengee",
               "onah", "inventivetalent", "xHascox", "sfarnham", "Bembo", "_PolynaLove_", "Pensul", "TorWolf",
               "Taytale", "Nausicaah", "flameboy101", "Teddy", "Judg3", "Citria", "Magicboys", "RapidTheNerd", "Cham",
               "vinny8ball", "Cheesey", "Dueces", "_fudgiethewhale", "DEADORKAI", "BlocksKey", "Plummel",
               "DistrictGecko",
               "AdamWho", "carstairs95", "MistressEldrid"]

auctions_list = []
dealer = ""

@dataclass()
class Auction:

    price: int

    contains_admin_souls: bool
    contains_hypixel_souls: bool
    contains_other_souls: bool

    auction_string: str

    def __lt__(self, other):
        return self.price < other.price

def int_to_Roman(num):

    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

def get_auctions(user: str):
    uuid_url = "https://api.mojang.com/users/profiles/minecraft/{username}".format(username=user)

    response = requests.get(uuid_url)

    uuid = response.json().get("id")

    auctions_url = "https://api.hypixel.net/skyblock/auction?key=" + os.environ.get("API_KEY") + "&player={thing_uuid}".format(
        thing_uuid=uuid)

    auctions_response = requests.get(auctions_url)

    auctions = auctions_response.json().get("auctions")

    return auctions


def get_info(auctions):
    keywords = ["eaper", "ummoning", "ecromancer"]

    nbt_list = []
    price = []

    dealer = ""

    if (auctions):

        for auction in auctions:

            for keyword in keywords:

                if keyword in auction.get("item_name"):
                    username_url = "https://api.mojang.com/user/profiles/{uuid}/names".format(
                        uuid=auction.get("auctioneer"))

                    response = requests.get(username_url)

                    # for key in response.json()[-1]:
                    #
                    #     print(key)

                    username = (response.json()[-1]).get("name")

                    dealer = username
                    nbt_list.append(auction.get("item_bytes").get("data"))
                    price.append(auction.get("starting_bid"))

    return dealer, nbt_list, price

def format_str(tag_string):

    string_thing = str(tag_string)

    string_thing = string_thing.replace("§6", "")
    string_thing = string_thing.replace("§d", "")
    str_list = string_thing.split("_")

    str_str = ""

    for word in str_list:

        ind = word.find(" ")

        if ind != -1:

            split_word = word.split(" ")

            for split in split_word:

                str_str += split.capitalize() + " "

        else:

            word = word.capitalize()

            str_str += word + " "

    return str_str

def convert_nbt(nbt_list):

    item_list = []
    names = []

    for soul in nbt_list:

        data = nbt.nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(soul)))

        list = data[0]

        compound = list[0]

        tag = compound[2]

        display = tag[3]

        name = display[1]

        ex = tag["ExtraAttributes"]

        souls_nbt = ex["necromancer_souls"]

        rune = ""

        enchantments_list = []

        hpb_count = 0

        recomb = 0

        if "rarity_upgrades" in ex:
            recomb = ex["rarity_upgrades"]

        if "hot_potato_count" in ex:
            hpb_count = ex["hot_potato_count"]

        if "enchantments" in ex:
            enchantments = ex["enchantments"]

            important_enchants = ["ultimate_wise", "ultimate_one_for_all"]

            for enchant in important_enchants:

                if enchant in enchantments:

                    if(enchant == "ultimate_wise"):
                        enchantments_list.append("Ultimate Wise " + str(enchantments["ultimate_wise"]))

                    elif(enchant == "ultimate_one_for_all"):
                        enchantments_list.append("One For All " + str(enchantments["ultimate_one_for_all"]))

        if "runes" in ex:

            runes = ex['runes']

            if "BLOOD" in runes:

                rune = "Blood Rune " + str(runes[0]) + " "

            if "SNOW" in runes:

                rune = "Snow Rune " + str(runes[0]) + " "

            if "HEARTS" in runes:

                rune = "Hearts Rune " + str(runes[0]) + " "

            if "LIGHTNING" in runes:

                rune = "Lightning Rune " + str(runes[0]) + " "

            if "PESTILENCE" in runes:

                rune = "Pestilence Rune " + str(runes[0]) + " "

            if "SPIRIT" in runes:

                rune = "Spirit Rune " + str(runes[0]) + " "

            if "MUSIC" in runes:

                rune = "Music Rune " + str(runes[0]) + " "

        reaperstring = "<a:scythe:998672774866419746>"
        necroswordstring = "<:necromsword:998672747813159022>"
        summoningringstring = "<a:summring:998672806378213408>"
        hpbstring = "<a:hpb:998672720906682398>"
        recombstring = "<a:recomb:998672693719224361>"

        formatted_name = format_str(name)
        final_name_str = ""

        if "Reaper" in formatted_name:

            final_name_str += reaperstring + " "

        elif "Necromancer" in formatted_name:

            final_name_str += necroswordstring + " "

        elif "Summoning" in formatted_name:

            final_name_str += summoningringstring + " "

        final_name_str += formatted_name

        if (hpb_count != 0):
            final_name_str += str(hpb_count) + hpbstring + " "

        if(recomb == 1):
            final_name_str += recombstring + " "

        if(enchantments_list):

            for important_enchants in enchantments_list:

                final_name_str += important_enchants + " "

        final_name_str += rune

        names.append(final_name_str)

        # print(len(tag))
        # print(tag.pretty_tree())

        souls = []

        for soul in souls_nbt:

            soul_id = soul[0]

            formatted_soul = format_str(soul_id).replace("Master Crypt Undead", "(MM)")[:-3]

            souls.append(formatted_soul)

        item_list.append(souls)

    return item_list, names

@bot.command(
   name="necroauctions",
   description="Show the auctions of a user",
   options=[
      interactions.Option(
         name="user",
         description="The name of the user",
         type=interactions.OptionType.STRING,
         required=True,
      ),
   ],
)
async def necroauctions(ctx: interactions.CommandContext, user: str):

    embed = interactions.Embed(title="Loading....", description="Please Wait")

    await ctx.send(embeds=[embed], ephemeral=True)

    global dealer
    global auctions_list

    auctions = get_auctions(user)
    dealer, nbt_list, price = get_info(auctions)

    nbt_data, names = convert_nbt(nbt_list)

    final_str = ""

    auctions_list_temp = []

    for i in range(len(nbt_data)):

        item_str = "**" + names[i] + "**" + "\n\n"

        temp_auction = Auction(price[i], False, False, False, "")

        for soul in nbt_data[i]:

            for admin in admin_names:

                if admin in soul:

                    temp_auction.contains_admin_souls = True

            if "Hypixel" in soul:

                temp_auction.contains_hypixel_souls = True


            item_str += "\t" + soul + " \n"

        if temp_auction.contains_hypixel_souls == False and temp_auction.contains_admin_souls == False:

            temp_auction.contains_other_souls = True

        temp_auction.auction_string = item_str + "\n\n"

        auctions_list_temp.append(temp_auction)

    auctions_list = auctions_list_temp

    for temp_auction in auctions_list:

        final_str += temp_auction.auction_string

    embed = interactions.Embed(title="Necromancy-related auctions of {userguy}".format(userguy=dealer), description=final_str)

    await ctx.send(embeds=[embed], components=[BotComponents.menu_row, BotComponents.pages_row])

@bot.component("sort_menu")
async def menu_response(ctx: interactions.CommandContext, options: list[str]):

    for option in options:

        if(option == "price_l"):

            auctions_list.sort()

            final_str = ""

            for temp_auction in auctions_list:
                final_str += temp_auction.auction_string

            embed = interactions.Embed(title="Necromancy-related auctions of {userguy} - LBIN to HBIN".format(userguy=dealer),
                                       description=final_str)

            await ctx.edit(embeds=[embed], components=[BotComponents.menu_row, BotComponents.pages_row])

        elif (option == "price_h"):

            auctions_list.sort(reverse=True)

            final_str = ""

            for temp_auction in auctions_list:
                final_str += temp_auction.auction_string

            embed = interactions.Embed(title="Necromancy-related auctions of {userguy} - HBIN to LBIN".format(userguy=dealer),
                                       description=final_str)

            await ctx.edit(embeds=[embed], components=[BotComponents.menu_row, BotComponents.pages_row])

        elif (option == "admin"):

            admin_auctions = []

            for auction in auctions_list:

                if auction.contains_admin_souls:

                    admin_auctions.append(auction)

            final_str = ""

            for temp_auction in admin_auctions:

                final_str += temp_auction.auction_string

            embed = interactions.Embed(title="Necromancy-related auctions of {userguy} with Admin Souls".format(userguy=dealer),
                                       description=final_str)

            await ctx.edit(embeds=[embed], components=[BotComponents.menu_row, BotComponents.pages_row])

        elif (option == "hypixel"):

            hypixel_auctions = []

            for auction in auctions_list:

                if auction.contains_hypixel_souls:
                    hypixel_auctions.append(auction)

            final_str = ""

            for temp_auction in hypixel_auctions:
                final_str += temp_auction.auction_string

            embed = interactions.Embed(title="Necromancy-related auctions of {userguy} with Hypixel Souls".format(userguy=dealer),
                                       description=final_str)

            await ctx.edit(embeds=[embed], components=[BotComponents.menu_row, BotComponents.pages_row])

        elif (option == "other"):

            other_auctions = []

            for auction in auctions_list:

                if auction.contains_hypixel_souls:
                    other_auctions.append(auction)

            final_str = ""

            for temp_auction in other_auctions:

                final_str += temp_auction.auction_string

            embed = interactions.Embed(title="Necromancy-related auctions of {userguy} with Other Souls".format(userguy=dealer),
                                       description=final_str)

            await ctx.edit(embeds=[embed], components=[BotComponents.menu_row, BotComponents.pages_row])

        else:

            embed = interactions.Embed(title="FAILED",
                                       description="Failed, please contact Literally 1984#1984 to report this bug")

            await ctx.send(embeds=[embed])

@bot.component("arrow_prev")
async def button_response(ctx: interactions.CommandContext):
    await ctx.edit("balls")

@bot.component("arrow_next")
async def menu_response(ctx: interactions.CommandContext):
    await ctx.edit("balls 2")



bot.start()
