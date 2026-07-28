AUTHOR = "Tommy Leonhardsen"
SITENAME = "wossname?"
SITEURL = ""

PATH = "content"
RELATIVE_URLS = True
STATIC_PATHS = ["images"]
TIMEZONE = "Europe/Oslo"
DEFAULT_LANG = "en"

THEME = "theme/wossname"

ARTICLE_URL = "{slug}.html"
ARTICLE_SAVE_AS = "{slug}.html"
DEFAULT_PAGINATION = False
DEFAULT_DATE_FORMAT = "%Y-%m-%d"

# Only the front page and the archive — no tag/category/author pages.
DIRECT_TEMPLATES = ["index", "archives"]
TAG_SAVE_AS = ""
TAGS_SAVE_AS = ""
CATEGORY_SAVE_AS = ""
CATEGORIES_SAVE_AS = ""
AUTHOR_SAVE_AS = ""
AUTHORS_SAVE_AS = ""

# Feeds are generated in publishconf.py only.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEVTO_PROFILE = "https://dev.to/tommy_leonhardsen_81d1f4e"
BOOKS_URL = "https://wossname-books.github.io/"
GITHUB_URL = "https://github.com/aweussom"
