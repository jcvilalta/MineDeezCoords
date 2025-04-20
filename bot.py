# Import required libraries
import discord
from discord import app_commands, Embed
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configure bot intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
bot = commands.Bot(command_prefix="!", intents=intents)

# File to store coordinates data
coords_file = "coordinates.json"

# Emojis for each dimension (visual representation)
DIMENSION_EMOJIS = {
    "overworld": "🌳",  # Overworld emoji
    "nether": "👹",     # Nether emoji
    "end": "😈"         # End emoji
}

def format_location_name(location: str) -> str:
    """
    Formats a location name to Title Case, ignoring prepositions.
    Example: "mina de carbó" -> "Mina de Carbó"
    """
    prepositions = {"de", "del", "d'", "la", "les", "i", "al", "en", "per"}
    words = location.lower().split()
    
    if not words:
        return ""
    
    # Capitalize first word
    formatted_words = [words[0].capitalize()]
    
    # Capitalize subsequent words if they are not prepositions
    for word in words[1:]:
        formatted_words.append(word if word in prepositions else word.capitalize())
    
    return " ".join(formatted_words)

def load_coords() -> dict:
    """
    Loads coordinates data from the JSON file.
    Returns a dictionary with messages and dimensions data.
    """
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
        # Return default structure if file doesn't exist or is invalid
        return {
            "messages": {},
            "dimensions": {
                "overworld": {},
                "nether": {},
                "end": {}
            }
        }

def save_coords(data: dict) -> None:
    """Saves coordinates data to the JSON file."""
    with open(coords_file, "w") as file:
        json.dump(data, file, indent=4)

@bot.event
async def on_ready():
    """Called when the bot connects to Discord."""
    print(f"✅ Connected as {bot.user}")
    try:
        # Sync slash commands with Discord
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
    """Slash command handler for saving/updating coordinates."""
    await interaction.response.defer()  # Acknowledge the interaction
    
    # Load existing data
    coords_data = load_coords()
    dim = dimension.value
    
    # Format location name (capitalization rules)
    formatted_location = format_location_name(location)
    
    # Update coordinates
    coords_data["dimensions"][dim][formatted_location] = {"x": x, "y": y, "z": z}
    save_coords(coords_data)
    
    # Build the embed message
    embed = Embed(
        title="🌍 GLOBAL COORDINATES",
        color=0xBF40BF,  # Purple accent color
        description="**Saved coordinates per dimension:**"
    )
    
    # Add a field for each dimension
    for dim_name in ["overworld", "nether", "end"]:
        emoji = DIMENSION_EMOJIS[dim_name]
        entries = coords_data["dimensions"][dim_name]
        
        if entries:
            content = [f"{emoji} **{dim_name.capitalize()}**"]
            coord_lines = []
            # Format coordinates as "Location: X=... Y=... Z=..."
            for loc, coord in entries.items():
                coord_lines.append(f"{loc}: X={coord['x']} Y={coord['y']} Z={coord['z']}")
            # Add coordinates in a code block
            content.append(f"```\n" + "\n".join(coord_lines) + "\n```")
        else:
            content = [f"{emoji} **{dim_name.capitalize()}**", "```\n🚫 No coordinates\n```"]
            
        embed.add_field(
            name="\u200b",  # Empty field name (invisible)
            value="\n".join(content),
            inline=False
        )
    
    # Add footer with last updater's name
    embed.set_footer(text=f"🔄 Last updated by: {interaction.user.name}")

    channel = interaction.channel
    channel_id = str(channel.id)
    
    try:
        # Edit existing message if available
        if channel_id in coords_data["messages"]:
            message_id = int(coords_data["messages"][channel_id])
            message = await channel.fetch_message(message_id)
            await message.edit(embed=embed)
        else:
            raise ValueError  # Trigger "new message" flow
            
    except (discord.NotFound, discord.Forbidden, ValueError):
        try:
            # Send new message and store its ID
            message = await channel.send(embed=embed)
            coords_data["messages"][channel_id] = message.id
            save_coords(coords_data)
        except discord.Forbidden:
            await interaction.followup.send("❌ Missing permissions!")
            return
    
    # Delete initial "bot is thinking" message
    await interaction.delete_original_response()

# Start the bot
bot.run(TOKEN)