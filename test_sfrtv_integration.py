import random
import re
from resources.lib.providers import sfrtv
from codequick import Script

plugin = Script


class TestSFRTvIntegration:
    def test_get_live_url(self):
        token = sfrtv.get_token(plugin)
        assert isinstance(token, str)

        active_services = sfrtv.get_active_services(plugin, token)
        assert len(active_services) > 70

        service = active_services[random.randint(0, len(active_services) - 1)]
        service_id = service['serviceId']
        assert isinstance(service_id, str)

        live_url = sfrtv.get_live_url(plugin, service_id, token)
        assert re.match(r'^https://.+\.mpd', live_url)

    def test_get_stream_url(self):
        token = sfrtv.get_token(plugin)
        assert isinstance(token, str)

        stores = sfrtv.get_replay_stores(plugin, token)
        assert len(stores) > 60

        store = stores[random.randint(0, len(stores) - 1)]
        store_id = store['action']['actionIds']['storeId']
        assert isinstance(store_id, str)

        categories = sfrtv.get_store_categories(plugin, store_id)
        assert len(categories) > 0

        category = categories[random.randint(0, len(categories) - 1)]
        category_id = category['id']
        assert isinstance(category_id, str)

        contents = sfrtv.get_category_contents(plugin, category_id, 0)
        assert len(contents) > 0

        content = contents[random.randint(0, len(contents) - 1)]
        content_id = content['id']
        assert isinstance(content_id, str)

        content_details = sfrtv.get_content_details(plugin, content_id)
        if 'seasons' in content_details:
            season = content_details['seasons'][0]
            season_id = season['id']
            assert isinstance(season_id, str)
            season_details = sfrtv.get_content_details(plugin, season_id)
            episode_id = season_details['episodes'][0]['id']
            assert isinstance(episode_id, str)
            video_url, context, offer_id = sfrtv.get_stream_url(plugin, episode_id, token)
        elif 'episodes' in content_details:
            episode_id = content_details['episodes'][0]['id']
            assert isinstance(episode_id, str)
            video_url, context, offer_id = sfrtv.get_stream_url(plugin, episode_id, token)
        else:
            movie_id = content_details['id']
            assert isinstance(movie_id, str)
            video_url, context, offer_id = sfrtv.get_stream_url(plugin, movie_id, token)

        assert context.upper() == 'REPLAY'
        assert re.match(r'^https://.+\.mpd', video_url)

