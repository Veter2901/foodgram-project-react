from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import ShoppingCart
from users.models import User


def download_cart(request):
    user = get_object_or_404(User, username=request.user.username)
    user_cart = ShoppingCart.objects.filter(user=user)
    if not user_cart.exists():
        return Response(
            'В корзине нет товаров', status=status.HTTP_400_BAD_REQUEST)

    text = 'Список покупок:\n\n'
    ingredient_name = 'recipe__recipe__ingredient__name'
    ingredient_unit = 'recipe__recipe__ingredient__measurement_unit'
    recipe_amount = 'recipe__recipe__amount'
    amount_sum = 'recipe__recipe__amount__sum'
    cart = user_cart.select_related('recipe').values(
        ingredient_name, ingredient_unit).annotate(Sum(
            recipe_amount)).order_by(ingredient_name)
    for _ in cart:
        text += (
            f'{_[ingredient_name]} ({_[ingredient_unit]})'
            f' — {_[amount_sum]}\n'
        )
    response = HttpResponse(text, content_type='text/plain')
    filename = 'shopping_list.txt'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
