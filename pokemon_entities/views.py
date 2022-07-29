import folium
from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, get_list_or_404
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
    active_pokemons_entities = PokemonEntity.objects.filter(appeared_at__lte=localtime(),
                                                            disappeared_at__gte=localtime())
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in active_pokemons_entities:
        pokemons_entity_photo = request.build_absolute_uri(f'/media/{pokemon_entity.pokemon.photo}')
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
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
    pokemon_by_id = get_list_or_404(Pokemon, id=pokemon_id)[0]

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    img_url = request.build_absolute_uri(f'/media/{pokemon_by_id.photo}')
    all_pokemons_by_pokemon_id = PokemonEntity.objects.filter(pokemon=pokemon_by_id)
    for pokemon_for_add_to_map in all_pokemons_by_pokemon_id:
        add_pokemon(folium_map, pokemon_for_add_to_map.lat, pokemon_for_add_to_map.lon, img_url)

    previous_evolution_img = request.build_absolute_uri(f'/media/{pokemon_by_id.previous_evolution.photo}')

    next_evolution = ''
    next_evolution_img = ''
    pokemon_evolutions = pokemon_by_id.evolutions.all()
    if pokemon_evolutions:
        next_evolution = pokemon_evolutions.last()
        next_evolution_img = request.build_absolute_uri(f'/media/{next_evolution.photo}')

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': {'title_ru': pokemon_by_id.title, 'img_url': img_url,
                    "description": pokemon_by_id.description,
                    "title_en": pokemon_by_id.title_en, "title_jp": pokemon_by_id.title_jp,
                    "previous_evolution": pokemon_by_id.previous_evolution,
                    'previous_evolution_img': previous_evolution_img, "next_evolution": next_evolution,
                    "next_evolution_img": next_evolution_img}})
