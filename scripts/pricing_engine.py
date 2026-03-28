import json, csv, os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_markup():
    rows = []
    with open(os.path.join(DATA_DIR, 'markup.csv')) as f:
        rows = list(csv.DictReader(f))
    return rows

def get_season(markup_rows, market, check_date):
    for row in markup_rows:
        if row['market'] != market: continue
        if row['date_start'] <= check_date <= row['date_end']:
            return row['season'], float(row['markup_factor'])
    return None, None

def price_regular_fit(pkg, star, market, season_label):
    markup_rows = load_markup()
    mu = next(float(r['markup_factor']) for r in markup_rows
              if r['market'] == market and r['season'] == season_label)

    hotel_cost = sum(h[f'rate_{star}star'] / 2 for h in pkg['hotels'])
    svc_cost = 0
    for day in pkg['variants']['regular_fit']['days']:
        for svc in day['services']:
            if svc['rate_type'] == 'PP':
                svc_cost += svc['rate']
            elif svc['rate_type'] == 'PI':
                svc_cost += svc['rate'] / 2

    total = hotel_cost + svc_cost
    twin   = round(total * mu, 3)
    single = round(total * mu * 2, 3)
    child  = round(twin * 0.416, 3)
    return {'single': single, 'twin': twin, 'child': child}

def price_private(pkg, star, market, season_label, pax):
    markup_rows = load_markup()
    mu = next(float(r['markup_factor']) for r in markup_rows
              if r['market'] == market and r['season'] == season_label)

    hotel_cost = sum(h[f'rate_{star}star'] / 2 for h in pkg['hotels'])
    vehicle_pp = pkg['variants']['private']['vehicle_cost']['rate'] / pax

    svc_cost = 0
    for day in pkg['variants']['private']['days']:
        for svc in day['services']:
            if svc['rate_type'] == 'PP':
                svc_cost += svc['rate']
            elif svc['rate_type'] == 'PI':
                svc_cost += svc['rate'] / pax

    total = hotel_cost + vehicle_pp + svc_cost
    return round(total * mu, 3)

def generate_price_tables(pkg_path):
    with open(pkg_path) as f:
        pkg = json.load(f)

    seasons = ['winter', 'summer']
    markets = ['Premium', 'Standard']
    stars   = ['3', '4']

    result = {'id': pkg['id'], 'title': pkg['title'], 'regular_fit': {}, 'private': {}}

    for market in markets:
        result['regular_fit'][market] = {}
        for season in seasons:
            result['regular_fit'][market][season] = {}
            for star in stars:
                result['regular_fit'][market][season][star] = price_regular_fit(pkg, star, market, season)

    if 'private' in pkg['variants'] and pkg['variants']['private'].get('vehicle_cost'):
        for market in markets:
            result['private'][market] = {}
            for season in seasons:
                result['private'][market][season] = {}
                for star in stars:
                    result['private'][market][season][star] = {}
                    for pax in pkg['variants']['private']['min_pax']:
                        result['private'][market][season][star][pax] = price_private(pkg, star, market, season, pax)

    return result

if __name__ == '__main__':
    import sys, json
    pkg_path = sys.argv[1] if len(sys.argv) > 1 else '../packages/2.1_paris_switzerland.json'
    tables = generate_price_tables(pkg_path)
    print(json.dumps(tables, indent=2))
