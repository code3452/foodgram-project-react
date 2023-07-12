from datetime import datetime

from django.http import HttpResponse


def shop_list(ingredients, user):
    today = datetime.today()
    shopp_list = (
        f'Дата: {today:%Y-%m-%d}\n\n'
        f'Покупки для: {user.get_full_name()}\n\n'
    )
    shopp_list += '\n'.join([
        f'- {ingredient["ingredient__name"]} '
        f'({ingredient["ingredient__measurement_unit"]})'
        f' - {ingredient["amount"]}'
        for ingredient in ingredients
    ])
    shopp_list += f'\n\nFoodgram ({today:%Y})'

    filename = f'{user.username}_shopp_list.txt'
    response = HttpResponse(shopp_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    return response
