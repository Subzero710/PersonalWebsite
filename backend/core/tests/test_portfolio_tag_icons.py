from pathlib import Path

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase

from core.models import Tag
from core.templatetags.markdown_extras import skill_icon_src


class PortfolioTagIconTests(SimpleTestCase):
    KO_TAGS = (
        ('Networking', 'networking'),
        ('Distributed', 'distributed'),
        ('Cybersecurity', 'cybersecurity'),
        ('CI/CD', 'cicd'),
        ('Reinforcement Learning', 'reinforcement-learning'),
        ('Automated Testing', 'automated-testing'),
        ('AI', 'ai'),
        ('Web Scraping', 'web-scraping'),
        ('CNN', 'cnn'),
    )

    def test_ko_tags_have_no_generic_or_unapproved_svg(self):
        for name, slug in self.KO_TAGS:
            with self.subTest(name=name):
                self.assertEqual(skill_icon_src(Tag(name=name, slug=slug)), '')

    def test_kubernetes_is_cncf_artwork(self):
        path = finders.find('core/icons/skills/kubernetes.svg')
        self.assertTrue(path)
        source = Path(path).read_text(encoding='utf-8')
        self.assertIn('viewBox="-0.17 0.08 230.10 223.35"', source)
        self.assertIn('#326ce5', source.lower())

    def test_new_approved_assets_are_shipped(self):
        for filename in ('kotlin.svg', 'kvmqemu.svg', 'lz4.svg', 'mcp.svg', 's3.svg', 'websocket.svg'):
            with self.subTest(filename=filename):
                self.assertTrue(finders.find(f'core/icons/skills/{filename}'))
