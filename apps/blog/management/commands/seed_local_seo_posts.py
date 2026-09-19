"""
Seeds the second batch of blog posts (local-SEO/AI-search angle).
Idempotent, same pattern as seed_launch_posts — matches on slug.

Usage:
    python manage.py seed_local_seo_posts
    python manage.py seed_local_seo_posts --status draft
"""
from django.core.management.base import BaseCommand

from apps.blog.models import Post

POSTS = [
    {
        "slug": "why-every-mvurwi-business-needs-a-website-2026",
        "title": "Why Every Mvurwi Business Needs a Website in 2026",
        "excerpt": "Mvurwi has grown fast — but most local businesses are still invisible online. Here's what that's actually costing you.",
        "body": """Mvurwi has changed. More butcheries, more beer outlets, more going on than a few years ago — growth that's easy to see just walking through town.

But here's the problem: most Mvurwi businesses are still invisible online.

#### 1. People Are Searching, Not Just Asking Around

When someone searches "farm inputs Mvurwi" or asks an AI assistant for a recommendation, those tools pull their answers from what's actually indexed on the web. A Facebook page mostly isn't part of that picture. If you only have a Facebook page, you're leaving that entire channel of potential customers to whoever *does* have a website — even if your business is genuinely better.

#### 2. Tobacco Season Brings Buyers From Out of Town

Buyers from Harare, South Africa, and Zambia often research before they travel — searching things like "auction floors Mvurwi" before making the trip. If you only have a Facebook page, there's a real chance they never find you before they arrive.

#### 3. Tenders and Suppliers Often Ask for a Website First

Banks, NGOs, and larger farm suppliers frequently expect a proper web presence before they'll consider working with a business — a Facebook page alone can read as less established, fairly or not.

#### 4. It's Cheaper Than Most People Assume

A proper .co.zw website now starts from **$25/year** with PHYB — domain and hosting included, no hidden fees. That's a small, predictable annual cost for something that represents your business every day it's live.

**What you get with PHYB:**

- Mobile-friendly site
- Built with SEO basics in place from day one
- WhatsApp button for orders
- You own it — unlike a Facebook page, nobody can suspend or delete it

Ready to put Mvurwi online? Visit https://phyb.co.zw/pricing/ — DM **"SIGNPOST"** to begin.""",
    },
    {
        "slug": "website-vs-facebook-page-zimbabwe",
        "title": "Website vs Facebook Page: What Zimbabwe Businesses Should Choose",
        "excerpt": "“Why can't I just use Facebook?” is the question I get most. Here's the honest comparison, not just a sales pitch.",
        "body": """"Why can't I just use Facebook?" is a question I get all the time. Here's the honest comparison.

| | Facebook Page | A Real Website |
|---|---|---|
| **Ownership** | Can be suspended or banned | You own it outright |
| **Search visibility** | Rarely indexed by Google/AI tools | Can be found on Google search |
| **What customers see** | Your posts alongside ads and competitors | Only your business |
| **Payments/bookings** | Awkward to do properly | Can be built in directly |
| **Credibility** | Can read as a side hustle | Reads as an established business |
| **Cost** | Free, but you're renting attention Meta controls | From $25/year, and you keep it |

#### The Part Most People Miss: AI Search Doesn't See Facebook the Same Way

When someone asks an AI assistant something like "best caterer in Harare," those tools are pulling from indexed web content — primarily websites, not social media posts. A Facebook-only business is largely invisible to that entire channel, which is only going to matter more as more people search this way.

#### What Facebook Is Actually Good For

Posting updates. Staying visible to people who already follow you. Building a sense of community around the brand.

#### What a Website Is Actually Good For

Getting found by *new* customers who don't already know you. Taking orders or payments properly. Looking established to anyone checking you out for the first time — a supplier, a bank, a stranger who just searched your name.

**The smart move is both.** Use Facebook to stay visible to people who already know you. Use a website to be found by the people who don't yet.

Get started from $25/year: Visit https://phyb.co.zw/pricing/ — DM **"SIGNPOST"** to begin.""",
    },
    {
        "slug": "how-to-get-customers-from-google-in-harare",
        "title": "How to Get Customers from Google in Harare",
        "excerpt": "Most Harare customers start their search on Google. If your business isn't there, someone else's is — here's how to fix that.",
        "body": """Most customers in Harare start their search on Google — "hair salon Harare," "wedding photographer Harare," and similar searches happen constantly. If you're not there, your competitor is.

#### Step 1: Get a Website

Google can't meaningfully rank a Facebook page the way it ranks an actual website with your business name, services, and location clearly laid out. This is the foundation — everything else below depends on it existing first.

#### Step 2: Use the Words People Actually Search

Put what people search for directly on your site — "Website Design Harare," "Wedding Photography Harare," whatever fits your business. Say specifically what you do and where, rather than only general phrases like "we are the best." Specific, searchable language is what actually gets matched to real searches.

#### Step 3: Make It Fast and Mobile-First

The large majority of searches in Zimbabwe happen on a phone. A site needs to load quickly and look right on a small screen, or people bounce before they even see what you offer.

#### Step 4: Add a WhatsApp Button

Make it one tap for someone to message you the moment they land on your site. That single detail is often the difference between a visitor and an actual inquiry.

PHYB builds all four of these in from the start — Signpost sites are live in 24–48 hours, full multi-page sites in 5–20 days depending on package.

Stop waiting only on referrals. Let Google bring customers to you as well.

Start here: Visit https://phyb.co.zw/pricing/ — DM **"SIGNPOST"** to begin.""",
    },
]

class Command(BaseCommand):
    help = "Seed (or update) the second batch of blog posts. Idempotent — matches on slug."

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            choices=["draft", "published"],
            default="published",
            help="Status to set on the posts (default: published). Use 'draft' to review before it goes live.",
        )

    def handle(self, *args, **options):
        status = options["status"]

        for entry in POSTS:
            post, created = Post.objects.update_or_create(
                slug=entry["slug"],
                defaults={
                    "title": entry["title"],
                    "excerpt": entry["excerpt"],
                    "body": entry["body"],
                    "status": status,
                },
            )
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{verb}: {post.title}"))

        self.stdout.write(self.style.SUCCESS(f"\nDone — {len(POSTS)} posts set to '{status}'."))
