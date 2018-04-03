from lookup_downloader_mod.lookup_tables_downloader import * #pylint: disable=W0614
if __name__ == "__main__":
    d = check_if_exists()
    if not d[0]:
        pull_allCountries()
    if not d[1]:
        pull_shapes_all_low()