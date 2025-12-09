from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import re
import datetime


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

def normalize_dict_api(data):
    if isinstance(data, list) and data:
        return data[0]            
    if isinstance(data, dict):
        return data
    return {}                    

def extract_ipa(phonetics):
    for entry in phonetics:
        ipa = entry.get("text")
        if ipa:
            return ipa  
    return None

WORD_LIST = [
    {"word": "serendipity", "definition": "the occurrence of events by chance in a happy way"},
    {"word": "ephemeral", "definition": "lasting for a very short time"},
    {"word": "mellifluous", "definition": "sweet or musical; pleasant to hear"},
    {"word": "sonder", "definition": "the realization that each passerby has a life as vivid as your own"},
    {"word": "luminous", "definition": "bright or shining, especially in the dark"},
    {"word": "petrichor", "definition": "the pleasant smell that accompanies the first rain after dry weather"},
    {"word": "ethereal", "definition": "extremely delicate and light in a way that seems not of this world"},
    {"word": "effervescent", "definition": "vivacious and enthusiastic; bubbling with excitement"},
    {"word": "limerence", "definition": "the state of being infatuated with another person"},
    {"word": "susurrus", "definition": "whispering, murmuring, or rustling"},
    {"word": "ineffable", "definition": "too great or extreme to be expressed in words"},
    {"word": "lacuna", "definition": "an unfilled space or interval; a gap"},
    {"word": "diaphanous", "definition": "light, delicate, and translucent"},
    {"word": "halcyon", "definition": "denoting a period of time in the past that was idyllically happy and peaceful"},
    {"word": "opalescent", "definition": "showing varying colors as an opal does"},
    {"word": "verdant", "definition": "green with grass or other rich vegetation"},
    {"word": "resplendent", "definition": "attractive and impressive through being richly colorful or sumptuous"},
    {"word": "imbroglio", "definition": "an extremely confused, complicated, or embarrassing situation"},
    {"word": "cacophony", "definition": "a harsh, discordant mixture of sounds"},
    {"word": "redolent", "definition": "strongly reminiscent or suggestive of something"},
    {"word": "languid", "definition": "displaying or having a disinclination for physical exertion"},
    {"word": "peregrination", "definition": "a long journey, especially on foot"},
    {"word": "obfuscate", "definition": "to make something obscure, unclear, or unintelligible"},
    {"word": "quintessential", "definition": "representing the most perfect example of a quality or class"},
    {"word": "ebullient", "definition": "cheerful and full of energy"},
    {"word": "penumbra", "definition": "the partially shaded outer region of a shadow"},
    {"word": "vicissitude", "definition": "a change of circumstances or fortune, typically one that is unwelcome"},
    {"word": "crepuscular", "definition": "of, resembling, or relating to twilight"},
    {"word": "proclivity", "definition": "a tendency to choose or do something regularly; an inclination"},
    {"word": "zeitgeist", "definition": "the defining spirit or mood of a particular period of history"}
]

def get_word_of_the_day():
    today = datetime.date.today()
    index = today.toordinal() % len(WORD_LIST)
    return WORD_LIST[index]

def get_dictionaryapi_definitions(term):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()

        # CASE 1 if valid response is a LIST
        if isinstance(data, list) and len(data) > 0:
            entry = data[0]  # first item
            phonetics = entry.get("phonetics", [])
            meanings = entry.get("meanings", [])
            definitions = []
            for m in meanings:
                for d in m.get("definitions", []):
                    definitions.append({
                        "partOfSpeech": m.get("partOfSpeech"),
                        "definition": d.get("definition"),
                        "example": d.get("example")
                    })

            return {
                "phonetics": phonetics,
                "definitions": definitions
            }
        # CASE 2 if dictionary API error (dict)
        elif isinstance(data, dict):
            return {
                "phonetics": [],
                "definitions": [],
                "error": data.get("message", "No definition found")
            }
        # Unknown format
        return {
            "phonetics": [],
            "definitions": []
        }

    except Exception as e:
        print("DICTIONARY API ERROR:", e)
        return {
            "phonetics": [],
            "definitions": []
        }

def fetch_wiktionary(word):
    url = "https://en.wiktionary.org/w/api.php"
    params = {
        "action": "parse",
        "page": word,
        "prop": "wikitext",
        "format": "json"
    }
    headers = {
        "User-Agent": "WordExplorer/1.0 (contact: celiavictor101@gmail.com)",
        "Accept": "application/json"
    }

    resp = requests.get(url, params=params, headers=headers)

    print("Status:", resp.status_code)
    print("BODY:", resp.text[:500], "...")

    #check for JSON
    try:
        data = resp.json()
    except Exception:
        print("WIKTIONARY ERROR: Could not decode JSON")
        return None

    #wikitext
    try:
        return data["parse"]["wikitext"]["*"]
    except KeyError:
        print("WIKTIONARY: No wikitext found")
        return None

def extract_etymology_from_dictapi(entry):
    """DictionaryAPI sometimes provides 'origin'. Try extracting it."""
    if not entry:
        return None
    
    # case if "origin" field
    origin = entry.get("origin")
    if origin:
        return origin

    meanings = entry.get("meanings", [])
    for m in meanings:
        for d in m.get("definitions", []):
            if "etymology" in d:
                return d["etymology"]
            if "origin" in d:
                return d["origin"]
    
    return None

def parse_etymology_minimal(wikitext):
    if not wikitext:
        return None
    sections = re.split(r"^==\s*(.*?)\s*==\s*$", wikitext, flags=re.MULTILINE)
    english_text = None

    for i in range(1, len(sections), 2):
        if sections[i].strip().lower() == "english":
            english_text = sections[i + 1]
            break

    if not english_text:
        return None

    parts = re.split(r"^===\s*(.*?)\s*===\s*$", english_text, flags=re.MULTILINE)
    ety_block = None

    for i in range(1, len(parts), 2):
        if parts[i].strip().lower().startswith("etymology"):
            ety_block = parts[i + 1]
            break

    if not ety_block:
        return None

    # ---- CLEANING SECTION ----
    while True:
        new = re.sub(r"\{\{[^{}]*\}\}", "", ety_block)
        if new == ety_block:
            break
        ety_block = new

    ety_block = re.sub(r"\[\[[^\|\]]*\|([^\]]+)\]\]", r"\1", ety_block)
    ety_block = re.sub(r"\[\[([^\]]+)\]\]", r"\1", ety_block)

    # 5. Remove HTML tags <ref>...</ref>, <span>, <i>, <b>, etc.
    ety_block = re.sub(r"<ref[^>]*>.*?</ref>", "", ety_block, flags=re.DOTALL)
    ety_block = re.sub(r"<.*?>", "", ety_block)

    # 6. Remove leftover punctuation junk and whitespace
    ety_block = re.sub(r"\s+", " ", ety_block).strip(" ,.:;")

    return ety_block if ety_block else None

def get_etymology(wikitext):
    clean = parse_etymology_minimal(wikitext)

    if clean and len(clean) > 10:
        return clean

    if wikitext:
        m = re.search(r"===Etymology===([\s\S]*?)(===|$)", wikitext)
        if m:
            raw = m.group(1)

            # Remove templates like {{der|...}}
            raw = re.sub(r"\{\{[^{}]+\}\}", "", raw)

            # Remove HTML tags
            raw = re.sub(r"<.*?>", "", raw)

            # Remove wikilinks [[word|display]] / [[word]]
            raw = re.sub(r"\[\[[^\|\]]*\|([^\]]+)\]\]", r"\1", raw)
            raw = re.sub(r"\[\[([^\]]+)\]\]", r"\1", raw)

            # Normalize whitespace
            raw = re.sub(r"\s+", " ", raw).strip()

            if len(raw) > 10:
                return "(Simplified extract) " + raw[:300] + "..."

    return "Etymology unavailable or too complex to parse."

def combine_etymologies(dictapi_ety, wiki_ety):
    """
    Combine DictionaryAPI + Wiktionary etymology cleanly.
    """
    parts = []

    if dictapi_ety:
        parts.append(dictapi_ety.strip())

    if wiki_ety:
        if not dictapi_ety or wiki_ety.strip() not in dictapi_ety:
            parts.append(wiki_ety.strip())

    if not parts:
        return "Etymology unavailable."

    return " | ".join(parts)

def get_combined_etymology(word):
    sources = []
    wikitext = fetch_wiktionary(word)
    if wikitext:
        parsed = parse_etymology_minimal(wikitext)
        if parsed:
            sources.append(f"**Wiktionary:** {parsed}")
    dict_data = get_dictionaryapi_definitions(word)
    dictapi_origin = extract_etymology_from_dictapi(normalize_dict_api(dict_data))
    if dictapi_origin:
        sources.append(f"**DictionaryAPI:** {dictapi_origin}")

    if not sources:
        return None

    return "\n\n".join(sources)



def get_wikipedia_summary(word):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{word}"
    headers = {
    "User-Agent": "WordExplorer/1.0 (contact: celiavictor101@gmail.com)",
    "Accept": "application/json"
    }

    print("\n--- WIKIPEDIA RAW RESPONSE ---")
    print("URL:", url)

    try:
        r = requests.get(url, headers=headers, timeout=8)

        print("Status:", r.status_code)

        if r.status_code != 200:
            print("WIKI: Non-200 response, skipping.")
            return None

        data = r.json()
        return {
            "extract": data.get("extract", None),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", None)
        }

    except Exception as e:
        print("WIKIPEDIA ERROR:", e)
        return None



def get_ngram_usage(word):
    """Try to fetch Google Ngram JSON. Best-effort. Returns list of {year, freq}."""
    url = ("https://books.google.com/ngrams/json"
           f"?content={requests.utils.quote(word)}&year_start=1800&year_end=2019&corpus=26&smoothing=3")
    try:
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            return []
        data = r.json()  
        if not data:
            return []
        series = data[0]
        timeseries = series.get("timeseries", [])
        years = list(range(1800, 2020))
        points = [{"year": y, "freq": f} for y, f in zip(years, timeseries)]
        return points
    except Exception:
        return []


@app.route("/", methods=["GET", "POST"])
def index():
    word_of_the_day = get_word_of_the_day()
    if request.method == "POST":
        q = request.form.get("q", "").strip()
        if q == "":
            return render_template("index.html", error="Please enter a word.", word_of_the_day=word_of_the_day)
        return redirect(url_for("word_page", term=q))
    return render_template("index.html", word_of_the_day=word_of_the_day)

@app.route("/word/<term>")
def word_page(term):
    term = term.strip()
    if not term:
        return redirect(url_for("index"))

    dictapi = get_dictionaryapi_definitions(term)
    dictapi_ety = extract_etymology_from_dictapi(dictapi)

    wikitext = fetch_wiktionary(term)
    wiki_ety = get_etymology(wikitext) if wikitext else None
    etymology = combine_etymologies(dictapi_ety, wiki_ety)

    wiki = get_wikipedia_summary(term)

    ngram = get_ngram_usage(term)

    # Phonetics
    phonetic_list = dictapi.get("phonetics", [])
    phonetic = phonetic_list[0].get("text") if phonetic_list else None
    for p in phonetic_list:
        if p.get("text"):
            phonetic = p["text"]
            break
    #template 
    payload = {
        "term": term,
        "phonetic": phonetic,
        "definitions": dictapi.get("definitions", [])[:6],
        "wikipedia": wiki,
        "etymology": etymology,
        "ngram": ngram,
        "word_of_the_day": get_word_of_the_day()
    }

    return render_template("word.html", **payload)



if __name__ == "__main__":
    app.run(debug=True)
