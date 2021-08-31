from oniref.strings import KleiStrings


def test_len():
    assert len(KleiStrings({})) == 0

    sample = KleiStrings({'foo': 'bar'})
    assert len(sample) == 1


def test_iter():
    assert list(KleiStrings({})) == []
    assert list(KleiStrings({'foo': 'bar', 'baz': 'quux'})) == ['foo', 'baz']


def test_get():
    assert KleiStrings({}).get('foo') is None
    assert KleiStrings({}).get('foo', 'bar') == 'bar'
    assert KleiStrings({}).get(key='foo', default='bar') == 'bar'
    assert KleiStrings({'foo': '<xml>bar</xml>'}).get('foo') == 'bar'


def test_get_raw():
    assert KleiStrings({}).get_raw('foo') is None
    assert KleiStrings({}).get_raw('foo', 'bar') == 'bar'
    assert KleiStrings({}).get_raw(key='foo', default='bar') == 'bar'
    assert (KleiStrings({'foo': '<xml>bar</xml>'}).get_raw('foo')
            == '<xml>bar</xml>')
