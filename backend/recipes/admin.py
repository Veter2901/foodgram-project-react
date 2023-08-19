from django.contrib import admin
from django.contrib.admin import display
from django.core import exceptions
from django.db.models import Count

from .models import (FavoriteRecipe, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'id',
        'author',
        'added_in_favorites',
        'ingredients_list',
    )
    readonly_fields = ('added_in_favorites',)
    list_filter = ('author', 'name', 'tags',)
    filter_vertical = ('tags',)
    empty_value_display = '-пусто-'

    @display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return obj.obj_count

    @display(description='Ингредиенты')
    def ingredients_list(self, obj):
        ingredient_names = []
        for ingredient in obj.ingredients.all():
            ingredient_names.append(ingredient.name)
        return ', '.join(ingredient_names)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            obj_count=Count(
                "favoriterecipe",
                distinct=True
            ),
            ingredients_list=Count(
                "ingredients",
                distinct=True
            ),
        )

    def save_model(self, request, obj, form, change):
        if not obj.tags.exists():
            raise exceptions.ValidationError(
                "Необходимо указать теги для рецепта."
            )
        if not obj.ingredients.exists():
            raise exceptions.ValidationError(
                "Необходимо указать ингредиенты для рецепта."
            )
        super().save_model(request, obj, form, change)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'color', 'slug',
    )
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'recipe'
    )
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'recipe'
    )
    search_fields = ('recipe',)
    list_filter = ('id', 'user', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(IngredientInRecipe)
class IngredientInRecipe(admin.ModelAdmin):
    list_display = (
        'recipe', 'ingredient', 'amount',
    )
