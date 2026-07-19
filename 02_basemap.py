#!/usr/bin/env python3
"""Genera el mapa base: PMTiles, buildings_index, roads (amb ponts/túnels) i pistes d'aeroport."""
import os
import multiprocessing


def main():
    from depot.maps import MapGen
    import config_bcn as C

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    obj = MapGen(
        city=C.CITY_CODE,
        bbox=C.BBOX,
        osmpbf="data/cataluna-latest.osm.pbf",
        outputdir=".",
        building_index_filter_size=20,
        building_tile_filter_size=20,
        building_index_simplification=1,
        building_tile_simplification=1,
        cities=C.LABEL_CITIES,
        suburbs=C.LABEL_SUBURBS,
        neighborhoods=C.LABEL_NEIGHBORHOODS,
        label_name_language=C.LABEL_LANGUAGE,
        road_name_preferred_language=C.ROAD_NAME_LANGUAGE,
        ncores=max(1, multiprocessing.cpu_count() - 1),
        RAM=8,
        cleanup_files=True,
    )

    obj.extract_base_data()
    obj.process_buildings()
    obj.process_roads_and_aeroways()
    obj.generate_pmtiles()
    obj.check_labels()
    obj.add_labels()

    print("\nMapa base generat a ./%s/" % C.CITY_CODE)


if __name__ == "__main__":
    # Imprescindible a macOS: multiprocessing usa 'spawn' i re-importa aquest
    # fitxer als processos fills; sense aquesta guarda ho re-executarien tot.
    main()
