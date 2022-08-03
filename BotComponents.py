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

price_ltoh = interactions.SelectOption(
    label="Price (Lowest)",
    value="price_l",
    description="Sort By Price - Lowest to Highest",
)

price_htol = interactions.SelectOption(
    label="Price (Highest)",
    value="price_h",
    description="Sort By Price - Highest to Lowest",
)

admin_souls = interactions.SelectOption(
    label="Admin Souls",
    value="admin",
    description="Shows Admin Souls Only",
)

hypixel_souls = interactions.SelectOption(
    label="Hypixel Souls",
    value="hypixel",
    description="Shows Hypixel Souls Only",
)

other_souls = interactions.SelectOption(
    label="Other Souls",
    value="other",
    description="Containing Non-Admin and Non-Hypixel Souls Only",
)

sort_menu = interactions.SelectMenu(
    options=[price_ltoh, price_htol, admin_souls, hypixel_souls, other_souls],
    placeholder="Sort by.....",
    custom_id="sort_menu",
)

next_page = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="<:arrow_forward:>",
    custom_id="arrow_next"
)

prev_page = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="<:arrow_backward:>",
    custom_id="arrow_prev"
)

num_souls = interactions.TextInput(
    style=interactions.TextStyleType.SHORT,
    label="How many souls would you like?",
    custom_id="num_souls",
    min_length=1,
    max_length=1,
)

pages_row = interactions.ActionRow.new(next_page, prev_page)
menu_row = interactions.ActionRow.new(sort_menu)

souls_modal = interactions.Modal(
        title="Souls Form",
        custom_id="souls_form",
        components=[num_souls],
)
