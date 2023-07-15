from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.fields import SerializerMethodField
from drf_extra_fields.fields import Base64ImageField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from recipes.models import (Tag, Ingredient, Recipe,
                            IngredientsInRecipe, ShoppingCart, Favorite)
from users.models import User, Follow


class TagSerializer(serializers.ModelSerializer):
    """Серилизатор тэга."""
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Серилизатор ингредиента."""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для модели User.
    """
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для модели User.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

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

    def get_is_subscribed(self):
        """
        Проверяем подписку пользователя на автора.
        """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.follower.user()


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписок.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit_recipes = request.query_params.get('recipes_limit')
        if limit_recipes is not None:
            recipes = obj.recipes.all()[:(int(limit_recipes))]
        else:
            recipes = obj.recipes.all()
        context = {'request': request}
        return RecipeSerializer(recipes, many=True,
                                context=context).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeIngredientSerializer(ModelSerializer):
    """Серилизатор чтения рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    image = Base64ImageField()
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

    def get_ingredients(self):
        """Метод ингредиентов в рецепте."""
        ingredients = IngredientsInRecipe.ingredient_list.ingredient()
        serializer = RecipeIngredientSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        """
        Проверка на наличие рецепта в избранном.
        """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.favorites()

    def get_is_in_shopping_cart(self, obj):
        """
        Проверка на наличие рецепта в списке покупок.
        """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.shopping_user()


class IngredientsReadInRecipeSerializer(ModelSerializer):
    """Чтение ингредиентов в рецепте."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', required=False)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', required=False)

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeAddIngredientSerializer(ModelSerializer):
    """Серилизатор записи ингредиентов в рецепт."""

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')


class RecipeCreateorChangesSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all())
    ingredients = RecipeAddIngredientSerializer()
    image = Base64ImageField()

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

    @staticmethod
    def add_ingredients(ingredients, recipe):
        """Метод добавления ингредиентов в рецепт."""
        ingredient_list = [
            IngredientsInRecipe(recipe=recipe,
                                ingredient=ingredient['id'],
                                amount=ingredient['amount'],)
            for ingredient in ingredients]
        IngredientsInRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, author=author,
                                       **validated_data)
        self.add_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        IngredientsInRecipe.ingredient_list.recipe().delete()
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(
            instance.recipe,
            context=context
        ).data
