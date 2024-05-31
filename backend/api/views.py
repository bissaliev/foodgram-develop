from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from users.models import Subscribe

from .serializers import (
    CustomUserSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    SubscribeSerializer,
    TagSerializer,
)

User = get_user_model()


class ListRetrieveMixinViewSet(
    ListModelMixin, RetrieveModelMixin, GenericViewSet
):
    pass


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, url_path="subscriptions")
    def subscribe_list(self, request):
        users = request.user.subscriber.all()
        serializer = SubscribeSerializer(
            users, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["POST", "DELETE"])
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            Subscribe.objects.create(author=author, subscriber=request.user)
            serializer = SubscribeSerializer(author)
            return Response(serializer.data)
        Subscribe.objects.filter(
            author=author, subscriber=request.user
        ).delete()
        return Response(status="204")


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer

    # def perform_create(self, serializer):
    # serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeReadSerializer
        return RecipeCreateSerializer


class TagViewSet(ListRetrieveMixinViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveMixinViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
