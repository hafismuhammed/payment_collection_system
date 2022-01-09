import bitly_api
from django.conf import settings

def shoten_url(url):
    bitly = bitly_api.Connection(access_token=settings.BITLY_ACCESS_TOKEN)
    response = bitly.shorten(url)
    url = response['url']
    return url