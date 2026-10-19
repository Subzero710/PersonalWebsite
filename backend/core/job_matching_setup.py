"""Concrete Job Matching readiness checks used by the page and POST endpoint.

Only reports missing public configuration fields; never exposes secret values.
"""


def setup_issues(config, api_key):
    issues = []
    if config is None:
        issues.append({
            'code': 'site_config_missing',
            'message': 'Site Config is missing. Create the portfolio profile in Django Admin.',
        })
    else:
        if not (config.first_name or '').strip():
            issues.append({
                'code': 'first_name_missing',
                'message': 'First name is missing in Django Admin → Site Config → Identity.',
            })
        if not (config.last_name or '').strip():
            issues.append({
                'code': 'last_name_missing',
                'message': 'Last name is missing in Django Admin → Site Config → Identity.',
            })
    if not (api_key or '').strip():
        issues.append({
            'code': 'api_key_missing',
            'message': 'OPENAI_API_KEY is missing from the Django web service environment.',
        })
    return issues
