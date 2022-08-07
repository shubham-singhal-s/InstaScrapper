from scraper.insta_scraper import Scraper

if __name__ == "__main__":
    """
        target_username must fulfill either or both of the below two criteria:
        -> You must follow that account
        -> It must be an open account.
    """
    target_username = [
        ["macrophotography", 50],
        ["macroworld", 10000],
        ["macroawards", 1300],
        ["macro_creative_pictures", 10000],
        ["macro_globe", 10000],
    ]

    array = []
    for name in [target_username[2]]:
        try:
            # scraper = Scraper('yanverbao2021', '1202oabrevnay', name[0], name[1])
            # scraper = Scraper('thanhngocdo1120', 'yanverbao2021', name[0], name[1])
            # scraper = Scraper('chile.studyforlife', 'yanverbao2021', name[0], name[1])
            # scraper = Scraper('nqbao1340202', 'yanverbao2021', name[0], name[1])
            scraper = Scraper("ntramy03182021", "yanverbao2021", name[0], name[1])
            # scraper = Scraper("nqbao1993", "Randomint202?", name[0], name[1])
            # scraper = Scraper("briannguyen202", "Randomint202?", name[0], name[1])
        except:
            array.append(name)
            continue
