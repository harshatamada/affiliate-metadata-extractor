import json

from bs4 import BeautifulSoup


def parse_jsonld(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    scripts = soup.find_all(
        "script",
        type="application/ld+json"
    )

    for script in scripts:

        try:

            data = json.loads(
                script.string
            )

            if (
                isinstance(data, dict)
                and
                data.get("@type")
                == "Product"
            ):

                return {
                    "name":
                    data.get("name"),

                    "description":
                    data.get("description"),

                    "image":
                    data.get("image"),

                    "price":
                    data.get("offers", {}).get("price"),
                }

        except:

            pass

    return None