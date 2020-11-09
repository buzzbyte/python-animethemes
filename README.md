# python-animethemes
A Python wrapper for AnimeThemes.moe API (incomplete).
Still a work-in-progress at the moment and subject to change.

Currently uses API endpoints at `https://animethemes.dev/api`

## Usage
```python
from animethemes import AnimeThemes

themes = AnimeThemes()

# Search for anime, themes, artists, etc.
search_result = themes.search("Bakemonogatari")
print(search_result.anime[0].name) # Bakemonogatari
print(search_result.themes[1].slug) # OP2

# Look up individual anime, themes, artists, etc.
anime_result = themes.anime("bakemonogatari")
print(anime_result.name) # Bakemonogatari
```