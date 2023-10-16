#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

# Function to scrape the translation for a verse
def scrape_translation(verse_reference):
    url = f"https://www.biblegateway.com/passage/?search={verse_reference}&version=ADB1905"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
   # Check if the element with class "passage-text" exists
    passage_text = soup.find("div", class_="passage-text")
    
    if passage_text:
        # Find all <p> tags within the "passage-text" div and extract their text
        p_tags = passage_text.find_all("p")
        verse_text_parts = [p.get_text() for p in p_tags]
        
        # Concatenate the text parts to form the verse text
        verse_text = '\n'.join(verse_text_parts)
        
        return verse_text.strip()
    else:
        # Handle the case where the element is not found
        return "Translation not available"  # You can customize this message

# # Open the file and read the verse references
# with open('verses.txt', 'r') as file:
#   verse_references = [line.strip() for line in file.readlines()]
#   print("Verse References:")
#   print(verse_references)


 
while True:

    # Initialize the list of verses to scrape
    verses_to_scrape = []
    
    # Get the deck name interactively
    deck_name = input("Enter the name of the deck you want to add to: ")

    # Get input verses interactively
    verse_references = []
    while True:
        verse_reference = input("Enter a verse reference (e.g., John 3:16), or press Enter to finish: ")
        if not verse_reference:
            break
        verse_references.append(verse_reference)

    # Retrieve the translations and add them to the list
    for verse_reference in verse_references:
        translation = scrape_translation(verse_reference)
        verses_to_scrape.append({
            "verse": verse_reference,
            "translation": translation
        })

    # # Debugging: Print all the verses to scrape
    # for verse in verses_to_scrape:
    #     print(verse)

    # Now you can proceed to create flashcards with the retrieved translations
    for verse_data in verses_to_scrape:

        # Define the AnkiConnect API endpoint
        ANKI_CONNECT_URL = "http://localhost:8765"

        # Function to create an Anki deck if it doesn't exist
        def create_anki_deck(deck_name):
            data = {
                "action": "createDeck",
                "version": 6,
                "params": {
                    "deck": deck_name
                }
            }

            try:
                response = requests.post(ANKI_CONNECT_URL, json=data)
                response.raise_for_status()  # Raise an exception if the response is not OK
                print(f"Anki deck '{deck_name}' created successfully!")
            except requests.exceptions.RequestException as e:
                print(f"Failed to create Anki deck: {e}")

        # Check if the deck exists, and create it if it doesn't
        deck_exists = False
        deck_check_data = {
            "action": "deckNames",
            "version": 6,
        }

        try:
            response = requests.post(ANKI_CONNECT_URL, json=deck_check_data)
            response.raise_for_status()
            deck_names = response.json()
            if deck_name in deck_names:
                deck_exists = True
        except requests.exceptions.RequestException as e:
            print(f"Failed to check if deck '{deck_name}' exists: {e}")

        if not deck_exists:
            create_anki_deck(deck_name)

        # Function to create an Anki flashcard
        def create_anki_flashcard(deck_name, front, back):
            data = {
                "action": "addNote",
                "version": 6,
                "params": {
                    "note": {
                        "deckName": deck_name,
                        "modelName": "SFM",
                        "fields": {
                            "Front": front,
                            "Back": f'<div style="font-family: inherit;">{translation}</div>'
                            # Add inline CSS to match the font
                        },
                        "tags": []
                    }
                }
            }

            try:
                response = requests.post(ANKI_CONNECT_URL, json=data)
                response.raise_for_status()  # Raise an exception if the response is not OK
                print("Anki flashcard created successfully!")
            except requests.exceptions.RequestException as e:
                print(f"Failed to create Anki flashcard: {e}")

        # Iterate through each verse_data and create flashcards
        for verse_data in verses_to_scrape:
            verse = verse_data["verse"]
            translation = verse_data["translation"]
            print(f"Verse: {verse}")
            create_anki_flashcard(deck_name, verse, translation)

    continue_input = input("Do you want to continue (yes/no)? ").strip().lower()
    if continue_input != "yes":
        break
