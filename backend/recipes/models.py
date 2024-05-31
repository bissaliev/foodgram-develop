from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField("Наименование тега", max_length=200, unique=True)
    color = models.CharField("Цвет тега", max_length=7, unique=True)
    slug = models.SlugField("Slug", max_length=200, unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField("Наименование", max_length=200, db_index=True)
    measurement_unit = models.CharField("Единица измерения", max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        "Название",
        max_length=200,
    )
    image = models.ImageField("Картинка", upload_to="recipes/%Y/%m/%d")
    text = models.TextField("Описание рецепты")
    cooking_time = models.PositiveIntegerField(
        "Время приготовления",
        validators=[
            MinValueValidator(1, "Нужно указать время приготовления!")
        ],
    )
    tags = models.ManyToManyField(
        to=Tag, related_name="recipes", verbose_name="Теги"
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through="IngredientRecipe",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    pub_date = models.DateTimeField("", auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.author}"

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class IngredientRecipe(models.Model):
    """Промежуточная модель Ингредиенты-Рецепты."""

    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_recipes",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Ингредиент",
    )
    amount = models.IntegerField(
        "Количество",
        validators=[
            MinValueValidator(
                1, "Количество ингредиентов должно быть не менее 1!"
            )
        ],
    )

    def __str__(self):
        return f"{self.recipe}: {self.ingredient}({self.amount})"
