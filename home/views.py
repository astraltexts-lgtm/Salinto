from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Mock data for the MVP home screen. In a later slice this will be replaced
# by a real Company model backed by user-submitted reviews.
SAMPLE_COMPANIES = [
    {
        'name': 'Bayanihan BPO Solutions',
        'industry': 'Business Process Outsourcing',
        'location': 'Cebu City',
        'rating': 4.2,
        'review_count': 58,
        'employment_types': ['Direct hire', 'Night differential'],
    },
    {
        'name': 'Lantawan Agri Corp',
        'industry': 'Agriculture',
        'location': 'Davao del Sur',
        'rating': 3.6,
        'review_count': 21,
        'employment_types': ['Direct hire', 'Seasonal'],
    },
    {
        'name': 'Tahanan Retail Group',
        'industry': 'Retail',
        'location': 'Quezon City',
        'rating': 2.9,
        'review_count': 94,
        'employment_types': ['Agency hired', 'Project based'],
    },
    {
        'name': 'Marino Logistics PH',
        'industry': 'Logistics & Freight',
        'location': 'Iloilo City',
        'rating': 4.5,
        'review_count': 37,
        'employment_types': ['Direct hire'],
    },
]


@login_required(login_url='login:login')
def home_view(request):
    """
    Home Screen slice: the first thing a Salinto user sees after logging in.

    For this MVP, the company list is static sample data used to
    demonstrate the intended browsing/search experience end to end.
    """
    query = request.GET.get('q', '').strip()

    companies = SAMPLE_COMPANIES
    if query:
        companies = [
            c for c in SAMPLE_COMPANIES
            if query.lower() in c['name'].lower() or query.lower() in c['industry'].lower()
        ]

    context = {
        'companies': companies,
        'query': query,
        'total_companies': len(SAMPLE_COMPANIES),
    }
    return render(request, 'home/home.html', context)
