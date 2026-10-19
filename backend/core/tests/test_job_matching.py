"""Run with: python manage.py test core.tests.test_job_matching"""

import json
from unittest.mock import patch

from django.test import SimpleTestCase
from core.job_matching import MatchingFailed, _response_text, verify_report
from core.job_matching_pdf import build_pdf, filename_for, slug_part
from core.job_matching_views import JobMatchForm
from core.job_matching_setup import setup_issues
from types import SimpleNamespace


class FilenameTests(SimpleTestCase):
    def test_french_accents_and_separators(self):
        self.assertEqual(filename_for('Jean', 'Dupont', 'Ingénieur DevOps / Cloud'),
                         'dupont_jean_ingenieur_devops_cloud.pdf')

    def test_double_name(self):
        self.assertEqual(filename_for('Anne-Marie', "O'Neill", 'Full Stack Developer'),
                         'oneill_anne_marie_full_stack_developer.pdf')

    def test_empty_name_is_not_silently_guessed(self):
        with self.assertRaises(ValueError):
            filename_for('', 'Dubois', 'Backend Engineer')


class FormTests(SimpleTestCase):
    def test_requires_role_and_description(self):
        form = JobMatchForm({'job_title': 'Backend engineer', 'job_description': 'Python'})
        self.assertFalse(form.is_valid())

    def test_accepts_full_job_posting(self):
        form = JobMatchForm({'job_title': 'Backend Engineer', 'job_description': 'Python and Django backend engineer with cloud deployments and PostgreSQL.'})
        self.assertTrue(form.is_valid())


class VerificationTests(SimpleTestCase):
    sources = {
        'project:9': {'id': 'project:9', 'kind': 'project', 'text': 'Implemented a Django API using PostgreSQL and tests.',
                      'label': 'Project 9', 'url': 'https://example.com/project/9/', 'narrative': 'Implemented a Django API using PostgreSQL and tests.',
                      'project': {'title': 'Project 9', 'summary': 'Backend API', 'tags': ['Django'],
                                  'url': 'https://example.com/project/9/', 'repo_url': '', 'demo_url': ''}},
        'skill:1': {'id': 'skill:1', 'kind': 'skill', 'text': 'Python', 'label': 'Skill: Python', 'url': ''},
    }

    def test_disallows_hallucinated_quotes_and_ids(self):
        report = verify_report({'requirements': [{'requirement': 'Django', 'job_excerpt': 'Django', 'category': 'required',
                'assessment': 'documented', 'evidence': [{'source_id': 'project:9', 'excerpt': '10 years at Google'}]}],
                'relevant_projects': ['project:9']}, self.sources)
        self.assertEqual(report['requirements'][0]['status'], 'not_documented')
        self.assertFalse(report['requirements'][0]['evidence'])
        self.assertFalse(report['projects'])

    def test_verified_project_quote(self):
        report = verify_report({'requirements': [{'requirement': 'Django API', 'job_excerpt': 'Django API', 'category': 'required',
                'assessment': 'documented', 'evidence': [{'source_id': 'project:9', 'excerpt': 'Implemented a Django API'}]}],
                'relevant_projects': ['project:9']}, self.sources)
        self.assertEqual(report['requirements'][0]['status'], 'documented')
        self.assertEqual(report['projects'][0]['title'], 'Project 9')

    def test_skill_listing_cannot_claim_experience(self):
        report = verify_report({'requirements': [{'requirement': '5 years Python', 'job_excerpt': '5 years Python', 'category': 'experience',
                'assessment': 'documented', 'evidence': [{'source_id': 'skill:1', 'excerpt': 'Python'}]}],
                'relevant_projects': []}, self.sources)
        self.assertEqual(report['requirements'][0]['status'], 'related')

    def test_rejects_invented_job_requirement(self):
        raw = {'requirements': [{'requirement': 'C++', 'job_excerpt': '10 years C++',
                 'category': 'required', 'assessment': 'related', 'evidence': []}], 'relevant_projects': []}
        with self.assertRaises(MatchingFailed):
            verify_report(raw, self.sources, job_description='Looking for a Django API engineer.')

    def test_pdf_bytes_and_sources(self):
        report = verify_report({'requirements': [{'requirement': 'Django API', 'job_excerpt': 'Django API', 'category': 'required',
                'assessment': 'documented', 'evidence': [{'source_id': 'project:9', 'excerpt': 'Implemented a Django API'}]}],
                'relevant_projects': ['project:9']}, self.sources)
        pdf = build_pdf(title='Backend engineer', company='Acme', first_name='Jean',
                        last_name='Dupont', report=report, public_url='https://example.com/')
        self.assertTrue(pdf.startswith(b'%PDF-'))
        self.assertGreater(len(pdf), 1000)

    def test_empty_requirement_list_errors(self):
        with self.assertRaises(MatchingFailed):
            verify_report({'requirements': [], 'relevant_projects': []}, self.sources)


class ReadinessTests(SimpleTestCase):
    def codes(self, config=None, key='present'):
        return [item['code'] for item in setup_issues(config, key)]

    def test_no_site_config(self):
        self.assertEqual(self.codes(None), ['site_config_missing'])

    def test_no_site_config_and_no_api_key(self):
        self.assertEqual(self.codes(None, ''), ['site_config_missing', 'api_key_missing'])

    def test_name_fields_reported_individually(self):
        config = SimpleNamespace(first_name='', last_name='')
        self.assertEqual(self.codes(config), ['first_name_missing', 'last_name_missing'])
        self.assertEqual(self.codes(SimpleNamespace(first_name='Jane', last_name='')),
                         ['last_name_missing'])
        self.assertEqual(self.codes(SimpleNamespace(first_name='', last_name='Doe')),
                         ['first_name_missing'])

    def test_only_api_key_missing(self):
        config = SimpleNamespace(first_name='Jane', last_name='Doe')
        self.assertEqual(self.codes(config, ''), ['api_key_missing'])

    def test_ready(self):
        config = SimpleNamespace(first_name=' Jane ', last_name='Doe')
        self.assertEqual(self.codes(config), [])
