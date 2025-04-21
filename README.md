# 🎮 MineDeezCoords Bot

**Discord bot per gestionar coordenades de Minecraft amb suport català**  
*Mantingueu el registre de les vostres ubicacions de Minecraft directament a Discord!*

[![Discord.py](https://img.shields.io/badge/discord.py-2.3.2+-blue.svg)](https://discordpy.readthedocs.io/)
[![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

![Banner Example](/banner1.png) <!-- Podeu afegir una imatge real aquí -->

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
```

## 🕹️ Ús Bàsic
### 💾 Guardar coordenades
```bash
/coords location:"Cova Diamants" dimension:Overworld x:100 y:64 z:-200
```

### 🔍 Cercar coordenades
```bash
# Per dimensió
/getcoords dimension:Nether

# Per ubicació específica
/getcoords location:"Cova Diamants"

# Totes les coordenades
/getcoords
```

### 📚 Estructura de Dades
El bot utilitza un fitxer coordinates.json amb aquest format:

```json
{
  "messages": {
    "canal_id": missatge_id
  },
  "dimensions": {
    "overworld": {
      "Cova Diamants": {"x": 100, "y": 64, "z": -200}
    },
    "nether": {},
    "end": {}
  }
}
```

## 🛠️ Desenvolupament
### Contribuir

Fes un fork del repositori

Crea una branca nova (git checkout -b nova-funcio)

Fes commit dels canvis (git commit -am 'Afegida nova funció')

Fes push a la branca (git push origin nova-funcio)

Obre una Pull Request