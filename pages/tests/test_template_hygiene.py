"""A rule that holds for every template the project renders, checked in one place.

This was found by reading the body of a passing test: the explanation above the
verification verdict was being served to the visitor. Django's `{# #}` matches on
a single line only, so a comment spread over two lines is not stripped. The rule
is not obvious and the failure is silent, which is why it is checked everywhere
rather than only where it was noticed.

The templates are discovered rather than listed, so moving one or adding one
cannot quietly drop it out of the check.
"""

from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.template.loader import get_template
from django.test import SimpleTestCase


def project_template_dirs():
    """The project's own template directories: the shared one and each app's.

    An app of this project sits directly under the repository root, which is
    what separates it from Django's own apps. Testing that the root is merely
    somewhere above the app is not enough, because the virtual environment also
    lives under the root and would drag in every template Django ships.
    """
    base = Path(settings.BASE_DIR).resolve()
    directories = [Path(directory) for directory in settings.TEMPLATES[0]["DIRS"]]

    for app_config in apps.get_app_configs():
        app_path = Path(app_config.path).resolve()
        if app_path.parent != base:
            continue
        if (app_path / "templates").is_dir():
            directories.append(app_path / "templates")

    return directories


def project_templates():
    """Every template of this project, as (loader name, path) pairs."""
    for directory in project_template_dirs():
        for path in sorted(directory.rglob("*.html")):
            yield path.relative_to(directory).as_posix(), path


class TemplateDiscoveryTests(SimpleTestCase):
    def test_the_templates_are_found(self):
        """Guards the checks below: an empty walk would pass them without checking anything."""
        self.assertGreater(len(list(project_templates())), 10)


class TemplateSyntaxTests(SimpleTestCase):
    """Every template parses.

    A template is only compiled when something renders it, so a tag typed wrong
    in a page no test opens is found by a visitor rather than by the suite. The
    commonest way to hit this is a translation tag without `{% load i18n %}`.
    """

    def test_every_template_compiles(self):
        for name, _path in project_templates():
            with self.subTest(template=name):
                get_template(name)


class TemplateCommentTests(SimpleTestCase):
    def test_no_template_opens_a_comment_it_does_not_close_on_the_same_line(self):
        offenders = []

        for name, path in project_templates():
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if "{#" in line and "#}" not in line:
                    offenders.append(f"{name}:{number}")

        self.assertEqual(offenders, [], "use {% comment %} for a comment over two lines")
