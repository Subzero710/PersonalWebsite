"""Technology icon selection is configured in Admin without schema migrations."""

from django.test import SimpleTestCase, TestCase

from core.admin import (
    SkillTechnologyIconForm,
    TagTechnologyIconForm,
    _admin_skill_icon_choices,
)
from core.models import SKILL_ICON_CHOICES, Tag


class IconChoicesTests(SimpleTestCase):
    def test_bundled_svg_icons_are_selectable(self):
        values = dict(_admin_skill_icon_choices())
        for key in ('rust', 'c', 'cplusplus', 'csharp', 'tensorflow',
                    'opencv', 'numpy', 'pandas', 'scikitlearn', 'flask'):
            self.assertIn(key, values)

    def test_no_model_choices_modified(self):
        old_values = dict(SKILL_ICON_CHOICES)
        self.assertNotIn('rust', old_values)
        self.assertIn('rust', dict(TagTechnologyIconForm().fields['icon_key'].choices))
        self.assertIn('rust', dict(SkillTechnologyIconForm().fields['icon_key'].choices))


class IconFormSaveTests(TestCase):
    def test_tag_can_use_extra_icon_without_model_migration(self):
        form = TagTechnologyIconForm({
            'name': 'Rust language', 'slug': 'rust-language', 'icon_key': 'rust',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().icon_key, 'rust')

    def test_invalid_icon_key_is_rejected(self):
        form = TagTechnologyIconForm({
            'name': 'Something', 'slug': 'something', 'icon_key': 'missing-logo',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('icon_key', form.errors)
