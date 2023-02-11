from scraper.insta_scraper import Scraper

if __name__ == "__main__":
    # target_username must fulfill either or both of the below two criteria:
    # -> You must follow that account
    # -> It must be an open account.
    target_username = [
        ["puppy", 20, "search"],
        # ["Mount everest", 500, "search"],
        # ["mountamadablam", 450, "hash"],
        # ["mountannapurna", 1200, "hash"],
        # ["patagoniamountains", 600, "hash"],
        # ["antarcticmountains", 70, "hash"],
        # ["himalayamountains", 4000, "hash"],
    ]

    array = []
    for name in target_username:
        try:
            # scraper = Scraper('yanverbao2021', '1202oabrevnay', name[0], name[1])
            # scraper = Scraper('thanhngocdo1120', 'yanverbao2021', name[0], name[1])
            # scraper = Scraper('chile.studyforlife', 'yanverbao2021', name[0], name[1])
            # scraper = Scraper('nqbao1340202', 'yanverbao2021', name[0], name[1])
            # scraper = Scraper(
            #     "ntramy03182021", "yanverbao2021", name[0], name[1], name[2]
            # )
            # scraper = Scraper("nqbao1993", "Randomint202?", name[0], name[1])
            scraper = Scraper(
                "briannguyen202", "Randomint202?", name[0], name[1], name[2]
            )
        except Exception as e:
            array.append(name)
            print("Error occured while parsing for tag {}".format(name[0]), e)
            continue

    # if len(array) > 0:
    #     print("Errors occured for: \n" + "\n".join(array))
