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
    
    coords_data["dimensions"][dim][location] = {"x": x, "y": y, "z": z}
    save_coords(coords_data)
    
    embed = Embed(
        title="🌍 COORDENADES GLOBALS",
        color=0xBF40BF, # 🟣 Color lila vibrant
        description="**Coordenades per dimensió:**"
    )
    
    for dim_name in ["overworld", "nether", "end"]:
        emoji = DIMENSION_EMOJIS[dim_name]
        entries = coords_data["dimensions"][dim_name]
        
        if entries:
            content = [f"{emoji} **{dim_name.capitalize()}**"]
            coord_lines = []
            for loc, coord in entries.items():
                coord_lines.append(f"{loc}: X={coord['x']} Y={coord['y']} Z={coord['z']}")
            # Afegim bloc de codi
            content.append(f"```\n" + "\n".join(coord_lines) + "\n```")
        else:
            content = [f"{emoji} **{dim_name.capitalize()}**", "```\n🚫Cap coordenada\n```"]
            
        embed.add_field(
            name="\u200b",
            value="\n".join(content),
            inline=False
        )
    
    embed.set_footer(text=f"🔄 Última actualització: {interaction.user.name}")

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
            await interaction.followup.send("❌ Error de permisos!")
            return
    
    await interaction.delete_original_response()

bot.run(TOKEN)