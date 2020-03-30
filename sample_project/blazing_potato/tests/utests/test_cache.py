import unittest
import cache
import errors

class TestClassExample(unittest.TestCase):
    def set_up(self):
        cacher = cache.get_cacher()
        cacher.internal_cache = {}
        return cacher

    def test_save(self):
        cacher = self.set_up()
        cacher.save("key1","value1")
        assert cacher.internal_cache == {"key1":"value1"}

    def test_get(self):
        cacher = self.set_up()
        cacher.save("key2","value2")
        assert cacher.get("key2") == "value2"

    def test_delete(self):
        cacher = self.set_up()
        cacher.save("key2","value2")
        cacher.delete("key2")
        assert cacher.internal_cache == {}

        try:
            cacher.delete("key3")
            assert False
        except errors.InvalidKey:
            assert True
