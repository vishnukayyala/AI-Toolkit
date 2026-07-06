"""
============================================================
AI Toolkit — Flask Web Application
Author: Vishnu

INTERVIEW TALKING POINTS (what the interviewer will ask):

1. "What is Flask?"
   Flask is a lightweight Python web framework. It handles URL routing,
   runs a web server, and renders HTML templates. It's called a
   "micro-framework" because it gives you only what you need.

2. "How does routing work?"
   The @app.route() decorator maps a URL path to a Python function.
   When a user visits /search, Flask calls the search() function.

3. "What is Jinja2?"
   Jinja2 is Flask's templating engine. It lets you embed Python logic
   ({% for %}, {% if %}) inside HTML files to generate dynamic pages.

4. "What is template inheritance?"
   base.html defines the navbar and footer. Other templates use
   {% extends "base.html" %} to inherit this layout, avoiding repetition.

5. "Why Flask over Django?"
   Flask is simpler and beginner-friendly. Django is heavier and better
   for large projects. Flask is perfect for projects where you want
   full control with minimal complexity.
============================================================
"""

from flask import Flask, render_template, request, abort, url_for
from data import tools  # Import our tools list from data.py

# Create the Flask application instance
# __name__ tells Flask to look for templates/ and static/ folders
# relative to this file's location
app = Flask(__name__)


# ── CATEGORY EMOJI MAPPING ────────────────────────────────────
# Maps each category name to its display emoji.
# Stored as a constant (UPPER_CASE = convention for constants in Python).
CATEGORY_EMOJIS = {
    "Writing":          "✍️",
    "Coding":           "💻",
    "Image Generation": "🎨",
    "Video Generation": "🎬",
    "Productivity":     "⚡",
    "Research":         "🔬",
    "Marketing":        "📢",
    "Education":        "📚",
}


# ── CONTEXT PROCESSOR ─────────────────────────────────────────
# This runs automatically before EVERY template render.
# It injects 'categories' and 'emojis' into all templates globally,
# so we don't pass them manually in every render_template() call.
#
# INTERVIEW TIP: Think of this as "global variables for your templates."
# Without this, we'd have to write: render_template(..., categories=..., emojis=...)
# in every single route function — which is repetitive (DRY principle).
@app.context_processor
def inject_global_vars():
    return {
        "categories": get_all_categories(),
        "emojis": CATEGORY_EMOJIS,
    }


# ── CUSTOM JINJA2 FILTER ──────────────────────────────────────
# Adds a custom |rgba filter to Jinja2 templates.
# Usage in template: {{ tool.color | rgba(0.18) }}
# This converts "#10a37f" into "rgba(16, 163, 127, 0.18)"
# Used to create tinted logo backgrounds without JavaScript.
#
# INTERVIEW TIP: Custom filters are how you add Python utility functions
# that run inside Jinja2 templates. The @app.template_filter decorator
# registers the function as a usable filter.
@app.template_filter("rgba")
def hex_to_rgba(hex_color, alpha=0.20):
    """
    Convert a hex colour like '#10a37f' to 'rgba(16, 163, 127, 0.20)'.

    Steps:
    1. Strip the '#' prefix
    2. Read each pair of hex digits (R, G, B)
    3. Convert from base-16 to base-10 using int(value, 16)
    4. Return as an rgba() CSS string
    """
    hex_color = hex_color.lstrip("#")          # Remove the '#' symbol
    r = int(hex_color[0:2], 16)                # Bytes 0-1 → Red
    g = int(hex_color[2:4], 16)                # Bytes 2-3 → Green
    b = int(hex_color[4:6], 16)                # Bytes 4-5 → Blue
    return f"rgba({r}, {g}, {b}, {alpha})"


# ══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# These are plain Python functions — no Flask-specific code.
# They make our route functions clean and easy to read.
# INTERVIEW TIP: Separation of concerns — each function does one thing.
# ══════════════════════════════════════════════════════════════

def get_all_categories():
    """
    Returns a list of unique category names in the order they first appear.

    How it works:
    - `tool["category"] for tool in tools` is a generator that yields each category
    - dict.fromkeys() creates {category: None, ...} — dict keys are unique,
      so duplicates are automatically removed while preserving insertion order
    - list() converts the dict keys back to a list

    INTERVIEW TIP: dict.fromkeys() is better than set() here because
    sets don't preserve order, but dicts (Python 3.7+) do.
    """
    return list(dict.fromkeys(tool["category"] for tool in tools))


def get_trending_tools():
    """
    Returns all tools where trending == True.

    Uses a list comprehension: [expression for item in list if condition]
    This is the most Pythonic way to filter a list.

    INTERVIEW TIP: List comprehensions are faster than for loops + append()
    because they're optimised at the Python interpreter level.
    """
    return [tool for tool in tools if tool.get("trending") is True]


def search_tools(query):
    """
    Searches tools by name, category, or description (case-insensitive).
    Returns a list of matching tools.

    Steps:
    1. Convert query to lowercase (for case-insensitive matching)
    2. Loop through every tool
    3. Check if the query appears in name, category, or description
    4. Collect matches and return them

    INTERVIEW TIP: The 'in' operator checks for substring presence.
    "chat" in "chatgpt" → True. Combined with .lower(), this makes
    the search case-insensitive (user can type "ChatGPT" or "chatgpt").
    """
    if not query:
        return []  # Guard clause: return empty list for blank queries

    q = query.lower()  # Normalise to lowercase once, before the loop

    results = []
    for tool in tools:
        name_match        = q in tool["name"].lower()
        category_match    = q in tool["category"].lower()
        description_match = q in tool["description"].lower()

        # Collect tool if any field matches
        if name_match or category_match or description_match:
            results.append(tool)

    return results


def filter_by_category(category_name):
    """
    Returns all tools that belong to the given category.

    Simple list comprehension with an equality check.
    category_name must exactly match tool["category"].

    INTERVIEW TIP: This is O(n) — we scan every tool once.
    For a list of 53 tools this is perfectly fast.
    For millions of tools you'd use a database with an index.
    """
    return [tool for tool in tools if tool["category"] == category_name]


def get_tool_by_id(tool_id):
    """
    Finds and returns a single tool by its numeric ID.
    Returns None if no tool with that ID is found.

    Uses next() with a generator expression:
    - `(tool for tool in tools if tool["id"] == tool_id)` is a generator
      that yields matching tools one by one
    - next() takes the first item from that generator
    - The second argument to next() is the default value if the generator
      is empty (i.e., no match found) — here we default to None

    INTERVIEW TIP: This is safer than tools[tool_id - 1] because
    IDs might not be sequential. next() with a default never crashes.
    """
    return next((tool for tool in tools if tool["id"] == tool_id), None)


def group_by_category(tools_list):
    """
    Groups a list of tools into a dictionary keyed by category name.

    Example output:
        {
            "Writing":  [tool1, tool2, ...],
            "Coding":   [tool3, tool4, ...],
            ...
        }

    Uses setdefault(key, default):
    - If key exists in dict, returns its value
    - If key doesn't exist, sets it to default (empty list) then returns it
    - We then .append(tool) to the returned list

    INTERVIEW TIP: setdefault() is a cleaner alternative to:
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(tool)
    """
    grouped = {}
    for tool in tools_list:
        category = tool["category"]
        grouped.setdefault(category, []).append(tool)
    return grouped


# ══════════════════════════════════════════════════════════════
# ROUTES
# Each @app.route() maps a URL pattern to a Python function.
# The function runs when a browser visits that URL and must
# return HTML (via render_template) or a redirect.
# ══════════════════════════════════════════════════════════════

@app.route("/")
def home():
    """
    Homepage route — the Netflix-style browsing page.

    What it does:
    1. Fetches the featured tool (ChatGPT = Tool of the Day)
    2. Fetches the top 5 trending tools
    3. Groups all tools by category for the category rows
    4. Renders index.html with all this data
    """
    featured = get_tool_by_id(1)              # Tool of the Day: ChatGPT (id=1)
    trending = get_trending_tools()[:5]        # First 5 trending tools
    grouped  = group_by_category(tools)        # All tools grouped into categories

    # Compute hero background colour from the featured tool's brand colour.
    # We call our custom hex_to_rgba() function directly (not as a Jinja2 filter).
    hero_rgba = hex_to_rgba(featured.get("color", "#E50914"), 0.28)

    return render_template(
        "index.html",
        featured=featured,
        trending=trending,
        grouped=grouped,
        hero_rgba=hero_rgba,
    )


@app.route("/search")
def search():
    """
    Search results route — pure server-side filtering, no JavaScript.

    How it works:
    1. The search form in base.html submits to /search?q=chatgpt via GET
    2. request.args.get("q") reads the ?q= value from the URL
    3. Python's search_tools() filters the list
    4. Results are passed to the template

    INTERVIEW TIP: We use GET (not POST) for search because:
    - The query is visible in the URL (/search?q=chatgpt)
    - Users can bookmark/share search results
    - Refreshing the page re-runs the same search (no "re-submit form?" popup)
    """
    query   = request.args.get("q", "").strip()  # Read ?q= from URL, strip whitespace
    results = search_tools(query)                  # Filter in Python

    return render_template(
        "search_results.html",
        query=query,
        results=results,
        result_count=len(results),
    )


@app.route("/category/<category_name>")
def category(category_name):
    """
    Category filter route — shows all tools in one category.

    The <category_name> part of the URL becomes a function parameter.
    Example: GET /category/Writing → category_name = "Writing"

    INTERVIEW TIP: Flask's dynamic URL segments (<variable>) let you
    build clean, readable URLs. <int:tool_id> auto-converts to integer.
    <category_name> stays a string (the default type).
    """
    # Return 404 if the category doesn't exist in our data
    valid_categories = get_all_categories()
    if category_name not in valid_categories:
        abort(404)

    cat_tools = filter_by_category(category_name)
    emoji     = CATEGORY_EMOJIS.get(category_name, "🔧")

    return render_template(
        "category.html",
        category_name=category_name,
        cat_tools=cat_tools,
        emoji=emoji,
    )


@app.route("/tool/<int:tool_id>")
def tool_detail(tool_id):
    """
    Tool detail route — full-page detail view for a single tool.

    <int:tool_id> tells Flask to:
    1. Extract the value from the URL  (e.g. /tool/1 → tool_id = 1)
    2. Convert it to an integer automatically
    3. Return 404 automatically if the value can't be converted to int

    INTERVIEW TIP: Using a full page (instead of a modal) keeps the
    app simpler — no JavaScript needed for opening/closing a modal.
    It also makes every tool page shareable via URL.
    """
    tool = get_tool_by_id(tool_id)

    if tool is None:
        abort(404)  # Return HTTP 404 if tool ID doesn't exist

    # Related tools: same category, excluding the current tool, max 4
    related = [
        t for t in tools
        if t["category"] == tool["category"] and t["id"] != tool_id
    ][:4]

    return render_template(
        "tool_detail.html",
        tool=tool,
        related=related,
    )


# ── ERROR HANDLERS ────────────────────────────────────────────

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 error page — shown when a route doesn't match."""
    return render_template("404.html"), 404


# ── START THE SERVER ──────────────────────────────────────────

if __name__ == "__main__":
    # debug=True gives:
    # - Auto-reload when you save .py files (no need to restart manually)
    # - Detailed error pages in the browser (with the Python traceback)
    # IMPORTANT: Always set debug=False before deploying to production
    print("=" * 50)
    print("  AI Toolkit is running!")
    print("  Open: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)
