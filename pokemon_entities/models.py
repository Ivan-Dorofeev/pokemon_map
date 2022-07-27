from django.db import models  # noqa F401


class Pokemon(models.Model):
    title = models.CharField("Название", max_length=200)
    photo = models.ImageField("Изображение", upload_to='pokemons')
    description = models.TextField("Описание", max_length=1000)
    title_en = models.CharField("Название на ангийском", max_length=30, blank=True)
    title_jp = models.CharField("Название на японском", max_length=30, blank=True)
    previous_evolution = models.ForeignKey('self', related_name='pokemon_evolusions', on_delete=models.CASCADE,
                                           blank=True, null=True)

    def __str__(self):
        return self.title


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(Pokemon, related_name='pokemons', on_delete=models.CASCADE)
    lat = models.FloatField("Широта")
    lon = models.FloatField("Долгота")
    appeared_at = models.DateTimeField("Время появления", null=True)
    disappeared_at = models.DateTimeField("Время исчезновение", null=True)
    level = models.IntegerField("Уровень", default=0)
    health = models.IntegerField("Здоровье", default=0)
    strength = models.IntegerField("Сила", default=0)
    defence = models.IntegerField("Защита", default=0)
    stamina = models.IntegerField("Выносливость", default=0)

    def __str__(self):
        return f'{self.pokemon} {self.appeared_at.date()} - {self.disappeared_at.date()}'
