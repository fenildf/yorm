# pylint: disable=missing-docstring,redefined-outer-name,unused-variable,expression-not-assigned

import pytest
from expecter import expect

import yorm
from yorm import exceptions
from yorm.mapper import Mapper
from yorm.types import Integer


class MyObject:
    var1 = 1


@pytest.fixture
def obj():
    return MyObject()


@pytest.fixture
def attrs():
    return {'var2': Integer, 'var3': Integer}


@pytest.yield_fixture(params=("real", "fake"))
def mapper(tmpdir, obj, attrs, request):
    path = request.param + "/path/to/file"
    backup = yorm.settings.fake
    if "fake" in path:
        yorm.settings.fake = True
    elif "real" in path:
        tmpdir.chdir()
    yield Mapper(obj, path, attrs, strict=True)
    yorm.settings.fake = backup


@pytest.fixture
def mapper_real(tmpdir, obj, attrs):
    tmpdir.chdir()
    return Mapper(obj, "real/path/to/file", attrs)


@pytest.yield_fixture
def mapper_fake(obj, attrs):
    backup = yorm.settings.fake
    yorm.settings.fake = True
    yield Mapper(obj, "fake/path/to/file", attrs)
    yorm.settings.fake = backup


def describe_mapper():

    def describe_create():

        def it_creates_the_file(mapper_real):
            mapper_real.create()

            expect(mapper_real.path).exists()
            expect(mapper_real.exists).is_true()
            expect(mapper_real.deleted).is_false()

        def it_pretends_when_fake(mapper_fake):
            mapper_fake.create()

            expect(mapper_fake.path).missing()
            expect(mapper_fake.exists).is_true()
            expect(mapper_fake.deleted).is_false()

        def it_can_be_called_twice(mapper_real):
            mapper_real.create()
            mapper_real.create()  # should be ignored

            expect(mapper_real.path).exists()

    def describe_delete():

        def it_deletes_the_file(mapper):
            mapper.create()
            mapper.delete()

            expect(mapper.path).missing()
            expect(mapper.exists).is_false()
            expect(mapper.deleted).is_true()

        def it_can_be_called_twice(mapper):
            mapper.delete()
            mapper.delete()  # should be ignored

            expect(mapper.path).missing()

    def describe_fetch():

        def it_adds_missing_attributes(obj, mapper):
            mapper.create()
            mapper.fetch()

            expect(obj.var1) == 1
            expect(obj.var2) == 0
            expect(obj.var3) == 0

        def it_ignores_new_attributes(obj, mapper):
            mapper.create()
            mapper.text = "var4: foo"

            mapper.fetch()
            with expect.raises(AttributeError):
                print(obj.var4)

        def it_infers_types_on_new_attributes_when_not_strict(obj, mapper):
            mapper.strict = False
            mapper.create()
            mapper.text = "var4: foo"

            mapper.fetch()
            expect(obj.var4) == "foo"

            obj.var4 = 42
            mapper.store()

            mapper.fetch()
            expect(obj.var4) == "42"

        def it_raises_an_exception_after_delete(mapper):
            mapper.delete()

            with expect.raises(exceptions.FileDeletedError):
                mapper.fetch()

    def describe_store():

        def it_creates_the_file_automatically(mapper_real):
            mapper_real.store()

            expect(mapper_real.path).exists()

    def describe_modified():

        def is_true_initially(mapper):
            expect(mapper.modified).is_true()

        def is_true_after_create(mapper):
            mapper.create()

            expect(mapper.modified).is_true()

        def is_true_after_delete(mapper):
            mapper.delete()

            expect(mapper.modified).is_true()

        def is_false_after_fetch(mapper):
            mapper.create()
            mapper.fetch()

            expect(mapper.modified).is_false()

        def can_be_set_false(mapper):
            mapper.modified = False

            expect(mapper.modified).is_false()

        def can_be_set_true(mapper):
            mapper.modified = True

            expect(mapper.modified).is_true()

    def describe_text():

        def can_get_the_file_contents(obj, mapper):
            obj.var3 = 42
            mapper.store()

            expect(mapper.text) == "var2: 0\nvar3: 42\n"

        def can_set_the_file_contents(obj, mapper):
            mapper.create()
            mapper.text = "var2: 42\n"
            mapper.fetch()

            expect(obj.var2) == 42
