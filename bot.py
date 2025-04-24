# Import required libraries
import discord
from discord import app_commands, Embed
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
from discord.ui import Button, View
import asyncio

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configure bot with basic intents
intents = discord.Intents.default()
intents.message_content = True  # Required for message content
bot = commands.Bot(command_prefix="!", intents=intents)

# File to store coordinates data
coords_file = "coordinates.json"

# Emoji mapping for different dimensions
DIMENSION_EMOJIS = {
    "overworld": "🌳",
    "nether": "👹",
    "end": "😈"
}

def format_location_name(location: str) -> str:
    """Formats location names following Catalan capitalization rules."""
    prepositions = {"de", "del", "d'", "la", "les", "i", "al", "en", "per"}
    words = location.split()  # Conservem la capitalització original
    
    if not words:
        return ""
    
    # Processem la primera paraula
    first_word = words[0]
    formatted_words = [first_word[0].upper() + first_word[1:]]  # Capitalitzem primera lletra
    
    # Processem la resta de paraules
    for word in words[1:]:
        lower_word = word.lower()
        if lower_word in prepositions:
            formatted_words.append(lower_word)
        else:
            # Conservem majúscules internes si existeixen
            if word == word.lower():
                formatted_words.append(word.capitalize())
            else:
                formatted_words.append(word)
    
    return " ".join(formatted_words)

def load_coords() -> dict:
    """Load coordinates data from JSON file."""
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
    """Save coordinates data to JSON file."""
    with open(coords_file, "w") as file:
        json.dump(data, file, indent=4)

@bot.event
async def on_ready():
    """Bot startup handler."""
    print(f"✅ Connectat com a {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# Command to save coordinates (user-facing text remains in Catalan)
@bot.tree.command(name="coords", description="Save coordinates for a dimension")
@app_commands.describe(
    location="Nom de la ubicació",
    dimension="Dimensió",
    x="Coordenada X",
    y="Coordenada Y",
    z="Coordenada Z"
)
@app_commands.choices(dimension=[
    app_commands.Choice(name="Overworld", value="overworld"),
    app_commands.Choice(name="Nether", value="nether"),
    app_commands.Choice(name="End", value="end")
])
async def coords_cmd(interaction: discord.Interaction, location: str, dimension: app_commands.Choice[str], x: int, y: int, z: int):
    """Handles coordinate saving functionality."""
    await interaction.response.defer()
    
    coords_data = load_coords()
    dim = dimension.value
    
    formatted_location = format_location_name(location)
    coords_data["dimensions"][dim][formatted_location] = {"x": x, "y": y, "z": z}
    save_coords(coords_data)
    
    # Create embed with updated coordinates
    embed = Embed(
        title="🌍 COORDENADES GLOBALS",
        color=0xBF40BF,
        description="**Coordenades guardades per dimensió:**"
    )
    
    # Populate embed fields for each dimension
    for dim_name in ["overworld", "nether", "end"]:
        emoji = DIMENSION_EMOJIS[dim_name]
        entries = coords_data["dimensions"][dim_name]
        
        if entries:
            content = [f"{emoji} **{dim_name.capitalize()}**"]
            coord_lines = [f"{loc}: X={c['x']} Y={c['y']} Z={c['z']}" for loc, c in entries.items()]
            content.append(f"```\n" + "\n".join(coord_lines) + "\n```")
        else:
            content = [f"{emoji} **{dim_name.capitalize()}**", "```\n🚫 Sense coordenades\n```"]
            
        embed.add_field(name="\u200b", value="\n".join(content), inline=False)
    
    embed.set_footer(text=f"🔄 Actualitzat per: {interaction.user.name}")
    
    # Update or create persistent message
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
            await interaction.followup.send("❌ Permisos insuficients!")
            return
    
    await interaction.delete_original_response()

# Autocomplete handler for location names
async def location_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    """Provides autocomplete suggestions for location names."""
    coords_data = load_coords()
    all_locations = []
    for dim in coords_data["dimensions"].values():
        all_locations.extend(dim.keys())
    filtered = [loc for loc in all_locations if current.lower() in loc.lower()]
    return [app_commands.Choice(name=loc, value=loc) for loc in filtered[:25]]

# Command to retrieve coordinates (user-facing text remains in Catalan)
@bot.tree.command(name="getcoords", description="Mostra coordenades amb filtres")
@app_commands.describe(
    dimension="Filtra per dimensió",
    location="Cerca una ubicació específica"
)
@app_commands.choices(dimension=[
    app_commands.Choice(name="Overworld", value="overworld"),
    app_commands.Choice(name="Nether", value="nether"),
    app_commands.Choice(name="End", value="end")
])
@app_commands.autocomplete(location=location_autocomplete)
async def getcoords_cmd(interaction: discord.Interaction, 
                       dimension: str = None, 
                       location: str = None):
    await interaction.response.defer()
    
    coords_data = load_coords()
    embed = Embed(color=0xBF40BF)

    if dimension:
        dim_emoji = DIMENSION_EMOJIS[dimension]
        entries = coords_data["dimensions"][dimension]
        
        if entries:
            content = "\n".join([f"{loc}: X={c['x']} Y={c['y']} Z={c['z']}" for loc, c in entries.items()])
            embed.description = (
                f"{dim_emoji}**COORDENADES DE L'{dimension.upper()}:**\n"
                f"```\n{content}\n```"
            )
        else:
            embed.description = f"{dim_emoji}**COORDENADES DE L'{dimension.upper()}:**\n```🚫 Cap coordenada```"

    elif location:
        formatted_location = format_location_name(location)
        found = False
        content = []
        
        for dim_name in ["overworld", "nether", "end"]:
            entries = coords_data["dimensions"][dim_name]
            if formatted_location in entries:
                coord = entries[formatted_location]
                content.append(
                    f"{DIMENSION_EMOJIS[dim_name]} {dim_name.capitalize()}: "
                    f"X={coord['x']} Y={coord['y']} Z={coord['z']}"
                )
                found = True
                
        if found:
            embed.description = (
                f"🔍 **COORDENADES DE '{formatted_location}':**\n"
                f"```\n" + "\n".join(content) + "\n```"
            )
        else:
            embed.description = f"🔍 **COORDENADES DE '{formatted_location}':**\n```🚫 No trobada```"

    else:
        embed.title = "🌍 COORDENADES GLOBALS"
        for dim_name in ["overworld", "nether", "end"]:
            entries = coords_data["dimensions"][dim_name]
            emoji = DIMENSION_EMOJIS[dim_name]
            
            if entries:
                content = "\n".join([f"{loc}: X={c['x']} Y={c['y']} Z={c['z']}" for loc, c in entries.items()])
                embed.add_field(
                    name=f"{emoji} **{dim_name.upper()}**",
                    value=f"```\n{content}\n```",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{emoji} **{dim_name.upper()}**",
                    value="```🚫 Cap coordenada```",
                    inline=False
                )
    
    await interaction.followup.send(embed=embed)

# Start the bot
bot.run(TOKEN)