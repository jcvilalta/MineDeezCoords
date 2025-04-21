# 🎮 MineDeezCoords Bot

**Discord bot per gestionar coordenades de Minecraft amb suport català**  
*Mantingueu el registre de les vostres ubicacions de Minecraft directament a Discord!*

[![Discord.py](https://img.shields.io/badge/discord.py-2.3.2+-blue.svg)](https://discordpy.readthedocs.io/)
[![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

![Banner Example](https://via.placeholder.com/800x200.png?text=MineDeezCoords+Bot+Showcase) <!-- Podeu afegir una imatge real aquí -->

## ✨ Característiques Principals
- **💾 Emmagatzematge persistent** en fitxer JSON
- **🎮 Suport per 3 dimensions**:
  - 🌳 Overworld 
  - 👹 Nether
  - 😈 End
- **🔍 Cerca intel·ligent** amb autocompletat
- **📱 Interfície en català** amb formatatge correcte
- **🔄 Missatge global autoactualitzable**
- **⚙️ Gestió d'errors** i permisos

## 🚀 Començem

### 📋 Prerequisits
- Python 3.10+
- [Discord Bot Token](https://discord.com/developers/applications)
- Permisos del bot:
  - `applications.commands`
  - `Send Messages`
  - `Embed Links`

### ⚙️ Instal·lació
```bash
# Clona el repositori
git clone https://github.com/el-teu-usuari/MineDeezCoords.git

# Entra a la carpeta
cd MineDeezCoords

# Instal·la dependències
pip install -r requirements.txt

# Configura el token
echo "DISCORD_TOKEN=el-teu-token-aqui" > .env