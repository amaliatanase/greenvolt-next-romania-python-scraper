import json
from unittest.mock import patch

import pytest
from scraper import main
from scraper.parse import parse_listing
from scraper.validate import assert_scrape_yielded_jobs, CanaryError, filter_valid_jobs


def posting(**changes):
    return {'title': 'Backend Engineer', 'url': 'https://apply.workable.com/j/ABC123/',
            'country': 'Romania', 'city': 'Bucharest', 'telecommuting': True, **changes}


def parse(*rows):
    return parse_listing(json.dumps({'jobs': list(rows)}))


def test_only_romania_even_for_remote_roles():
    rows = [posting(), posting(country='Estonia', url='https://x/ee'),
            posting(country=None, url='https://x/unknown'),
            posting(country='Worldwide', url='https://x/world')]
    jobs = parse(*rows)
    assert len(jobs) == 1
    assert jobs[0]['location'] == ['Bucharest']
    assert jobs[0]['workmode'] == 'remote'


def test_nested_location_hybrid_and_country_normalization():
    jobs = parse(posting(location={'country': ' Romania ', 'city': 'Cluj-Napoca', 'telecommuting': True},
                         workplace_type='hybrid'))
    assert jobs[0]['location'] == ['Cluj-Napoca']
    assert jobs[0]['workmode'] == 'hybrid'


def test_missing_city_and_workmode_do_not_invent_them():
    jobs = parse(posting(city='', telecommuting=None))
    assert jobs[0]['location'] == ['România']
    assert jobs[0]['workmode'] is None


def test_deduplicates_urls_without_merging_different_postings():
    assert len(parse(posting(), posting(), posting(url='https://apply.workable.com/j/DEF/'))) == 2


@pytest.mark.parametrize('changes', [{'title': ''}, {'url': ''}, {'url': 'javascript:alert(1)'}, {'url': None}])
def test_unpublishable_postings_are_rejected(changes):
    assert parse(posting(**changes)) == []


@pytest.mark.parametrize('payload', [{}, {'jobs': None}, {'jobs': {}}])
def test_schema_changes_fail_visibly(payload):
    with pytest.raises(ValueError):
        parse_listing(json.dumps(payload))


def test_foreign_only_result_still_triggers_canary():
    with pytest.raises(CanaryError):
        assert_scrape_yielded_jobs(parse(posting(country='Estonia')))


def test_source_to_upload_model_preserves_workable_fields():
    response = json.dumps({'jobs': [posting(), posting(country='Estonia', url='https://x/ee')]})
    with patch.object(main.browser, 'get_html', return_value=response):
        raw_jobs = main.scrape_careers()
    kept, dropped = filter_valid_jobs(raw_jobs)
    assert not dropped and len(kept) == 1
    job = main._to_job_model(kept[0], '12345678', 'EXAMPLE COMPANY')
    assert job['location'] == ['Bucharest']
    assert job['workmode'] == 'remote'
    assert job['url'] == 'https://apply.workable.com/j/ABC123/'
    assert job.get('expirationdate') is None
