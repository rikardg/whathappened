from app.character.coc7e.routes import half, fifth


def test_half():
    assert half("100") == 50
    assert half("55") == 27
    assert half("foo") == ''


def test_fifth():
    assert fifth("100") == 20
    assert fifth("54") == 10
    assert fifth("foo") == ''