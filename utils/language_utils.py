# Map of language names to ISO 639-1 codes
LANGUAGE_CODES = {
    "English": "en",
    "Mandarin Chinese": "zh",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "Arabic": "ar",
    "Bengali": "bn",
    "Russian": "ru",
    "Portuguese": "pt",
    "Japanese": "ja",
    "German": "de",
    "Indonesian": "id",
    "Urdu": "ur",
    "Turkish": "tr",
    "Vietnamese": "vi",
    "Korean": "ko",
    "Italian": "it",
    "Punjabi": "pa",
    "Telugu": "te",
    "Tamil": "ta",
    "Swahili": "sw",
    "Malay": "ms",
    "Thai": "th",
    "Persian (Farsi)": "fa",
    "Ukrainian": "uk",
    "Finnish": "fi",
    "Swedish": "sv",
    "Dutch": "nl",
    "Greek": "el",
    "Polish": "pl",
    "Romanian": "ro",
    "Czech": "cs",
    "Bulgarian": "bg",
    "Danish": "da",
    "Norwegian": "no",
    "Hebrew": "he",
    "Hungarian": "hu",
    "Slovak": "sk",
    "Lithuanian": "lt",
    "Slovenian": "sl",
    "Latvian": "lv",
    "Estonian": "et",
    "Maltese": "mt",
    "Albanian": "sq",
    "Croatian": "hr",
    "Serbian": "sr",
    "Macedonian": "mk",
    "Bosnian": "bs",
    "Mongolian": "mn",
    "Kazakh": "kk",
    "Azerbaijani": "az",
    "Georgian": "ka",
    "Armenian": "hy",
    "Nepali": "ne",
    "Sinhala": "si",
    "Khmer": "km",
    "Lao": "lo",
    "Burmese": "my",
    "Tagalog": "tl",
    "Cebuano": "ceb",
    "Maori": "mi",
    "Hawaiian": "haw",
    "Samoan": "sm",
    "Fijian": "fj",
    "Tongan": "to",
    "Welsh": "cy",
    "Irish": "ga",
    "Scottish Gaelic": "gd",
    "Basque": "eu",
    "Catalan": "ca",
    "Galician": "gl",
    "Corsican": "co",
    "Haitian Creole": "ht",
    "Esperanto": "eo",
    "Latin": "la",
    "Luxembourgish": "lb",
    "Frisian": "fy",
    "Icelandic": "is",
    "Amharic": "am",
    "Somali": "so",
    "Malagasy": "mg",
    "Zulu": "zu",
    "Xhosa": "xh",
    "Yoruba": "yo",
    "Igbo": "ig",
    "Hausa": "ha",
    "Chichewa": "ny",
    "Shona": "sn",
    "Kinyarwanda": "rw",
    "Kurdish": "ku",
    "Pashto": "ps",
    "Tajik": "tg",
    "Turkmen": "tk",
    "Uzbek": "uz",
    "Kyrgyz": "ky",
    "Hmong": "hmn",
    "Māori": "mi",
    "Yiddish": "yi",
    "Sindhi": "sd",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Odia": "or",
    "Assamese": "as"
}

# Reverse map for looking up names from codes
LANGUAGE_NAMES = {code: name for name, code in LANGUAGE_CODES.items()}


def get_language_list():
    """Get a list of all supported language names."""
    return sorted(LANGUAGE_CODES.keys())


def get_language_code(language_name):
    """Get the ISO 639-1 code for a language name."""
    return LANGUAGE_CODES.get(language_name, "en")  # Default to English


def get_language_name(language_code):
    """Get the language name for an ISO 639-1 code."""
    return LANGUAGE_NAMES.get(language_code, "English")  # Default to English


def is_valid_language(language_name):
    """Check if a language name is supported."""
    return language_name in LANGUAGE_CODES
