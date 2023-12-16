import unittest
import random
from resources.lib.providers import sfrtv
from codequick import Script

plugin = Script


class TestSFRTvIntegration(unittest.TestCase):
    def test_get_live_url(self):
        token = sfrtv.get_token(plugin)
        self.assertIsNotNone(token,
                             'token is defined')

        active_services = sfrtv.get_active_services(plugin, token)
        self.assertGreater(len(active_services), 70,
                           'More than 70 active services')

        service = active_services[random.randint(0, len(active_services) - 1)]
        service_id = service['serviceId']
        self.assertIsNotNone(service_id)

        live_url = sfrtv.get_live_url(plugin, service_id, token)
        self.assertRegex(live_url, r'^https://.+\.mpd',
                         'looks like an url')

    def test_get_stream_url(self):
        token = sfrtv.get_token(plugin)
        self.assertIsNotNone(token,
                             'token is defined')

        stores = sfrtv.get_replay_stores(plugin, token)
        self.assertGreater(len(stores), 60,
                           'More than 60 stores')

        store = stores[random.randint(0, len(stores) - 1)]
        store_id = store['action']['actionIds']['storeId']
        self.assertIsNotNone(store_id)

        categories = sfrtv.get_store_categories(plugin, store_id)
        self.assertGreater(len(categories), 0,
                           'At least 1 category')

        category = categories[random.randint(0, len(categories) - 1)]
        category_id = category['id']
        self.assertIsNotNone(category_id)

        contents = sfrtv.get_category_contents(plugin, category_id, 0)
        self.assertGreater(len(contents), 0,
                           'At least 1 content')

        content = contents[random.randint(0, len(contents) - 1)]
        content_id = content['id']
        self.assertIsNotNone(content_id)

        content_details = sfrtv.get_content_details(plugin, content_id)
        self.assertIsNotNone(content_details)

        if 'episodes' in content_details:
            episode_id = content_details['episodes'][0]['id']
            self.assertIsNotNone(episode_id)
            video_url, context, offer_id = sfrtv.get_stream_url(plugin, episode_id, token)
        else:
            movie_id = content_details['id']
            self.assertIsNotNone(movie_id)
            video_url, context, offer_id = sfrtv.get_stream_url(plugin, movie_id, token)

        self.assertEqual(context.upper(), 'REPLAY',
                         'context is replay')
        self.assertRegex(video_url, r'^https://.+\.mpd',
                         'looks like an url')


if __name__ == '__main__':
    unittest.main()
