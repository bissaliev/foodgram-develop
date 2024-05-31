from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from users.models import Subscribe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    class Meta:
        fields = ("email", "id", "username", "first_name", "last_name")
        model = User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        model = User


class RecipeForSubscribeSerializer(ModelSerializer):
    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        model = Subscribe

    def get_is_subscribed(self, obj) -> bool:
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return request.user == obj.subscriber

    def get_recipes(self, obj):
        return RecipeForSubscribeSerializer(
            obj.author.recipes.all(), many=True
        ).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class IngredientRecipeSerializer(ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        fields = ("id", "name", "measurement_unit", "amount")
        model = IngredientRecipe


class IngredientRecipeCreateSerializer(ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        fields = ("id", "amount")
        model = IngredientRecipe


class TagSerializer(ModelSerializer):
    class Meta:
        fields = ("id", "name", "color", "slug")
        model = Tag


class IngredientSerializer(ModelSerializer):
    class Meta:
        fields = ("id", "name", "measurement_unit")
        model = Ingredient


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source="ingredient_recipes"
    )

    class Meta:
        fields = (
            "id",
            "author",
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        model = Recipe


class RecipeCreateSerializer(ModelSerializer):
    ingredients = IngredientRecipeCreateSerializer(
        many=True, source="ingredient_recipes"
    )
    image = Base64ImageField()

    class Meta:
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )
        model = Recipe

    def create_ingredients(self, ingredients, recipe):
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient.get("id")),
                amount=ingredient.get("amount"),
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredient_recipes")
        author = validated_data.pop("author")
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.pop("name", instance.name)
        instance.text = validated_data.pop("text", instance.text)
        instance.image = validated_data.pop("image", instance.image)
        instance.cooking_time = validated_data.pop(
            "cooking_time", instance.cooking_time
        )
        if "tags" in validated_data:
            instance.tags.set(validated_data.pop("tags"))
        if "ingredient_recipes" in validated_data:
            instance.ingredients.clear()
            self.create_ingredients(
                validated_data.pop("ingredient_recipes"), instance
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={"request": self.context.get("request")}
        ).data
