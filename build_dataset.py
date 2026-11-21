"""
build_dataset.py
Downloads, cleans and merges the data for the ionosphere / CO2 / geomagnetic storm study.

Run:      python build_dataset.py
Needs:    pip install pandas numpy requests
Produces: a folder "ionosphere_data" containing
            raw/                the files exactly as downloaded (kept for the record)
            merged_daily.csv    one row per day, all variables
            summary.txt         what was downloaded, sanity checks, and day counts

Sources
  CO2        NOAA Global Monitoring Laboratory, Mauna Loa daily means
  Dst, F10.7 NASA OMNI2 hourly files (Dst there comes from WDC Kyoto)
  foF2, hmF2, TEC   GIRO DIDBase, Roquetes / Ebro Observatory, URSI code EB040

Every setting you might want to change is in the SETTINGS block below.
"""

import io
import os
import sys
import time
from datetime import date, datetime

import numpy as np
import pandas as pd
import requests

# ----------------------------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------------------------
OUT_DIR = "ionosphere_data"

DRIVER_START_YEAR = 1974      # CO2 and Dst start here (used in the time series)
IONO_START_YEAR = 1988        # Roquetes data start in 1988
END_YEAR = date.today().year  # up to the current year

STATION = "EB040"             # Roquetes, Ebro Observatory (40.8N, 0.5E)

# Ionosonde quality filter.
# CS = confidence score of the automatic scaling: 0-100, 999 = manually scaled,
# -1 = unknown. Records below MIN_CS are dropped. Set MIN_CS = None for no filter.
MIN_CS = 70
KEEP_UNKNOWN_CS = True        # keep records whose score is -1 (unknown)?

# CO2 changes slowly, so gaps of up to this many days are filled by drawing a
# straight line between the days on either side. Longer gaps are left empty.
CO2_MAX_GAP_DAYS = 14

# A day is kept only if at least this many of its 24 hours have a reading.
MIN_HOURS_PER_DAY = 18

# Start date of each solar cycle (month of sunspot minimum).
# CONFIRM THESE against the SILSO cycle table before the final run.
CYCLE_STARTS = {
    21: "1976-03-01",
    22: "1986-09-01",
    23: "1996-08-01",
    24: "2008-12-01",
    25: "2019-12-01",
}
# Cycle 25 has not ended, so its length is assumed. 11 years is the average cycle.
ASSUMED_CYCLE25_LENGTH_DAYS = 4018

CO2_URL = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_daily_mlo.csv"
OMNI_URL = "https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/omni2_{year}.dat"
# GIRO moved its data service in 2026; the old DIDBGetValues address now returns 404.
GIRO_URL = "https://lgdc.uml.edu/fastchar/getbest"
GIRO_PAUSE_SECONDS = 2        # wait between requests so the server does not block us
USER_AGENT = "ionosphere-co2-study/1.0 (research use; python-requests)"

# Position of each value in an OMNI2 hourly record (counting from 0).
OMNI_COL_DST = 40
OMNI_COL_F107 = 50
# ----------------------------------------------------------------------------

RAW_DIR = os.path.join(OUT_DIR, "raw")
LOG = []


def log(msg=""):
    print(msg)
    LOG.append(str(msg))


def fetch(url, save_as, retries=3, timeout=180, params=None, quiet=False):
    """Download url to raw/save_as (skipped if already there). Returns the text."""
    path = os.path.join(RAW_DIR, save_as)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            # 30 s to connect, `timeout` seconds to receive the file
            r = requests.get(url, params=params, timeout=(30, timeout),
                             headers={"User-Agent": USER_AGENT})
            if r.status_code == 429:  # server says: too many requests, slow down
                time.sleep(60 * attempt)
                last_error = "429 too many requests"
                continue
            r.raise_for_status()
            with open(path, "w", encoding="utf-8") as f:
                f.write(r.text)
            return r.text
        except Exception as e:  # network errors, timeouts, HTTP errors
            last_error = e
            time.sleep(5 * attempt)
    if not quiet:
        log(f"  !! could not download {save_as}: {last_error}")
    return None


def fetch_giro_year(year):
    """One year of soundings. Tries the whole year in one request; if the
    server refuses, asks month by month and joins the pieces."""
    name = f"giro_{STATION}_{year}.txt"
    path = os.path.join(RAW_DIR, name)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def query(start, end, save_as, quiet):
        params = {"ursiCode": STATION, "charName": "foF2,hmF2,TEC",
                  "fromDate": start, "toDate": end}
        text = fetch(GIRO_URL, save_as, timeout=600, params=params, quiet=quiet)
        time.sleep(GIRO_PAUSE_SECONDS)
        return text

    text = query(f"{year}/01/01 00:00:00", f"{year}/12/31 23:59:59", name, quiet=True)
    if text is not None:
        return text

    log(f"   {year}: whole-year request failed, trying month by month")
    parts = []
    for month in range(1, 13):
        last_day = (pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)).day
        piece = query(f"{year}/{month:02d}/01 00:00:00",
                      f"{year}/{month:02d}/{last_day} 23:59:59",
                      f"giro_{STATION}_{year}_{month:02d}.txt", quiet=False)
        if piece is None:
            log(f"  !! {year}: month {month:02d} failed, so {year} is incomplete. Run again later.")
            return None
        parts.append(piece)
    text = "\n".join(parts)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


# ----------------------------------------------------------------------------
# 1. CO2
# ----------------------------------------------------------------------------
def parse_co2(text):
    """NOAA daily file: comment lines start with '#'; then year, month, day,
    decimal date, CO2 in ppm."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p for p in line.replace(",", " ").split() if p]
        try:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            value = float(parts[-1])
        except (ValueError, IndexError):
            continue  # header line or malformed line
        if value <= 0:  # NOAA marks missing days with negative numbers
            continue
        rows.append((pd.Timestamp(year=y, month=m, day=d), value))
    df = pd.DataFrame(rows, columns=["date", "co2_ppm"]).drop_duplicates("date")
    return df.set_index("date").sort_index()


def fill_short_gaps(df):
    """Fill gaps of up to CO2_MAX_GAP_DAYS by straight-line interpolation.
    Adds a column co2_filled (True where the value was filled, not measured)."""
    df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="D"))
    df.index.name = "date"
    gap = df.co2_ppm.isna()
    gap_length = gap.groupby((~gap).cumsum()).transform("sum")
    straight_line = df.co2_ppm.interpolate(limit_area="inside")
    fill_here = gap & (gap_length <= CO2_MAX_GAP_DAYS)
    df.loc[fill_here, "co2_ppm"] = straight_line[fill_here]
    df["co2_filled"] = fill_here
    df = df.dropna(subset=["co2_ppm"])
    log(f"   filled {int(fill_here.sum())} days in gaps of up to {CO2_MAX_GAP_DAYS} days; "
        f"{int((gap & ~fill_here).sum())} days in longer gaps left empty")
    return df


def get_co2():
    log("1. CO2 (NOAA GML, Mauna Loa daily means)")
    text = fetch(CO2_URL, "co2_daily_mlo.csv")
    if text is None:
        return pd.DataFrame(columns=["co2_ppm"])
    df = parse_co2(text)
    df = df[df.index.year >= DRIVER_START_YEAR]
    if len(df):
        log(f"   {len(df)} measured days, {df.index.min().date()} to {df.index.max().date()}, "
            f"{df.co2_ppm.min():.1f} to {df.co2_ppm.max():.1f} ppm")
        df = fill_short_gaps(df)
    return df


# ----------------------------------------------------------------------------
# 2. Dst and F10.7 from OMNI2
# ----------------------------------------------------------------------------
def parse_omni(text):
    """OMNI2 hourly file: one line per hour, values separated by spaces."""
    rows = []
    for line in text.splitlines():
        p = line.split()
        if len(p) <= OMNI_COL_F107:
            continue
        try:
            y, doy, hr = int(p[0]), int(p[1]), int(p[2])
            dst = float(p[OMNI_COL_DST])
            f107 = float(p[OMNI_COL_F107])
        except ValueError:
            continue
        rows.append((y, doy, hr, dst, f107))
    df = pd.DataFrame(rows, columns=["y", "doy", "hr", "dst", "f107"])
    # fill values used by OMNI for missing data
    df.loc[df.dst.abs() >= 9999, "dst"] = np.nan
    df.loc[df.f107 >= 999, "f107"] = np.nan
    df["date"] = pd.to_datetime(df.y.astype(str), format="%Y") + pd.to_timedelta(df.doy - 1, unit="D")
    return df


def get_omni():
    log("2. Dst and F10.7 (NASA OMNI2 hourly files)")
    frames = []
    for year in range(DRIVER_START_YEAR, END_YEAR + 1):
        text = fetch(OMNI_URL.format(year=year), f"omni2_{year}.dat")
        if text:
            frames.append(parse_omni(text))
    if not frames:
        return pd.DataFrame()
    hourly = pd.concat(frames, ignore_index=True)

    g = hourly.groupby("date")
    daily = pd.DataFrame({
        "dst_mean": g.dst.mean(),      # average of the day's hourly values
        "dst_min": g.dst.min(),        # most disturbed hour of the day
        "dst_hours": g.dst.count(),    # how many hourly values the day has
        "f107": g.f107.mean(),
    })
    daily = daily[daily.dst_hours > 0]
    log(f"   {len(daily)} days with Dst, {daily.index.min().date()} to {daily.index.max().date()}")

    # Sanity checks against well-known storms. If these fail, the column
    # positions at the top of the script are wrong for this file version.
    checks = {"1989-03-14": -589, "2003-11-20": -422}
    for day, expected in checks.items():
        ts = pd.Timestamp(day)
        if ts in daily.index:
            got = daily.loc[ts, "dst_min"]
            ok = "OK" if abs(got - expected) <= 25 else "!! MISMATCH - check OMNI column positions"
            log(f"   check: minimum Dst on {day} = {got:.0f} nT (published about {expected}) {ok}")
    f = daily.f107.dropna()
    if len(f):
        ok = "OK" if 60 <= f.min() and f.max() <= 500 else "!! unexpected range - check OMNI column positions"
        log(f"   check: F10.7 range {f.min():.0f} to {f.max():.0f} {ok}")
    return daily


# ----------------------------------------------------------------------------
# 3. Ionosonde data from GIRO DIDBase
# ----------------------------------------------------------------------------
def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def parse_giro(text):
    """DIDBase text: comment lines start with '#'. Data lines are
    time, CS, then for each characteristic a value followed by a quality flag.
    Missing values are written as '---'."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.upper().startswith("ERROR"):
            continue
        p = line.split()
        if len(p) < 3 or not _is_number(p[1]):
            continue
        t = pd.to_datetime(p[0], errors="coerce", utc=True)
        if pd.isna(t):
            continue
        values = [x for x in p[2:] if x == "---" or _is_number(x)]
        if len(values) < 3:
            continue
        v = [np.nan if x == "---" else float(x) for x in values[:3]]
        rows.append((t.tz_localize(None), float(p[1]), v[0], v[1], v[2]))
    return pd.DataFrame(rows, columns=["time", "cs", "foF2", "hmF2", "TEC"])


def get_giro():
    log(f"3. foF2, hmF2, TEC (GIRO DIDBase, station {STATION})")
    frames = []
    for year in range(IONO_START_YEAR, END_YEAR + 1):
        text = fetch_giro_year(year)
        if not text:
            continue
        df = parse_giro(text)
        log(f"   {year}: {len(df)} soundings")
        if len(df):
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    s = pd.concat(frames, ignore_index=True).drop_duplicates("time").sort_values("time")
    total = len(s)
    log(f"   total soundings: {total}")
    log(f"   manually scaled (CS = 999): {(s.cs == 999).sum()}  "
        f"automatic: {((s.cs >= 0) & (s.cs <= 100)).sum()}  unknown: {(s.cs < 0).sum()}")

    # quality filter
    if MIN_CS is not None:
        keep = (s.cs >= MIN_CS)
        if KEEP_UNKNOWN_CS:
            keep |= (s.cs < 0)
        s = s[keep]
        log(f"   kept after quality filter (CS >= {MIN_CS}): {len(s)} of {total}")

    # physically impossible values are treated as missing
    s.loc[(s.foF2 <= 0) | (s.foF2 > 30), "foF2"] = np.nan
    s.loc[(s.hmF2 < 100) | (s.hmF2 > 800), "hmF2"] = np.nan
    s.loc[(s.TEC <= 0) | (s.TEC > 300), "TEC"] = np.nan

    # Step 1: average within each hour, so that years sampled every 5 minutes
    # and years sampled every 15 or 60 minutes are treated the same way.
    s["hour"] = s.time.dt.floor("h")
    hourly = s.groupby("hour")[["foF2", "hmF2", "TEC"]].mean()
    hourly["date"] = hourly.index.normalize()

    # Step 2: daily mean of the hourly means, only for days with enough hours.
    g = hourly.groupby("date")
    daily = pd.DataFrame(index=sorted(hourly.date.unique()))
    for name in ["foF2", "hmF2", "TEC"]:
        n = g[name].count()
        mean = g[name].mean()
        daily[name] = mean.where(n >= MIN_HOURS_PER_DAY)
        daily[f"{name}_hours"] = n
    daily.index.name = "date"
    for name in ["foF2", "hmF2", "TEC"]:
        log(f"   {name}: {daily[name].notna().sum()} days kept "
            f"(of {(daily[f'{name}_hours'] > 0).sum()} days with any reading)")
    return daily


# ----------------------------------------------------------------------------
# 4. Solar cycle phase
# ----------------------------------------------------------------------------
def add_solar_cycle_phase(df):
    starts = sorted((pd.Timestamp(v), k) for k, v in CYCLE_STARTS.items())
    df["solar_cycle"] = np.nan
    df["solar_cycle_phase"] = np.nan
    for i, (start, number) in enumerate(starts):
        if i + 1 < len(starts):
            end = starts[i + 1][0]
            length = (end - start).days
        else:  # the current, unfinished cycle
            end = pd.Timestamp.max
            length = ASSUMED_CYCLE25_LENGTH_DAYS
        in_cycle = (df.index >= start) & (df.index < end)
        df.loc[in_cycle, "solar_cycle"] = number
        df.loc[in_cycle, "solar_cycle_phase"] = (df.index[in_cycle] - start).days / length
    return df


# ----------------------------------------------------------------------------
def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    log(f"Run on {datetime.now():%Y-%m-%d %H:%M}")
    log(f"Settings: MIN_CS={MIN_CS}, MIN_HOURS_PER_DAY={MIN_HOURS_PER_DAY}, "
        f"cycle 25 length={ASSUMED_CYCLE25_LENGTH_DAYS} days")
    log()

    co2 = get_co2()
    log()
    omni = get_omni()
    log()
    giro = get_giro()
    log()

    merged = co2.join(omni, how="outer").join(giro, how="outer").sort_index()
    merged.index.name = "date"
    merged = add_solar_cycle_phase(merged)
    merged["year"] = merged.index.year

    out = os.path.join(OUT_DIR, "merged_daily.csv")
    merged.to_csv(out, float_format="%.4f")

    log("4. Merged table")
    log(f"   rows (days): {len(merged)}")
    drivers = ["co2_ppm", "dst_mean", "solar_cycle_phase"]
    have = [c for c in drivers if c in merged.columns]
    for name in ["TEC", "foF2", "hmF2"]:
        if name in merged.columns:
            n = merged[have + [name]].dropna().shape[0]
            log(f"   days usable for the {name} model (CO2, Dst, phase and {name} all present): {n}")
    if "f107" in merged.columns:
        log(f"   days with F10.7: {merged.f107.notna().sum()}")
    log()
    log("Days per year with each ionospheric parameter:")
    cols = [c for c in ["foF2", "hmF2", "TEC"] if c in merged.columns]
    if cols:
        log(merged.groupby("year")[cols].count().to_string())

    with open(os.path.join(OUT_DIR, "summary.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    log()
    log(f"Saved {out} and summary.txt")


if __name__ == "__main__":
    main()
