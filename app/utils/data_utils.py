import json
import os

DATA_PATH = "app/data/countries.json"

def load_countries():
    base_path = "app/data/countries.json"
    meta_path = "app/data/countries_metadata.json"
    lang_path = "app/data/countrieslanguage.json"
    
    if not os.path.exists(base_path):
        return []
        
    with open(base_path, 'r') as f:
        base_data = json.load(f).get("results", [])
        
    # Load metadata
    metadata = {}
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta_list = json.load(f)
            metadata = {m["country"].lower(): m for m in meta_list}
            
    # Load languages
    languages = {}
    if os.path.exists(lang_path):
        with open(lang_path, 'r') as f:
            lang_list = json.load(f)
            languages = {l["country_name"].lower(): l["languages"] for l in lang_list}
            
    # Merge
    for country in base_data:
        name = country.get("country_name", "").lower()
        
        # Add metadata (Landscape, FloraFauna, seasons)
        if name in metadata:
            country.update(metadata[name])
            
        # Add languages
        if name in languages:
            country["official_languages"] = languages[name]
            
    return base_data

def search_countries(query_text=None, filters=None):
    """
    Search countries based on a text query and/or specific field filters.
    filters: dict of field_name: value (e.g., {"region": "Asia"})
    """
    countries = load_countries()
    results = []
    
    for country in countries:
        # Check filters first
        match = True
        if filters:
            for key, value in filters.items():
                if key not in country:
                    match = False
                    break
                
                country_val = country.get(key)
                if isinstance(country_val, str):
                    if str(value).lower() not in country_val.lower():
                        match = False
                        break
                elif country_val != value:
                    # For numbers or exact matches
                    if isinstance(country_val, (int, float)) and isinstance(value, (int, float)):
                        # Handle basic comparisons if value is a string like ">500"
                        pass # basic equality for now
                    elif country_val != value:
                        match = False
                        break
        
        if not match:
            continue
            
        # Check keyword search across all fields if query_text is provided
        if query_text:
            found_keyword = False
            # Search in a few key fields for performance and relevance
            searchable_text = f"{country.get('country_name', '')} {country.get('capital', '')} {country.get('region', '')} {country.get('subregion', '')}"
            if query_text.lower() in searchable_text.lower():
                found_keyword = True
            
            if not found_keyword:
                continue
                
        results.append(country)
        
    return results

def filter_countries(region=None, min_population=None, max_population=None, languages=None):
    countries = load_countries()
    filtered = []
    
    for country in countries:
        # Check region
        if region and country.get("region", "").lower() != region.lower():
            continue
            
        # Check population
        pop = country.get("population", 0)
        if min_population is not None and pop < min_population:
            continue
        if max_population is not None and pop > max_population:
            continue
            
        filtered.append(country)
        
    return filtered

def get_country_by_name(name):
    countries = load_countries()
    for country in countries:
        if country.get("country_name", "").lower() == name.lower():
            return country
    return None

if __name__ == "__main__":
    # Example test
    asia_large = filter_countries(region="Asia", min_population=500000000)
    print(f"Found {len(asia_large)} countries in Asia with > 50cr population")
    for c in asia_large:
        print(f"- {c['country_name']}: {c['population']}")
