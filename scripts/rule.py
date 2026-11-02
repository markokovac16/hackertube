import time

RECENT_DAYS = 1095
RISING_MIN = 5
MIN_SPREAD_DAYS = 60


def rising(r, min_rec, min_years):
    return (len(r["years"]) < min_years
            and r["recommenders"] >= RISING_MIN
            and r["threads"] >= RISING_MIN
            and r["first"] >= time.time() - RECENT_DAYS * 86400
            and r["last"] - r["first"] >= MIN_SPREAD_DAYS * 86400)


def qualifies(r, min_rec, min_years):
    if r["recommenders"] >= min_rec and len(r["years"]) >= min_years:
        return True
    return rising(r, min_rec, min_years)
