import nbt
import io
import base64
import interactions
import requests
import json
from interactions.ext.tasks import IntervalTrigger, create_task
from dataclasses import dataclass
import re
import os

bot = interactions.Client(token=token=os.environ.get("TOKEN"),
                          intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)


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
        print(tag.pretty_tree())

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

    auctions = get_auctions(user)
    dealer, nbt_list, price = get_info(auctions)

    nbt_data, names = convert_nbt(nbt_list)

    final_str = ""

    for i in range(len(nbt_data)):

        item_str = "**" + names[i] + "**" + "\n\n"

        for soul in nbt_data[i]:

            item_str += "\t" + soul + " \n"

        final_str += item_str + "\n\n"


    embed = interactions.Embed(title="Necromancy-related auctions of {userguy}".format(userguy=dealer), description=final_str)

    await ctx.send(embeds=[embed])


bot.start()
