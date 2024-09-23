import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        # Этот параметр указывает Django, что этот класс не является представлением таблицы
        abstract = True

class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
        
class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('Жанр')
        verbose_name_plural = _('Жанры')
        
    def __str__(self):
        return self.name

class Person(UUIDMixin, TimeStampedMixin):
    class Gender(models.TextChoices):
        MALE = 'male', _('male')
        FEMALE = 'female', _('female')
        
    full_name = models.CharField(_('full name'), max_length=1024)
    gender = models.TextField(_('gender'), choices=Gender.choices, null=True) 
    
    class Meta:
        db_table = "content\".\"person"
        indexes = [
            models.Index(fields=["full_name"], name="person_full_name_idx"),
        ]
        verbose_name = _('Участник')
        verbose_name_plural = _('Участники')
        
    def __str__(self):
        return self.full_name
        
class Filmwork(UUIDMixin, TimeStampedMixin):
    types=[
        ('movie',_('Кино')),
        ('tv_show',_('Шоу')),
        ]
    title = models.CharField(_('title'), max_length=1024)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateTimeField(_('creation date'),blank=True)
    rating = models.FloatField(_('rating'),
            blank=True,
            validators=[MinValueValidator(0),
            MaxValueValidator(100)]
           ) 
    type = models.TextField(_('type'), choices=types )
    genres = models.ManyToManyField(Genre, through='GenreFilmwork',verbose_name=_('genres'))
    persons = models.ManyToManyField(Person, through='PersonFilmwork',verbose_name=_('persons'))
    certificate = models.CharField(_('certificate'), max_length=512, blank=True, null=True)
    # Базовая папка указана в файле настроек как MEDIA_ROOT
    file_path = models.FileField(_('file'), blank=True, null=True, upload_to='movies/')

    class Meta:
        db_table = "content\".\"film_work"
        indexes = [
            models.Index(fields=["creation_date"], name="film_work_creation_date_idx"),
            models.Index(fields=["rating"], name="film_work_rating_idx"),
            models.Index(fields=["title"], name="film_work_title_idx"),
        ]
        verbose_name = _('Фильм')
        verbose_name_plural = _('Фильмы')
        
    def __str__(self):
        return self.title
        
class GenreFilmwork(UUIDMixin, TimeStampedMixin):
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        db_table = "content\".\"genre_film_work" 
        indexes = [
            models.Index(fields=["film_work_id","genre_id"], name="film_work_genre_idx"),
        ]
        verbose_name = _('Жанр фильма')
        verbose_name_plural = _('Жанры фильма')
        
class PersonFilmwork(UUIDMixin, TimeStampedMixin):
    class Role(models.TextChoices):
        ACTOR = 'actor', _('Actor')
        DIRECTOR = 'director', _('Director')
        SCREENWRITER = 'screenwriter', _('Screenwriter')
        
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE,verbose_name='film_work')
    person = models.ForeignKey('Person', on_delete=models.CASCADE,verbose_name='person')
    role = models.TextField(_('role'),choices=Role.choices)
    
    class Meta:
        db_table = "content\".\"person_film_work"
        indexes = [
            models.Index(fields=["film_work_id","person_id"], name="film_work_person_idx"),
        ]
        verbose_name = _('Участник фильма')
        verbose_name_plural = _('Участники фильма')