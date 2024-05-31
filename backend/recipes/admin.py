from django.contrib import admin

from .models import Ingredient, IngredientRecipe, Recipe, Tag

admin.site.register(Ingredient)
admin.site.register(Tag)


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInline,)
