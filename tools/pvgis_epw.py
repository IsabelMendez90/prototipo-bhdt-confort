# coding: utf-8
"""Download a PVGIS Typical Meteorological Year as EPW and register it for the web page.

Adapted from the Ladybug Grasshopper component "LB Download PVGIS EPW" (J. I. Méndez).
Runs from the command line or from the GitHub Action in .github/workflows/epw.yml.

Example
    python tools/pvgis_epw.py --coords "25.6866, -100.3161" --name "Monterrey" --state "Nuevo Leon" --country "Mexico"
"""
import argparse, io, json, os, re, sys, unicodedata, urllib.request

PVGIS_API_URL = "https://re.jrc.ec.europa.eu/api/v5_3/tmy"
HERE = os.path.dirname(os.path.abspath(__file__))
EPW_DIR = os.path.join(HERE, "..", "epw")


def parse_coordinates(value):
    text = str(value).strip().replace("−", "-").replace("–", "-").replace("—", "-").replace(";", ",")
    nums = re.findall(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", text)
    if len(nums) != 2:
        raise ValueError("Enter exactly two coordinates as 'latitude, longitude'. Received %r" % value)
    lat, lon = float(nums[0]), float(nums[1])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Coordinates out of range")
    return lat, lon


def ascii_text(value):
    return "".join(c for c in unicodedata.normalize("NFKD", str(value or "")) if not unicodedata.combining(c))


def clean_field(value, default="-"):
    text = re.sub(r"\s+", " ", re.sub(r"[,;\r\n\t]+", " ", ascii_text(value))).strip()
    return text or default


def safe_filename(value):
    text = re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9._-]+", "_", ascii_text(value))).strip("._-")
    return text or "PVGIS_Location"


def download(lat, lon):
    url = "%s?lat=%.6f&lon=%.6f&usehorizon=1&outputformat=epw" % (PVGIS_API_URL, lat, lon)
    with urllib.request.urlopen(url, timeout=120) as r:
        data = r.read().decode("utf-8-sig", errors="replace")
    lines = data.splitlines(True)
    if not lines or not lines[0].upper().startswith("LOCATION,") or len(lines) < 8768:
        raise ValueError("PVGIS did not return a complete EPW. First line: %r" % (lines[0][:200] if lines else ""))
    return lines


def rewrite_location(lines, name, state, country, lat, lon):
    f = lines[0].rstrip("\r\n").split(",")
    tz, elev = f[8].strip(), f[9].strip()
    lines[0] = ",".join(["LOCATION", clean_field(name, "Custom Location"), clean_field(state), clean_field(country),
                         "PVGIS_TMY", "PVGIS", "%.6f" % lat, "%.6f" % lon, tz, elev]) + "\n"
    return lines


def register(name, filename):
    path = os.path.join(EPW_DIR, "index.json")
    items = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else []
    items = [i for i in items if i.get("file") != filename] + [{"name": name, "file": filename}]
    json.dump(items, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coords", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--state", default="")
    ap.add_argument("--country", default="")
    a = ap.parse_args()
    lat, lon = parse_coordinates(a.coords)
    lines = rewrite_location(download(lat, lon), a.name, a.state, a.country, lat, lon)
    os.makedirs(EPW_DIR, exist_ok=True)
    filename = safe_filename(a.name) + "_PVGIS_TMY.epw"
    with io.open(os.path.join(EPW_DIR, filename), "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)
    label = ", ".join([x for x in [a.name, a.state] if x]) + " (PVGIS TMY)"
    register(label, filename)
    print("Saved epw/%s" % filename)


if __name__ == "__main__":
    sys.exit(main())
