# Europe Incoming — FIT Data Layer

Master data repository for FIT package pricing and program definitions.

## Structure
```
data/
  hotel_rates_master.csv      # PPPN hotel rates by city
  transfer_rates_master.csv   # Airport/station transfer rates
  services_master.csv         # All services, trains, excursions (core + optional)
  markup.csv                  # Market markup factors by season
  exchange_rates.csv          # Currency conversion rates

packages/
  2.1_paris_switzerland.json  # One file per program
  ...

scripts/
  pricing_engine.py           # Calculates all price tables from package JSON + CSVs
```

## How it works
1. Update a rate in any CSV → push → all affected packages reprice on next build
2. Each package JSON defines the service list; prices are calculated at build time
3. The GitHub Pages portal reads generated prices — no manual PDF updates needed

## Pricing logic
- Hotel rates (PI): divide by 2 for per-person cost
- Service rates (PP): already per-person
- Service rates (PI): divide by 2 for per-person
- Private tours: vehicle cost divided by pax count
- Final price = cost × markup factor
- Child rate = twin rate × 0.416
