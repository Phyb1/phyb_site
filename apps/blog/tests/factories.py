import factory

from apps.blog.models import Post


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f"Article {n}")
    excerpt = "A short excerpt."
    body = "Full article body text."
    status = Post.Status.PUBLISHED
