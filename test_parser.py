import parsers as pr
import pytest


@pytest.fixture
def default_parser():
    return pr.DefaultParser()

def test_extract_static_assets(default_parser):
    html = """
    <link rel="stylesheet" href="http://aosabook.org/en/500L/theme/css/bootstrap.css" type="text/css" />
    <link rel="stylesheet" href="http://aosabook.org/en/500L/theme/css/bootstrap-responsive.css" type="text/css" />
    <link rel="stylesheet" href="http://aosabook.org/en/500L/theme/css/code.css" type="text/css" />
    <link rel="stylesheet" href="http://aosabook.org/en/500L/theme/css/500L.css" type="text/css" />
    <script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
    </script>
    """
    assert len(default_parser.extract_static_assets(html)) == 5


@pytest.mark.parametrize('entrypoint, url', [
    ('http://foo.com', 'http://foo.com'),
    ('https://foo.com', 'http://foo.com'),
    ('http://foo.com', 'https://foo.com'),
    ('http://foo.com', 'https://foo.com/some/path'),
    ('http://foo.com', 'https://foo.com/some/path?arg=1'),
    ('http://foo.com', 'https://foo.com/some/path#12'),
    ('http://foo.com', 'https://foo.com/some/path#12?arg=1&arg1=2'),
])
def test_is_external_url_returns_false_if_hostnames_of_both_urls_match(default_parser, entrypoint, url):
    assert not default_parser.is_external_url(entrypoint, url)


@pytest.mark.parametrize('entrypoint, url', [
    ('http://bar.com', 'http://foo.com'),
    ('//bar.com', 'http://foo.com'),
    ('http://bar.com', '//foo.com'),
    ('http://bar.com', 'https://foo.com'),
    ('http://bar.com', 'https://foo.com?arg=1'),
])
def test_is_external_url_returns_true_if_hostnames_do_not_match(default_parser, entrypoint, url):
    assert default_parser.is_external_url(entrypoint, url)

@pytest.mark.parametrize(
    'base_url, url, expected',
    [
        ('http://localhost', '/', 'http://localhost/'),
        ('http://localhost', '/foo.css', 'http://localhost/foo.css'),
        ('http://localhost', '/some/script/path/1.js', 'http://localhost/some/script/path/1.js'),
    ])
def test_normalize_url_returns_full_url_given_relative(default_parser, base_url, url, expected):
    assert default_parser.normalize_url(base_url, url) == expected


def test_normalize_url_retuns_full_url_if_absolute_is_given(default_parser):
    assert default_parser.normalize_url('http://foo.com', 'http://external/resource.css') == 'http://external/resource.css'

@pytest.mark.parametrize(
    'base_url, url, expected',
    [
        ('http://localhost', '/?arg1=1&foo=1', 'http://localhost/'),
        ('http://localhost', '/foo.css#page1', 'http://localhost/foo.css'),
        ('http://localhost', '/some/script/path/1.js#page1?arg1=1', 'http://localhost/some/script/path/1.js'),
    ])
def test_normalize_url_strips_qeuey_args_and_anchors(default_parser, base_url, url, expected):
    assert default_parser.normalize_url(base_url, url) == expected
