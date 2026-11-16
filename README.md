# Salinto (MVP)

A clear window into your next workplace. Salinto is a Philippine workplace
transparency platform where users can browse company reviews, salary
insights, and employment details before making a career decision.

This repository is the **Prelim Examination MVP**: the three required
screens (Login, Register, Home), built as independent Django apps
following **vertical slicing** rather than one big app with everything
mixed together.

## Vertical slicing structure

Instead of grouping all models together, all views together, etc.
(horizontal layering), each screen/feature owns its own end-to-end slice:

```
salinto_project/     # Project settings, root urls.py
accounts/             # Vertical slice: Login + Register + Logout
    forms.py          #   - RegisterForm, LoginForm
    views.py          #   - register_view, login_view, logout_view
    urls.py           #   - /login/, /register/, /logout/
dashboard/            # Vertical slice: Home screen
    views.py          #   - home_view (mock company data + search)
    urls.py            #   - / (home)
templates/
    base.html          # Shared layout (fonts, stylesheet, messages)
    accounts/
        login.html
        register.html
    dashboard/
        home.html
static/
    css/style.css      # Full design system (see below)
```

Each app is self-contained: its own views, urls, and templates. Adding a
future slice (e.g. a `reviews` app, a `companies` app) means adding a new
folder next to `accounts` and `dashboard`, not touching existing code.

## Design decisions (v2)

- **Concept**: the name "Salinto" plays on *salaming pinto* ("glass
  door"), the same idea behind "Glassdoor." Rather than an abstract
  glass effect, the visual signature is a **literal window-pane grid**
  (mullions and all) with warm light glowing through it — shown once,
  prominently, on the Login/Register screens.
- **Color**: light, warm palette — a linen background (`#f2efe8`), warm
  near-black text (`#2a2620`) instead of pure black, and a single
  desaturated orange accent (`#e0923c`) used consistently rather than
  multiple competing accent colors.
- **Type**: `Outfit` for headings (rounded, distinct) paired with
  `Plus Jakarta Sans` for body/UI text, loaded from Google Fonts.
  Deliberately avoids Inter, which is the most common default choice
  and reads as generic.
- **Layout**: auth screens use a split-screen layout (brand/window
  panel left, form right), collapsing to a stacked layout on mobile.
  Border-radius is intentionally varied across components (cards,
  buttons, tags) rather than using one uniform radius everywhere.
- **Depth**: shadows are tinted warm brown rather than flat black, and
  company cards lift slightly on hover to feel interactive rather than
  static.

## Mock data notice

The Home screen currently displays a small, hardcoded list of sample
companies (in `dashboard/views.py`) purely to demonstrate the intended
browsing/search experience. There is no real company or review database
yet — that is planned for a later slice once a `Company`/`Review` model
is introduced.

## How to run locally

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations (creates the local SQLite database)
python manage.py migrate

# 4. Run the development server
python manage.py runserver

# 5. Open in your browser
# http://127.0.0.1:8000/  -> redirects to /login/ if not logged in
```

Create a superuser if you want to access Django's admin panel
(`/admin/`):

```bash
python manage.py createsuperuser
```

## Screens

| Screen   | URL          | Notes                                             |
|----------|--------------|----------------------------------------------------|
| Login    | `/login/`    | Authenticates an existing user                     |
| Register | `/register/` | Creates a new account, logs the user in immediately|
| Home     | `/`          | Requires login; shows searchable sample companies  |

Logging out is available from the navbar on the Home screen and routes
to `/logout/`.
