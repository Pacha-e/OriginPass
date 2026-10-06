"""Pages that belong to the site itself rather than to any one app.

The landing page and the credits of the photographs it shows. They live here
rather than in `config` because `config` is configuration, and a page is not.

The error pages have no view: Django's own handlers render `403.html`, `404.html`
and `500.html` from the project template directory, and replacing them with
handlers of our own would add code whose only effect is to move three files.
"""

from django.shortcuts import render


def home(request):
    """The public landing page, reachable without an account."""
    return render(request, "pages/home.html")


#: The photographs shown in the interface and in the demonstration data. Each
#: one is under a free licence that asks for its author to be named, so they are
#: named here, on a page linked from every page.
PHOTO_CREDITS = [
    {
        "image": "img/crafts/sombrero.jpg",
        "subject": "Sombrero vueltiao",
        "author": "Hurluberlue",
        "licence": "CC BY-SA 4.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/4.0",
        "source": "https://commons.wikimedia.org/wiki/File:Sombrero_vueltiao_de_Colombia.jpg",
    },
    {
        "image": "img/passport-sample.jpg",
        "subject": "Sombrero vueltiao",
        "author": "Jdvillalobos",
        "licence": "Public domain",
        "licence_url": "",
        "source": "https://commons.wikimedia.org/wiki/File:Sombrero_vueltiao.jpg",
    },
    {
        "image": "img/crafts/mochila.jpg",
        "subject": "Mochila wayuu",
        "author": "Neima Paz",
        "licence": "CC BY-SA 4.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/4.0",
        "source": "https://commons.wikimedia.org/wiki/File:Wo%27olu.jpg",
    },
    {
        "image": "img/crafts/ceramica.jpg",
        "subject": "Cerámica de Ráquira",
        "author": "Cjaviersr",
        "licence": "CC BY-SA 4.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/4.0",
        "source": "https://commons.wikimedia.org/wiki/"
        "File:24_trabajo_en_cer%C3%A1mica_artesanal_en_R%C3%A1quira_Boyac%C3%A1.JPG",
    },
    {
        "image": "img/crafts/san-jacinto.jpg",
        "subject": "Artesanías de San Jacinto",
        "author": "San jacintero",
        "licence": "CC BY-SA 4.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/4.0",
        "source": "https://commons.wikimedia.org/wiki/File:Artesan%C3%ADa_san_jacinto.jpg",
    },
    {
        "image": "img/demo/antiguo-sombrero.jpg",
        "subject": "Sombrero vueltiao (datos de demostración)",
        "author": "Hurluberlue",
        "licence": "CC BY-SA 4.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/4.0",
        "source": "https://commons.wikimedia.org/wiki/File:Antiguo_sombrero_vueltiao.jpg",
    },
    {
        "image": "img/demo/hamaca.jpg",
        "subject": "Hamaca (datos de demostración)",
        "author": "Xemenendura",
        "licence": "CC BY-SA 3.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/3.0",
        "source": "https://commons.wikimedia.org/wiki/File:Hamacas_en_Los_Llanos.jpeg",
    },
    {
        "image": "img/demo/mochilas.jpg",
        "subject": "Mochilas wayuu (datos de demostración)",
        "author": "Alejandra Quintero Sinisterra",
        "licence": "CC BY 2.0",
        "licence_url": "https://creativecommons.org/licenses/by/2.0",
        "source": "https://commons.wikimedia.org/wiki/File:Mochilas_wayuu.png",
    },
]


def credits(request):
    """Who took each photograph, and under which licence it is shown."""
    return render(request, "pages/credits.html", {"credits": PHOTO_CREDITS})
