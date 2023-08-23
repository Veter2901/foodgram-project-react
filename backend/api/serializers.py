from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (IntegerField, ReadOnlyField,
                                   SerializerMethodField)
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from recipes.models import (FavoriteRecipe, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscribe, User


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')
        required_fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )


class UserListSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


class SubscribeRecipeSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscribeSerializer(UserListSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на данного пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return SubscribeRecipeSerializer(
            recipes,
            many=True).data


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(ModelSerializer):
    id = ReadOnlyField(
        source='ingredient.id')
    name = ReadOnlyField(
        source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeReadSerializer(ModelSerializer):
    author = UserListSerializer(
        read_only=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe',
        required=True,
    )
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        return (self.context.get('request').user.is_authenticated
                and FavoriteRecipe.objects.filter(
                    user=self.context.get('request').user,
                    recipe=obj
        ).exists())

    def get_is_in_shopping_cart(self, obj):
        return (self.context.get('request').user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=self.context.get('request').user,
                    recipe=obj
        ).exists())


class IngredientsEditSerializer(ModelSerializer):
    id = IntegerField(write_only=True)
    amount = IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeEditSerializer(ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientsEditSerializer(
        many=True
    )
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserListSerializer(
        read_only=True
    )
    cooking_time = IntegerField(
        min_value=1,
        max_value=300,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        name = data.get('name')
        if len(name) < 4 or not name.isalpha():
            raise ValidationError({
                'name': 'Должно быть мин. 4 знака и мин. 1 буква.'
            })

        ingredients = data.get('ingredients')
        if not ingredients or len(ingredients) == 0:
            raise ValidationError({
                'ingredients': 'Укажите хотя бы один ингредиент'
            })

        ing_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ing_ids) != len(set(ing_ids)) or not all(
            Ingredient.objects.filter(id=id).exists() for id in ing_ids
        ):
            raise ValidationError({
                'ingredients': 'Указаны некорректные ингредиенты'
            })

        tags = data.get('tags')
        if not tags or len(tags) == 0 or len(tags) != len(set(tags)):
            raise ValidationError({
                'tags': 'Укажите хотя бы один уникальный тег'
            })

        amounts = data.get('ingredients')
        if any(item['amount'] < 1 for item in amounts):
            raise ValidationError({
                'amount': 'Количество ингредиента не может быть меньше 1'
            })

        cooking_time = data.get('cooking_time')
        if cooking_time < 1 or cooking_time > 300:
            raise ValidationError({
                'cooking_time': 'Укажите время от 1 до 300 минут'
            })

        return data

    @transaction.atomic
    def create_ingredients_amounts(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientInRecipe.objects.bulk_create([
                IngredientInRecipe(
                    ingredient_id=ingredient.get('id'),
                    recipe=recipe,
                    amount=ingredient.get('amount'),)
            ])

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if ingredients:
            instance.ingredients.clear()
            self.create_ingredients_amounts(ingredients, instance)
        if tags:
            instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data

class RecipeBriefSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

class RecipeShortSerializer(ModelSerializer):
    """Серилизатор полей избранных рецептов и покупок."""

    class Meta:
        fields = (
            'name', 'text', 'cooking_time',
            'image',
        )
        model = Recipe

class FavoriteSerializer(ModelSerializer):
    """Сериализатор для избранных рецептов."""

    class Meta:
        fields = (
            'recipe', 'user'
        )
        model = FavoriteRecipe

    def validate(self, data):
        if FavoriteRecipe.objects.filter(user = data['user'], recipe=data['recipe']).exists():
            raise ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
    
class ShopListSerializer(ModelSerializer):
    """Сериализатор для списка покупок."""
    class Meta:
        fields = (
            'recipe', 'user'
        )
        model = ShoppingCart

    def validate(self, data):
        if ShoppingCart.objects.filter(user = data['user'], recipe=data['recipe']).exists():
            raise ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
