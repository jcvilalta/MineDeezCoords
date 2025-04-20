import discord
from discord import app_commands
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

def load_coords():
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

def save_coords(data):
    with open(coords_file, "w") as file:
        json.dump(data, file, indent=4)

@bot.event
async def on_ready():
    print(f"✅ Connectat com a {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Sincronitzades {len(synced)} comandes")
    except Exception as e:
        print(f"❌ Error sincronitzant: {e}")

@bot.tree.command(name="coords", description="Guarda coordenades per dimensió")
@app_commands.describe(
    location="Nom del lloc",
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
    await interaction.response.defer()
    
    coords_data = load_coords()
    dim = dimension.value
    
    # Actualitzem coordenades
    coords_data["dimensions"][dim][location] = {"x": x, "y": y, "z": z}
    
    # Generem el contingut formatat
    content = "```\n"
    content += "📍 COORDENADES GLOBALS\n"
    content += "════════════════════════\n\n"
    
    for dim_name in ["overworld", "nether", "end"]:
        entries = coords_data["dimensions"][dim_name]
        content += f"【{dim_name.upper()}】\n"
        content += "─" * (len(dim_name) + 6) + "\n"
        
        if entries:
            for loc, coord in entries.items():
                content += f"• {loc.ljust(15)} X: {str(coord['x']).rjust(5)} "
                content += f"Y: {str(coord['y']).rjust(3)} Z: {str(coord['z']).rjust(5)}\n"
        else:
            content += "   (sense dades)\n"
        
        content += "\n"
    
    content += "```"  # Tancament del code block
    
    channel = interaction.channel
    channel_id = str(channel.id)
    
    try:
        if channel_id in coords_data["messages"]:
            message_id = int(coords_data["messages"][channel_id])
            message = await channel.fetch_message(message_id)
            await message.edit(content=content)
        else:
            raise ValueError
            
    except (discord.NotFound, discord.Forbidden, ValueError):
        try:
            message = await channel.send(content)
            coords_data["messages"][channel_id] = message.id
        except discord.Forbidden:
            await interaction.followup.send("❌ Error de permisos!")
            return
            
    save_coords(coords_data)
    await interaction.delete_original_response()

bot.run(TOKEN)