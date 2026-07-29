import re

def detect_response_language(question):
    """
    Detect the language requested by the user.
    Defaults to English.
    """

    q = question.lower()

    language_map = {
        "hindi": "Hindi",
        "english": "English",
        "italian": "Italian",
        "french": "French",
        "german": "German",
        "spanish": "Spanish",
        "telugu": "Telugu",
        "tamil": "Tamil",
        "kannada": "Kannada",
        "malayalam": "Malayalam",
        "marathi": "Marathi",
        "bengali": "Bengali",
        "gujarati": "Gujarati",
        "punjabi": "Punjabi",
        "urdu": "Urdu",
        "japanese": "Japanese",
        "chinese": "Chinese",
        "korean": "Korean"
    }

    for key, value in language_map.items():
        if re.search(rf"\b{key}\b", q):
            return value

    return "English"