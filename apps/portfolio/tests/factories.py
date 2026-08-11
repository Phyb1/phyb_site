import factory

from apps.portfolio.models import Project


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    title = factory.Sequence(lambda n: f"Client Project {n}")
    summary = "A short project summary."
    package = Project.Package.STANDARD
