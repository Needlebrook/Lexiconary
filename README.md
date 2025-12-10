
# Lexiconary: A Book-Style Word Explorer 📚

> *CS50x Final Project by Celia Victor*

Video Demo: https://youtu.be/BcwUYVedf18

Lexiconary is a Flask-powered web application that brings together definitions, etymology, encyclopedia summaries, and historical usage data into one book-like interface.
It is designed to feel warm, readable, & “dictionary-like,” blending modern API integration with parchment-inspired styling.

## 📖 Features

### ✔ Full Flask Web Application

Built entirely using Python’s Flask framework, with clean routing, templates, modular code structure, and Bootstrap-based UI components.

### ✔ Search for Any Word

Users can type a word into the search bar and instantly retrieve:

* Definitions (dictionaryapi.dev)
* Phonetics & examples
* Wikipedia summaries
* Ngram usage frequency
* Etymology (parsed from Wiktionary)

### ✔ Multiple API Integrations

Lexiconary fetches data from:

* dictionaryapi.dev (definitions, phonetics, examples)
* Wiktionary (etymology Markdown parsed to readable text)
* Wikipedia REST API (encyclopedia summary)
* Google Books Ngram (usage frequency)

Each request includes robust exception handling.

### ✔ Error Handling

Graceful fallback messages when:

* Word not found
* API returns no data
* Parsing fails (e.g. Wiktionary HTML inconsistencies)
* Network/API rate-limit errors

The user always receives clear feedback instead of raw errors.

### ✔ Clean, Book-Like Output

Results are presented in distinct parchment-styled cards with:

* Drop caps
* Section ribbons
* Margin rules
* Soft page shadows
* Fully responsive mobile UI

### ✔ Some small flourishes

* Word of the Day banner on top
* Search history (local/session storage)
* Mobile-optimized layout
* Smooth scrolling to results

## 🖼 Screenshots

<img width="926" height="454" alt="Screenshot 2025-12-09 203315" src="https://github.com/user-attachments/assets/dfc7f996-cf50-4f5e-907a-fbe207469409" />
<img width="926" height="452" alt="Screenshot 2025-12-09 203126" src="https://github.com/user-attachments/assets/8e723b0e-ee21-44c5-bdb3-0caa53684744" />
<img width="923" height="365" alt="Screenshot 2025-12-09 203237" src="https://github.com/user-attachments/assets/979ac2b4-19b3-49c6-8c4e-f0834725711a" />
<img width="923" height="389" alt="Screenshot 2025-12-09 203150" src="https://github.com/user-attachments/assets/3870bc20-ef31-4959-a1ea-16116e8417e8" />
<img src="https://github.com/user-attachments/assets/b2063501-3243-4a8f-9479-21a23b9485dc" />

## 🛠 Technologies Used


- Python 3
- Flask (with Jinja2 Templates)
- HTML5 / CSS / Bootstrap 5
- JavaScript
- Chart.js (for Ngram chart)
- REST API integrations

## ▶️ How to Run Locally

1. Clone the repository

2. Install dependencies:
``` 
pip install -r requirements.txt
```
3. Start the Flask server:
```
flask run
```
4. Go to your browser:
``` 
http://127.0.0.1:5000 
```

