from django.contrib import admin
from django.contrib.admin import display

from .models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = [
        'pk',
        'name',
        'color',
        'slug'
    ]
    search_fields = [
        'name',
        'color',
        'slug'
    ]


class IngredientsInRecipetline(admin.TabularInline):
    model = IngredientsInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'author',
        'total_favorites',
        'pub_date',
    ]
    inlines = [IngredientsInRecipetline]
    search_fields = [
        'name',
        'author',
    ]
    empty_value_display = '-empty-'

    @display(description='Счётчик добавлений в избранное')
    def total_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )


@admin.register(IngredientsInRecipe)
class RecipeingredinetAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'ingredient',
        'recipe',
    ]
    search_fields = [
        'ingredient',
        'recipe',
    ]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


admin.site.register(ShoppingCart)
