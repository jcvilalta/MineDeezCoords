# Import required libraries
import discord
from discord import app_commands, Embed, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

TEST_GUILD_ID = 916239256677142559

# Configure bot with basic intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# File to store coordinates data
coords_file = "coordinates.json"

# Emoji mapping for different dimensions
DIMENSION_EMOJIS = {
    "overworld": "🌳",
    "nether": "👹",
    "end": "😈"
}

# ---------- HELPERS ----------
def format_location_name(location: str) -> str:
    """Formats location names following Catalan rules while preserving mid-word capitals."""
    prepositions = {"de", "del", "d'", "la", "les", "i", "al", "en", "per"}
    words = location.split()
    
    if not words:
        return ""
    
    first_word = words[0]
    formatted_words = [first_word[0].upper() + first_word[1:]]  # Capitalitza primera lletra
    
    for word in words[1:]:
        lower_word = word.lower()
        if lower_word in prepositions:
            formatted_words.append(lower_word)
        else:
            if word == word.lower():
                formatted_words.append(word.capitalize())
            else:
                formatted_words.append(word)
    
    return " ".join(formatted_words)

def load_coords() -> dict:
    try:
        with open(coords_file, "r", encoding='utf-8') as file:
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
    with open(coords_file, "w", encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def create_global_embed(coords_data: dict) -> Embed:
    """Crea l'embed global amb totes les coordenades"""
    embed = Embed(
        title="🌍 COORDENADES GLOBALS",
        color=0xBF40BF,
        description="**Coordenades guardades per dimensió:**"
    )
    
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
    
    return embed

# ---------- AUTOCOMPLETE ----------
async def location_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    coords_data = load_coords()
    all_locations = []
    for dim in coords_data["dimensions"].values():
        all_locations.extend(dim.keys())
    filtered = [loc for loc in all_locations if current.lower() in loc.lower()]
    return [app_commands.Choice(name=loc, value=loc) for loc in filtered[:25]]

# ---------- VIEWS ----------
class ConfirmDeleteView(View):
    def __init__(self, target, is_dimension=False):
        super().__init__(timeout=30)
        self.target = target
        self.is_dimension = is_dimension
        self.confirmed = False

    @discord.ui.button(label="✅ Confirmar", style=ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        self.confirmed = True
        self.stop()
        await interaction.response.edit_message(content="✅ Eliminant...", view=None)

    @discord.ui.button(label="❌ Cancelar", style=ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        self.stop()
        await interaction.response.edit_message(content="❌ Acció cancel·lada", view=None)

# ---------- COMMANDS ----------
@bot.event
async def on_ready():
    print(f"✅ Connectat com a {bot.user}")
    try:
        await bot.tree.sync()
        print("🔁 Comandes GLOBALS sincronitzades!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def sync(ctx):
    """Força la sincronització global"""
    await bot.tree.sync()
    await ctx.send("✅ Comandes globals sincronitzades!")

@bot.tree.command(name="coords", description="Desa coordenades per una dimensió")
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
    await interaction.response.defer()
    
    coords_data = load_coords()
    dim = dimension.value
    
    formatted_location = format_location_name(location)
    coords_data["dimensions"][dim][formatted_location] = {"x": x, "y": y, "z": z}
    save_coords(coords_data)
    
    embed = create_global_embed(coords_data)
    embed.set_footer(text=f"🔄 Actualitzat per: {interaction.user.name}")
    
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
async def getcoords_cmd(interaction: discord.Interaction, dimension: str = None, location: str = None):
    await interaction.response.defer()
    
    coords_data = load_coords()
    embed = Embed(color=0xBF40BF)

    if dimension:
        dim_emoji = DIMENSION_EMOJIS[dimension]
        entries = coords_data["dimensions"][dimension]
        
        if entries:
            content = "\n".join([f"{loc}: X={c['x']} Y={c['y']} Z={c['z']}" for loc, c in entries.items()])
            embed.description = f"{dim_emoji}**COORDENADES DE L'{dimension.upper()}:**\n```\n{content}\n```"
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
                content.append(f"{DIMENSION_EMOJIS[dim_name]} {dim_name.capitalize()}: X={coord['x']} Y={coord['y']} Z={coord['z']}")
                found = True
                
        if found:
            embed.description = f"🔍 **COORDENADES DE '{formatted_location}':**\n```\n" + "\n".join(content) + "\n```"
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

@bot.tree.command(name="editcoords", description="Edita coordenades existents")
@app_commands.describe(
    location="Ubicació a editar",
    dimension="Dimensió",
    x="Nova coordenada X",
    y="Nova coordenada Y",
    z="Nova coordenada Z"
)
@app_commands.choices(dimension=[
    app_commands.Choice(name="Overworld", value="overworld"),
    app_commands.Choice(name="Nether", value="nether"),
    app_commands.Choice(name="End", value="end")
])
@app_commands.autocomplete(location=location_autocomplete)
async def editcoords_cmd(interaction: discord.Interaction, 
                        location: str, 
                        dimension: str, 
                        x: int, 
                        y: int, 
                        z: int):
    await interaction.response.defer()
    
    coords_data = load_coords()
    dim = dimension
    formatted_location = format_location_name(location)
    
    # Verificar si l'ubicació existeix a la dimensió
    if formatted_location not in coords_data["dimensions"][dim]:
        await interaction.followup.send(f"❌ `{formatted_location}` no existeix a {dim.capitalize()}!", ephemeral=True)
        return
    
    # Actualitzar coordenades
    coords_data["dimensions"][dim][formatted_location] = {"x": x, "y": y, "z": z}
    save_coords(coords_data)
    
    # Actualitzar missatge global
    channel = interaction.channel
    channel_id = str(channel.id)
    try:
        if channel_id in coords_data["messages"]:
            message = await channel.fetch_message(coords_data["messages"][channel_id])
            new_embed = create_global_embed(coords_data)
            new_embed.set_footer(text=f"🔄 Actualitzat per: {interaction.user.name}")
            await message.edit(embed=new_embed)
    except Exception as e:
        print(f"Error actualitzant missatge: {e}")
    
    await interaction.followup.send(f"✅ **{formatted_location}** actualitzat a {dim.capitalize()}!", ephemeral=True)

@bot.tree.command(name="deletecoords", description="Elimina coordenades existents")
@app_commands.describe(
    location="Ubicació a eliminar",
    dimension="Dimensió a buidar"
)
@app_commands.choices(dimension=[
    app_commands.Choice(name="Overworld", value="overworld"),
    app_commands.Choice(name="Nether", value="nether"),
    app_commands.Choice(name="End", value="end")
])
@app_commands.autocomplete(location=location_autocomplete)
async def deletecoords_cmd(interaction: discord.Interaction, location: str = None, dimension: str = None):
    await interaction.response.defer(ephemeral=True)
    
    coords_data = load_coords()
    target = None
    is_dimension = False

    if location and dimension:
        await interaction.followup.send("❌ Selecciona només ubicació O dimensió", ephemeral=True)
        return
        
    if location:
        formatted_location = format_location_name(location)
        target = formatted_location
        found = False
        for dim in ["overworld", "nether", "end"]:
            if formatted_location in coords_data["dimensions"][dim]:
                del coords_data["dimensions"][dim][formatted_location]
                found = True
        if not found:
            await interaction.followup.send(f"❌ Ubicació no trobada: {formatted_location}", ephemeral=True)
            return
            
    elif dimension:
        target = dimension
        is_dimension = True
        coords_data["dimensions"][dimension].clear()
        
    else:
        await interaction.followup.send("❌ Selecciona una ubicació o dimensió", ephemeral=True)
        return

    view = ConfirmDeleteView(target, is_dimension)
    msg_content = f"⚠️ Confirmes eliminar **{target}**? Aquesta acció és irreversible!"
    
    await interaction.followup.send(msg_content, view=view, ephemeral=True)
    await view.wait()
    
    if view.confirmed:
        save_coords(coords_data)
        await interaction.edit_original_response(content=f"✅ S'ha eliminat: **{target}**")
        
        # Actualitza missatge global
        channel = interaction.channel
        channel_id = str(channel.id)
        if channel_id in coords_data["messages"]:
            try:
                message = await channel.fetch_message(coords_data["messages"][channel_id])
                new_embed = create_global_embed(coords_data)
                new_embed.set_footer(text=f"🔄 Actualitzat per: {interaction.user.name}")
                await message.edit(embed=new_embed)
            except Exception as e:
                print(f"Error actualitzant missatge: {e}")
    else:
        await interaction.edit_original_response(content="❌ Acció cancel·lada")

# ---------- RUN BOT ----------
bot.run(TOKEN)