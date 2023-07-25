from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from rest_framework import permissions, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            IngredientsInRecipe,)
from .serializers import (IngredientSerializer,
                          TagSerializer,
                          RecipeSerializer,
                          FollowSerializer,
                          RecipeCreateorChangesSerializer,
                          RecipeIngredientSerializer,)
from .filters import FilterIngredient
from .permissions import IsAdminAuthorOrReadOnly, IsAdminOrReadOnly
from users.models import User, Follow
from .shop_list import shopp_list
from .pagination import SimplePagination


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated, ])
def follow_author(request, pk):
    """
    Подписка на автора.
    """
    user = get_object_or_404(User, username=request.user.username)
    author = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if user.id == author.id:
            content = {'errors': 'Нельзя подписаться на себя'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        try:
            Follow.objects.create(user=user, author=author)
        except IntegrityError:
            content = {'errors': 'Вы уже подписаны на данного автора'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        follows = User.objects.all().filter(username=author)
        serializer = FollowSerializer(
            follows,
            context={'request': request},
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        try:
            subscription = Follow.objects.get(user=user, author=author)
        except ObjectDoesNotExist:
            content = {'errors': 'Вы не подписаны на данного автора'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return HttpResponse('Вы успешно отписаны от этого автора',
                            status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для рецепта."""
    queryset = Recipe.objects.all()
    serializer_classes = {
        'retrieve': RecipeIngredientSerializer,
        'list': RecipeIngredientSerializer,
    }
    default_serializer_class = RecipeCreateorChangesSerializer
    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = SimplePagination

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action,
                                           self.default_serializer_class)

    def _favorite_shopping_post_delete(self, related_manager):
        recipe = self.get_object()
        if self.request.method == 'DELETE':
            related_manager.get(recipe_id=recipe.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if related_manager.filter(recipe=recipe).exists():
            raise ValidationError('Рецепт уже в избранном')
        related_manager.create(recipe=recipe)
        serializer = RecipeSerializer(instance=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'], )
    def favorite(self, request, pk=None):
        return self._favorite_shopping_post_delete(
            request.user.favorite
        )

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'], )
    def shopping_cart(self, request, pk=None):
        return self._favorite_shopping_post_delete(
            request.user.shopping_user
        )

    def download_shopping_cart(self, request):
        """Выгрузка списка покупок."""
        user = request.user
        if not user.shopping_user.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = IngredientsInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = shopp_list(ingredients=ingredients, user=user)
        return shopping_list


class IngredientViewSet(ModelViewSet):
    """Вьюсет для ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterIngredient


class TagViewSet(ModelViewSet):
    """Вьюсет для тэга."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
