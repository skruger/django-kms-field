from django_kms import cache

from django.test import TestCase


class CacheTestCase(TestCase):
    def test_purge(self):
        simple_cache = cache.SimpleCache(max_size=2)

        simple_cache.set('a', 'String 1')
        self.assertEqual(list(simple_cache._cache.keys()), ['a'])
        self.assertEqual(len(simple_cache), 1)

        simple_cache.set('b', 'String 2')
        self.assertEqual(list(simple_cache._cache.keys()), ['a', 'b'])
        self.assertEqual(len(simple_cache), 2)

        simple_cache.set('c', 'String 3')
        self.assertEqual(list(simple_cache._cache.keys()), ['b', 'c'])
        self.assertEqual(simple_cache.get('c'), 'String 3')
        self.assertEqual(len(simple_cache), 2)

        with self.assertRaises(cache.SimpleCache.CacheMiss):
            simple_cache.get('a')
