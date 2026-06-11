from bs4 import BeautifulSoup


def parse_opengraph(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    data = {}

    tags = {
        "title": "og:title",
        "description": "og:description",
        "image": "og:image",
        "type": "og:type"
    }

    for key, value in tags.items():

        tag = soup.find(
            "meta",
            property=value
        )

        if tag:

            data[key] = tag.get(
                "content"
            )

    return data
    