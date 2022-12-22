import pytest

@pytest.fixture
def tr():
    return TestResource()

class TestResource(object):

    def dump(self, val = None, label = None):
        if label:
            msg = '\n{} =>'.format(label)
            print(msg)
        else:
            print()
        print(val)
        print()

