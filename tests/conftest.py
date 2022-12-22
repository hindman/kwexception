import pytest

@pytest.fixture
def tr():
    return TestResource()

class TestResource(object):

    def dump(self, val = None, label = 'dump()'):
        fmt = '\n--------\n{label} =>\n{val}'
        msg = fmt.format(label = label, val = val)
        print(msg)

    def dumpj(self, val = None, label = 'dump()', indent = 4):
        val = json.dumps(val, indent = indent)
        self.dump(val, label)

