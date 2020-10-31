"""Test functions specific to Call of Cthulhu."""
import os
import json
import pytest

from jsonschema import validate
from app.character.coc import convert_from_dholes
from app.character.coc import schema, new_character

BASEDIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(name='dholes_sheet')
def fixture_dholes_sheet() -> dict:
    """Load character sheet from JSON and convert to dict."""
    sheet = None
    filename = os.path.join(BASEDIR, 'testchar_dholes.json')
    with open(filename, 'r') as input_file:
        sheet = json.load(input_file)

    return sheet


@pytest.fixture(name='test_sheet')
def fixture_test_sheet() -> dict:
    """Load character sheet from JSON and convert to dict."""
    sheet = None
    with open(os.path.join(BASEDIR, 'testchar.json'), 'r') as input_file:
        sheet = json.load(input_file)

    return sheet


def test_validate(test_sheet: dict):
    nc = new_character("Test Character", "Classic (1920's)")

    validate(nc, schema=schema)
    validate(test_sheet, schema=schema)


def test_convert_from_dholes(dholes_sheet: dict, test_sheet: dict):
    """Test conversion from a character sheet generated at dholes house."""
    assert dholes_sheet is not None
    converted = convert_from_dholes(dholes_sheet)

    sheet_sections = ['meta', 'personalia', 'characteristics',
                      'skills', 'weapons', 'combat', 'backstory',
                      'possessions', 'cash', 'assets']

    for section in sheet_sections:
        assert section in converted

    skills = converted['skills']
    assert isinstance(skills, list)

    skill_names = ['Accounting', 'Appraise', 'Cthulhu Mythos']
    for skill in skills:
        if skill['name'] in skill_names:
            skill_names.remove(skill['name'])

    assert not skill_names

    weapons = converted['weapons']
    assert isinstance(weapons, list)

    possessions = converted['possessions']
    assert isinstance(possessions, list)

    validate(converted, schema=schema)
