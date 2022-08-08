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

admin_names = ["Rezzus", "Agentkid", "Cryptkeeper", "Thorlon", "Plancke",
               "Hcherndon", "Devslashnull", "Codename B", "Apunch", "Deprecatednether", "Jayavarmen",
               "Zeroerrors", "Zumulus", "Nitroholic", "Orangemarshall", "Connorlinfoot",
               "Externalizable",
               "Relenter", "Dctr", "Minikloon", "Slikey", "Pxlpanda", "Riari", "Steampunkstein",
               "Xael_thomas", "Ninjacharliet", "Don pireso", "Chilynn", "Pjoke1", "Jamiethegeek",
               "Fr0z3n",
               "Luckykessie", "Robitybobity", "Mootv", "Otium", "Noxyd", "Bingmo", "Propzie", "Roddan",
               "Winghide",
               "Buddhacat", "Sylent", "Ladybleu", "Cecer", "Bloozing", "Ob111", "Likaos", "skyerzz", "Revengee",
               "onah", "inventivetalent", "Xhascox", "sfarnham", "Bembo", " polynalove ", "Pensul", "Torwolf",
               "Taytale", "Nausicaah", "Flameboy101", "Teddy", "Judg3", "Citria", "Magicboys", "Rapidthenerd", "Cham",
               "vinny8ball", "Cheesey", "Dueces", " fudgiethewhale", "Deadorkai", "BlocksKey", "Plummel",
               "Districtgecko",
               "Adamwho", "carstairs95", "Mistresseldrid"]

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

def safe_num(num):
   if isinstance(num, str):
      num = float(num)
   return float('{:.3g}'.format(abs(num)))

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
 
def format_number(num):
   num = safe_num(num)
   sign = ''

   metric = {'T': 1000000000000, 'B': 1000000000, 'M': 1000000, 'K': 1000, '': 1}

   for index in metric:
      num_check = num / metric[index]

      if (num_check >= 1):
         num = num_check
         sign = index
         break

   return f"{str(num).rstrip('0').rstrip('.')}{sign}"


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

        item_str = "**" + names[i] + "**" + " - " + str(format_number(price[i])) + "\n\n"

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

    await ctx.send(embeds=[embed], components=[BotComponents.price_menu_row, BotComponents.souls_menu_row, BotComponents.pages_row])

@bot.component("sort_price_menu")
async def menu_response(ctx: interactions.CommandContext, options: list[str]):

    for option in options:

        if(option == "price_l"):

            auctions_list.sort()

            final_str = ""

            for temp_auction in auctions_list:
                final_str += temp_auction.auction_string

            embed = interactions.Embed(title="Necromancy-related auctions of {userguy} - LBIN to HBIN".format(userguy=dealer),
                                       description=final_str)

            await ctx.edit(embeds=[embed], components=[BotComponents.price_menu_row, BotComponents.souls_menu_row, BotComponents.pages_row])

        elif (option == "price_h"):

            auctions_list.sort(reverse=True)

            final_str = ""

            for temp_auction in auctions_list:
                final_str += temp_auction.auction_string

            embed = interactions.Embed(title="Necromancy-related auctions of {userguy} - HBIN to LBIN".format(userguy=dealer),
                                       description=final_str)

            await ctx.edit(embeds=[embed], components=[BotComponents.price_menu_row, BotComponents.souls_menu_row, BotComponents.pages_row])

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

            await ctx.edit(embeds=[embed], components=[BotComponents.price_menu_row, BotComponents.souls_menu_row, BotComponents.pages_row])

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

            await ctx.edit(embeds=[embed], components=[BotComponents.price_menu_row, BotComponents.souls_menu_row, BotComponents.pages_row])

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

            await ctx.edit(embeds=[embed], components=[BotComponents.price_menu_row, BotComponents.souls_menu_row, BotComponents.pages_row])

        else:

            embed = interactions.Embed(title="FAILED",
                                       description="Failed, please contact Literally 1984#1984 to report this bug")

            await ctx.send(embeds=[embed])

@bot.component("sort_souls_menu")
async def menu_response(ctx: interactions.CommandContext, options: list[str]):

    for option in options:

        if(option == "price_l"):

            auctions_list.sort()

            final_str = ""

            for temp_auction in auctions_list:
                final_str += temp_auction.auction_string

            embed = interactions.Embed(title="Necromancy-related auctions of {userguy} - LBIN to HBIN".format(userguy=dealer),
                                       description=final_str)

            await ctx.edit(embeds=[embed], components=[BotComponents.price_menu_row, BotComponents.souls_menu_row, BotComponents.pages_row])

        elif (option == "price_h"):

            auctions_list.sort(reverse=True)

            final_str = ""

            for temp_auction in auctions_list:
                final_str += temp_auction.auction_string

            embed = interactions.Embed(title="Necromancy-related auctions of {userguy} - HBIN to LBIN".format(userguy=dealer),
                                       description=final_str)

            await ctx.edit(embeds=[embed], components=[BotComponents.price_menu_row, BotComponents.souls_menu_row, BotComponents.pages_row])

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

            await ctx.edit(embeds=[embed], components=[BotComponents.price_menu_row, BotComponents.souls_menu_row, BotComponents.pages_row])

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

            await ctx.edit(embeds=[embed], components=[BotComponents.price_menu_row, BotComponents.souls_menu_row, BotComponents.pages_row])

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

            await ctx.edit(embeds=[embed], components=[BotComponents.price_menu_row, BotComponents.souls_menu_row, BotComponents.pages_row])

        else:

            embed = interactions.Embed(title="FAILED",
                                       description="Failed, please contact Literally 1984#1984 to report this bug")

            await ctx.send(embeds=[embed])

@bot.event(name="on_message_create")
async def on_message_create(message: interactions.Message):
  
    if "hp" in message.content and "dmg" in message.content:
      
        hp = ""
        damage = ""
        split_str = message.content.split(" ")
        
        hp = split_str[0]
        damage = split_str[2]
      
        if (hp.endswith('m')):

          hp_int = int(hp[:-1]) * 1000000

        elif (hp.endswith('k')):

          hp_int = int(hp[:-1]) * 1000

        elif hp.endswith('b'):

          hp_int = int(hp[:-1]) * 1000000000

        else:

          hp_int = int(hp)

        if (damage.endswith('m')):

          damage_int = int(damage[:-1]) * 1000000

        elif (damage.endswith('k')):

          damage_int = int(damage[:-1]) * 1000

        elif damage.endswith('b'):

          damage_int = int(damage[-1]) * 1000000000
        
        else:
         
          damage_int = int(damage)

        manacost = damage_int / 50 + hp_int / 100000

        manacostmin = manacost * 0.268 

        embed = interactions.Embed(title="**Mana Cost Calculation**",
                                  description="**Summon Stats**:\n\n　**HP**: {health}\n\n　**Damage**: {dmg}\n\n\n**Mana Cost**:\n\n　**Raw Mana Cost**: {mana}\n\n　**With Max Reduction**: {manamin}"
                                  .format(health=hp, dmg=damage, mana=int(manacost), manamin=int(manacostmin)), color=0x911ef5)

        await message.reply(embeds=[embed])

@bot.component("arrow_prev")
async def button_response(ctx: interactions.CommandContext):
    await ctx.edit("balls")

@bot.component("arrow_next")
async def menu_response(ctx: interactions.CommandContext):
    await ctx.edit("balls 2")

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
   embed = interactions.Embed(title="Faq",
                              description="Please select a section to learn more about\n\nIf you still have any questions, feel free to ask them in #questions-and-advice!",
                              color=0x911ef5)

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
    
@bot.command(
   name="mana",
   description="Calculates the mana cost given HP and Damage",
   options=[
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
      interactions.Option(
         name="breeze",
         description="The amount of breeze you have in total",
         type=interactions.OptionType.INTEGER,
         required=False,
      ),
   ],
)
async def manacostcalculator(ctx: interactions.CommandContext, hp: str, damage:
 str, breeze=0):
   if (hp.endswith('m')):

      hp_int = int(hp[:-1]) * 1000000

   elif (hp.endswith('k')):

      hp_int = int(hp[:-1]) * 1000

   if (damage.endswith('m')):

      damage_int = int(damage[:-1]) * 1000000

   elif (damage.endswith('k')):

      damage_int = int(damage[:-1]) * 1000

   manacost = damage_int / 50 + hp_int / 100000

   manacostmin = -1
   
   minstr = "**With Max Reduction:**"
    
   if breeze > 40 and breeze < 60:

      manacostmin = manacost * 0.268 * 0.6
      minstr += " (using b10 equipment and wise drag)"

   elif breeze >= 60:

      manacostmin = manacost * 0.4 * (100-breeze)*0.01
      minstr += "(using nether armor)"

   else:

      minstr += "(using wise drag)"

      manacostmin = manacost * 0.268 * (100 - breeze) * 0.01

   minstr += " " + str(manacostmin)

   embed = interactions.Embed(title="**Mana Cost Calculation**",
                              description="**Summon Stats**:\n\n　**HP**: {health}\n\n　**Damage**: {dmg}\n\n\n**Mana Cost**:\n\n　**Raw Mana Cost**: {mana}\n\n {minimumstring}"
                              .format(health=hp, dmg=damage, mana=manacost, minimumstring = minstr), color=0x911ef5)

   await ctx.send(embeds=[embed])

bot.start()

