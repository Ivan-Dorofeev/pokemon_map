
import folium
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils.timezone import localtime

from pokemon_entities.models import Pokemon, PokemonEntity

MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    pokemons = Pokemon.objects.all()
    active_pokemons = PokemonEntity.objects.filter(appeared_at__lte=localtime(),
                                                   disappeared_at__gte=localtime())
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon in active_pokemons:
        pokemons_entity_photo = request.build_absolute_uri(f'/media/{pokemon.pokemon.photo}')
        add_pokemon(
            folium_map, pokemon.lat,
            pokemon.lon,
            pokemons_entity_photo
        )

    pokemons_on_page = []
    for pokemon in pokemons:
        img_url = request.build_absolute_uri(f'/media/{pokemon.photo}')
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': img_url,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemons = Pokemon.objects.all()

    for pokemon in pokemons:
        if pokemon.id == int(pokemon_id):
            selected_pokemon = PokemonEntity.objects.filter(pokemon=pokemon)
            break
    else:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in selected_pokemon:
        img_url = request.build_absolute_uri(f'/media/{pokemon_entity.pokemon.photo}')
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            img_url
        )

    previous_evolution_img = request.build_absolute_uri(f'/media/{pokemon.previous_evolution.photo}')

    next_evolution = ""
    next_evolution_serialized = pokemon.parent.all()
    if next_evolution_serialized:
        if len(next_evolution_serialized) > 1:
            next_evolution = next_evolution_serialized[1]
        else:
            next_evolution = next_evolution_serialized[0]
        next_evolution_img = request.build_absolute_uri(f'/media/{next_evolution.photo}')
    else:
        next_evolution_img = ""

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': {'title_ru': pokemon.title, 'img_url': img_url, "description": pokemon.description,
                    "title_en": pokemon.title_en, "title_jp": pokemon.title_jp,
                    "previous_evolution": pokemon.previous_evolution,
                    'previous_evolution_img': previous_evolution_img, "next_evolution": next_evolution,
                    "next_evolution_img": next_evolution_img}})
