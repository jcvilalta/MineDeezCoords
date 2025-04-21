# Import required libraries
import discord
from discord import app_commands, Embed
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

coords_file = "coordinates.json"

DIMENSION_EMOJIS = {
    "overworld": "🌳",
    "nether": "👹",
    "end": "😈"
}

def format_location_name(location: str) -> str:
    prepositions = {"de", "del", "d'", "la", "les", "i", "al", "en", "per"}
    words = location.lower().split()
    
    if not words:
        return ""
    
    formatted_words = [words[0].capitalize()]
    for word in words[1:]:
        formatted_words.append(word if word in prepositions else word.capitalize())
    
    return " ".join(formatted_words)

def load_coords() -> dict:
    try:
        with open(coords_file, "r") as file:
            data = json.load(file)
            return {
                "messages": {str(k): v for k, v in data.get("messages", {}).items()},
                "dimensions": data.get("dimensions", {
                    "overworld": {},
                    "nether": {},
                    "end": {}
                })
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "messages": {},
            "dimensions": {
                "overworld": {},
                "nether": {},
                "end": {}
            }
        }

def save_coords(data: dict) -> None:
    with open(coords_file, "w") as file:
        json.dump(data, file, indent=4)

@bot.event
async def on_ready():
    print(f"✅ Connectat com a {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

@bot.tree.command(name="coords", description="Save coordinates for a dimension")
@app_commands.describe(
    location="Name of the location",
    dimension="Dimension",
    x="X coordinate",
    y="Y coordinate",
    z="Z coordinate"
)
@app_commands.choices(dimension=[
    app_commands.Choice(name="Overworld", value="overworld"),
    app_commands.Choice(name="Nether", value="nether"),
    app_commands.Choice(name="End", value="end")
])
async def coords_cmd(interaction: discord.Interaction, location: str, dimension: app_commands.Choice[str], x: int, y: int, z: int):
    await interaction.response.defer()
    
    coords_data = load_coords()
    dim = dimension.value
    
    formatted_location = format_location_name(location)
    coords_data["dimensions"][dim][formatted_location] = {"x": x, "y": y, "z": z}
    save_coords(coords_data)
    
    embed = Embed(
        title="🌍 GLOBAL COORDINATES",
        color=0xBF40BF,
        description="**Saved coordinates per dimension:**"
    )
    
    for dim_name in ["overworld", "nether", "end"]:
        emoji = DIMENSION_EMOJIS[dim_name]
        entries = coords_data["dimensions"][dim_name]
        
        if entries:
            content = [f"{emoji} **{dim_name.capitalize()}**"]
            coord_lines = [f"{loc}: X={c['x']} Y={c['y']} Z={c['z']}" for loc, c in entries.items()]
            content.append(f"```\n" + "\n".join(coord_lines) + "\n```")
        else:
            content = [f"{emoji} **{dim_name.capitalize()}**", "```\n🚫 No coordinates\n```"]
            
        embed.add_field(name="\u200b", value="\n".join(content), inline=False)
    
    embed.set_footer(text=f"🔄 Last updated by: {interaction.user.name}")
    channel = interaction.channel
    channel_id = str(channel.id)
    
    try:
        if channel_id in coords_data["messages"]:
            message_id = int(coords_data["messages"][channel_id])
            message = await channel.fetch_message(message_id)
            await message.edit(embed=embed)
        else:
            raise ValueError
    except (discord.NotFound, discord.Forbidden, ValueError):
        try:
            message = await channel.send(embed=embed)
            coords_data["messages"][channel_id] = message.id
            save_coords(coords_data)
        except discord.Forbidden:
            await interaction.followup.send("❌ Missing permissions!")
            return
    
    await interaction.delete_original_response()

# Funció d'autocompletat definida ABANS de la comanda
async def location_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    coords_data = load_coords()
    all_locations = []
    for dim in coords_data["dimensions"].values():
        all_locations.extend(dim.keys())
    filtered = [loc for loc in all_locations if current.lower() in loc.lower()]
    return [app_commands.Choice(name=loc, value=loc) for loc in filtered[:25]]

@bot.tree.command(name="getcoords", description="Mostra coordenades amb filtres opcionals")
@app_commands.describe(
    dimension="Filtra per dimensió",
    location="Cerca una ubicació específica"
)
@app_commands.choices(dimension=[
    app_commands.Choice(name="Overworld", value="overworld"),
    app_commands.Choice(name="Nether", value="nether"),
    app_commands.Choice(name="End", value="end")
])
@app_commands.autocomplete(location=location_autocomplete)  # Referència directa
async def getcoords_cmd(interaction: discord.Interaction, 
                       dimension: app_commands.Choice[str] = None, 
                       location: str = None):
    await interaction.response.defer()
    
    coords_data = load_coords()
    embed = Embed(title="🔍 COORDENADES TROBADES", color=0xBF40BF, description="**Resultats de la cerca:**")
    
    if location:
        formatted_location = format_location_name(location)
        found = False
        for dim_name in ["overworld", "nether", "end"]:
            entries = coords_data["dimensions"][dim_name]
            if formatted_location in entries:
                coord = entries[formatted_location]
                embed.add_field(
                    name=f"{DIMENSION_EMOJIS[dim_name]} {dim_name.capitalize()}",
                    value=f"```\nX={coord['x']} | Y={coord['y']} | Z={coord['z']}\n```",
                    inline=False
                )
                found = True
        if not found:
            embed.description = f"🚫 No s'han trobat coordenades per: `{formatted_location}`"
    elif dimension:
        dim_name = dimension.value
        entries = coords_data["dimensions"][dim_name]
        if entries:
            content = [f"{loc}: X={c['x']} Y={c['y']} Z={c['z']}" for loc, c in entries.items()]
            embed.add_field(
                name=f"{DIMENSION_EMOJIS[dim_name]} {dim_name.capitalize()}",
                value=f"```\n" + "\n".join(content) + "\n```",
                inline=False
            )
        else:
            embed.description = f"🚫 No hi ha coordenades a {dim_name.capitalize()}"
    else:
        for dim_name in ["overworld", "nether", "end"]:
            entries = coords_data["dimensions"][dim_name]
            if entries:
                content = [f"{loc}: X={c['x']} Y={c['y']} Z={c['z']}" for loc, c in entries.items()]
                embed.add_field(
                    name=f"{DIMENSION_EMOJIS[dim_name]} {dim_name.capitalize()}",
                    value=f"```\n" + "\n".join(content) + "\n```",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{DIMENSION_EMOJIS[dim_name]} {dim_name.capitalize()}",
                    value="```\n🚫 Cap coordenada\n```",
                    inline=False
                )
    
    await interaction.followup.send(embed=embed)

bot.run(TOKEN)