"""
Seeds the three launch blog posts. Idempotent: matches on slug, so running
this again after editing the content below updates the existing posts
in place rather than creating duplicates.

Usage:
    python manage.py seed_launch_posts
    python manage.py seed_launch_posts --status draft   # review before publishing
"""
from django.core.management.base import BaseCommand

from apps.blog.models import Post

POSTS = [
    {
        "slug": "demystifying-websites-why-your-business-needs-one",
        "title": "Demystifying Websites: What They Are and Why Your Zimbabwean Business Needs One",
        "excerpt": "A website is your 24/7 storefront \u2014 but in Zimbabwe specifically, it's also what makes you show up on Google before your competitor does.",
        "body": """In today's digital age, websites have become indispensable tools for businesses. But what exactly is a website? Simply put, it's a collection of pages hosted on the internet \u2014 your online storefront, open to anyone who wants to know what you sell, where you are, and how to reach you.

Think of it as the virtual face of your business, open 24/7, whether you're a vegetable stall in Mvurwi or a growing company in Harare. Having a website offers advantages that a WhatsApp number and a Facebook page alone can't match.

Credibility. Zimbabwean consumers are just as tech-savvy as anyone else \u2014 when someone's deciding between two businesses and one shows up on Google with a real website and the other doesn't, that decision is already half made. A site doesn't need to be elaborate to do this job; it needs to exist.

Accessibility. Your shop has hours. Your website doesn't. Someone browsing at 11pm because that's when they finally have data and time can still find your prices, your location, and a WhatsApp button to order \u2014 without waiting for you to open.

Reach beyond where you can physically be. A .co.zw domain and a real site mean someone in Bulawayo, or a relative sending money from the diaspora to buy from you, can find you the same way someone down the road can. That's not a luxury reserved for big companies \u2014 it's available at $25/year now.

Marketing that compounds. Every blog post, every page, every bit of content you publish is something Google can index and someone can search for later. A Facebook post disappears from feeds within a day. A website page keeps working for you months later.

Real insight into who's actually interested. Once you have a website, you can see what people are searching for, what pages they spend time on, and what's actually driving inquiries \u2014 information a WhatsApp inbox alone can't give you.

None of this requires a huge budget or months of work. A proper business website \u2014 one built to load fast even on 2G/3G, with WhatsApp ordering built in from day one \u2014 starts at $25/year here. That's less than the cost of one data bundle a month, for something that works every day it's live.

If you haven't put your business online yet, now's the moment \u2014 not because it's trendy, but because your competitors are already doing it, and every day you're not found is a day they are.

Ready to get found? See packages and past work at phyb.co.zw/pricing.""",
    },
    {
        "slug": "how-much-should-a-website-cost-in-zimbabwe",
        "title": "How Much Should a Website Actually Cost in Zimbabwe? (2026 Breakdown)",
        "excerpt": "From a $25/year signpost to a full online store \u2014 a transparent breakdown of what you actually get at each price point, and why \u201cit depends\u201d doesn't have to mean unclear.",
        "body": """\u201cHow much does a website cost?\u201d is one of the most common questions I get, and it's a fair one \u2014 pricing in this industry can feel like a black box. Here's a transparent breakdown, using real numbers, not vague ranges.

Signpost \u2014 $25/year. This is the entry point: a 2-page site with your business info, a free .co.zw domain, hosting, and a WhatsApp ordering button, live within 24\u201348 hours. It's built for one job \u2014 making sure that when someone Googles your business, something real shows up. If you're currently relying entirely on word of mouth and a WhatsApp number, this is the smallest possible step that actually changes that.

Basic \u2014 $80. A proper small website: up to 5 pages, mobile-first design, a contact form, basic SEO and Google Business setup, and \u2014 importantly \u2014 an admin panel so you can edit your own text, prices, and photos without calling a developer every time something changes. Good for startups, CVs, and portfolios that need to look legitimate.

Standard \u2014 $200. Everything in Basic, plus up to 8 pages, a blog/CMS built into that same admin panel (so you can publish your own updates), a portfolio or testimonials section, and stronger SEO. This is the tier most growing businesses actually need \u2014 enough room to tell a fuller story without paying for e-commerce you're not ready to use yet.

Premium \u2014 $370. Up to 12 pages, a full e-commerce store with payments, a booking system, WhatsApp API integration, and custom UI/UX design. Built for businesses ready to actually sell and take bookings online, not just be found.

Why the range, and why it's worth it compared to the alternatives: A $20/month page-builder subscription (Wix and similar) adds up to roughly $240/year \u2014 every year, forever, and your site disappears the moment you stop paying. Every PHYB package is a one-time build fee (Signpost is the exception, deliberately kept as a low annual cost since it's the cheapest possible way in) \u2014 after that, you're only paying for domain + hosting renewal, $25/year from year two, regardless of tier.

What determines where you should start: if you just need to stop being invisible on Google, Signpost. If you need a real presence with room to edit it yourself, Basic or Standard. If you're ready to actually sell or take bookings through the site, Premium.

There's no single \u201ccorrect\u201d price for a website \u2014 but there is a correct question, which is what you actually need it to do. Once that's clear, the price follows.

See the full breakdown and past work at phyb.co.zw/pricing.""",
    },
    {
        "slug": "why-you-should-own-your-website-not-rent-it",
        "title": "Why You Should Own Your Website, Not Rent It",
        "excerpt": "Wix and similar platforms feel easy at first \u2014 until you've paid $240/year for three years and still don't actually own anything. Here's the difference real ownership makes.",
        "body": """There's a quiet trap in how most small businesses end up online: page-builder platforms like Wix make it easy to start, but what you're actually doing is renting a website, not owning one. It's worth understanding the difference before you commit to either path.

The rental model. Wix and similar platforms charge roughly $20/month \u2014 about $240/year \u2014 for as long as you want your site to stay live. Stop paying for any reason (a slow month, a change in priorities, simply forgetting) and the site disappears immediately. Everything you built, gone. You never actually held the deed to it; you were paying for access.

The ownership model. A site built properly \u2014 a real domain you control, hosting you pay for directly, code that's actually yours \u2014 doesn't have this failure mode. If you ever want to switch developers, change hosts, or just take a break from paying attention to it, the site keeps existing. You're not one missed payment away from losing your online presence entirely.

\u201cBut I can't edit a real website myself\u201d \u2014 actually, you can. This is the part people assume is the tradeoff, and it isn't one at PHYB: every package from Basic upward includes a real admin panel. You can change a price, swap a photo, or fix a typo yourself, in about two minutes, any time \u2014 without messaging a developer and waiting. The admin panel isn't a page-builder's drag-and-drop editor bolted onto a rented site; it's a real content management system attached to a site you own outright.

The actual math. Basic starts at $80 once, with $25/year afterward for domain and hosting \u2014 meaningfully less than three years of a Wix subscription, and at the end of it you own something instead of having rented it.

Room to grow without starting over. Because it's a real codebase, not a page-builder template, a site can grow with you \u2014 add a blog, add e-commerce, add a booking system \u2014 without migrating everything to a new platform later. Growth is an upgrade, not a rebuild.

Renting is fine for something you expect to be temporary. A business's online presence usually isn't temporary \u2014 which means ownership isn't a luxury upgrade, it's just the more sensible default.

Ready to own yours instead of renting it? See packages at phyb.co.zw/pricing.""",
    },
]


class Command(BaseCommand):
    help = "Seed (or update) the three launch blog posts. Idempotent \u2014 matches on slug."

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

        self.stdout.write(self.style.SUCCESS(f"\nDone \u2014 {len(POSTS)} posts set to '{status}'."))
