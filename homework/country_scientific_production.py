import os
import pandas as pd
import folium


def load_affiliations():
    """Carga los datos de Scopus."""

    dataframe = pd.read_csv(
        (
            "https://raw.githubusercontent.com/jdvelasq/"
            "datalabs/master/datasets/scopus-papers.csv"
        )
    )

    return dataframe[["Affiliations"]]


def remove_na_rows(affiliations):
    """Elimina filas con valores nulos."""

    return affiliations.dropna(subset=["Affiliations"])


def add_countries_column(affiliations):
    """Extrae países de las afiliaciones."""

    affiliations = affiliations.copy()

    affiliations["countries"] = affiliations["Affiliations"].apply(
        lambda x: list(
            set(
                [
                    affiliation.split(",")[-1].strip()
                    for affiliation in x.split(";")
                ]
            )
        )
    )

    return affiliations


def clean_countries(affiliations):
    """Corrige nombres de países."""

    affiliations = affiliations.copy()

    affiliations["countries"] = affiliations["countries"].apply(
        lambda countries: [
            (
                "United States of America"
                if country == "United States"
                else country
            )
            for country in countries
        ]
    )

    return affiliations


def count_country_frequency(affiliations):
    """Cuenta frecuencia de países."""

    countries = affiliations["countries"].explode()

    countries = countries.value_counts()

    countries = countries.rename_axis("countries")

    countries = countries.reset_index(name="count")

    return countries


def plot_world_map(countries):
    """Genera mapa mundial."""

    world_map = folium.Map(
        location=[20, 0],
        zoom_start=2,
    )

    folium.Choropleth(
        geo_data=(
            "https://raw.githubusercontent.com/"
            "python-visualization/folium/master/"
            "examples/data/world-countries.json"
        ),
        data=countries,
        columns=["countries", "count"],
        key_on="feature.properties.name",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Scientific Production",
    ).add_to(world_map)

    world_map.save("files/map.html")


def make_worldmap():
    """Función principal."""

    os.makedirs("files/output", exist_ok=True)

    affiliations = load_affiliations()

    affiliations = remove_na_rows(affiliations)

    affiliations = add_countries_column(affiliations)

    affiliations = clean_countries(affiliations)

    countries = count_country_frequency(affiliations)

    countries.to_csv(
        "files/output/countries.csv",
        index=False,
    )

    plot_world_map(countries)


if __name__ == "__main__":
    make_worldmap()