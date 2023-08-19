from colorfield.fields import ColorField
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=settings.MAX_LEN,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цветовой HEX-код',
        unique=True,
        max_length=settings.MAX_LEN,
        default='#49B64E',
        null=True,
        blank=True,
    )
    slug = models.SlugField(
        verbose_name='Slug тега',
        max_length=settings.MAX_LEN,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=settings.MAX_LEN,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=settings.MAX_LEN,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit')]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=settings.MAX_LEN,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=1,
        validators=(
            MinValueValidator(1, 'Минимальное значение 1 минута!'),
            MaxValueValidator(300, 'Максимальное значение 300 минут!'),),
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientInRecipe',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Автор: {self.author.username} рецепт: {self.name}'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингридиент',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1,
        validators=(
            MinValueValidator(1, 'Минимальное количество 1'),
            MaxValueValidator(5000, 'Максимальное количество 5000'),),
    )

    class Meta:
        ordering = ('ingredient',)
        verbose_name = 'Ингедиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient')]

    def __str__(self):
        return (
            f'{self.ingredient.name} {self.amount} '
            f'({self.ingredient.measurement_unit}) '
            f'в рецепте {self.recipe.name}.'
        )


class CustomRecipeModel(models.Model):
    user = models.ForeignKey(
        User,
        related_name="%(class)s",
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="%(class)s",
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('id',)


class FavoriteRecipe(CustomRecipeModel):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourite')]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(CustomRecipeModel):
    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_cart')]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину покупок'
