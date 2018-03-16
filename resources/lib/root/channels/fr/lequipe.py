# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2017  SylvainCecchetto

    This file is part of Catch-up TV & More.

    Catch-up TV & More is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Catch-up TV & More is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with Catch-up TV & More; if not, write to the Free Software Foundation,
    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import re
import ast
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

# TO DO
# Get Info Live


URL_ROOT = 'https://www.lequipe.fr'

URL_ROOT_VIDEO_LEQUIPE = 'https://www.lequipe.fr/lachainelequipe/'

URL_REPLAY_VIDEO_LEQUIPE = 'https://www.lequipe.fr/' \
                           'lachainelequipe/morevideos/%s'
# Category_id


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = "list_shows_1"
        return list_shows(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    else:
        return None

CATEGORIES = {
    'tout': URL_ROOT_VIDEO_LEQUIPE,
    'L\'Équipe du Soir': URL_ROOT_VIDEO_LEQUIPE + 'morevideos/1',
    'L\'Équipe d\'Estelle': URL_ROOT_VIDEO_LEQUIPE + 'morevideos/98',
    'Événements': URL_ROOT_VIDEO_LEQUIPE + 'morevideos/66',
    'L\'Équipe du week-end': URL_ROOT_VIDEO_LEQUIPE + 'morevideos/64',
    'La Grande Soirée': URL_ROOT_VIDEO_LEQUIPE + 'morevideos/93',
    'Les Grands Docs': URL_ROOT_VIDEO_LEQUIPE + 'morevideos/28',
    'Émission spéciale': URL_ROOT_VIDEO_LEQUIPE + 'morevideos/42'
}

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build shows listing"""
    shows = []

    # Get categories :
    for category_name, category_url in CATEGORIES.iteritems():

        shows.append({
            'label': category_name,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                category_url=category_url,
                page='1',
                category_name=category_name,
                next='list_videos',
                window_title=category_name
            )
        })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    url = params.category_url + '/' + params.page
    file_path = utils.download_catalog(
        url,
        '%s_%s_%s.html' % (
            params.channel_name,
            params.category_name,
            params.page))
    root_html = open(file_path).read()
    root_soup = bs(root_html, 'html.parser')

    category_soup = root_soup.find_all(
        'a',
        class_='colead')

    for program in category_soup:

        # Get Video_ID
        url = URL_ROOT + program['href'].encode('utf-8')
        html_video_equipe = utils.get_webcontent(url)
        video_id = re.compile(
            r'www.dailymotion.com/embed/video/(.*?)\?',
            re.DOTALL).findall(html_video_equipe)[0]

        title = program.find(
            'h2').get_text().encode('utf-8')
        colead__image = program.find(
            'div',
            class_='colead__image')
        img = colead__image.find(
            'img')['data-src'].encode('utf-8')

        date = colead__image.find(
            'span',
            class_='colead__layerText colead__layerText--bottomleft'
        ).get_text().strip().encode('utf-8')  # 07/09/17 | 01 min
        date = date.split('/')
        day = date[0]
        mounth = date[1]
        year = '20' + date[2].split(' ')[0]

        date = '.'.join((day, mounth, year))
        aired = '-'.join((year, mounth, day))

        duration_string = colead__image.find(
            'span',
            class_='colead__layerText colead__layerText--bottomleft'
        ).get_text().strip().encode('utf-8')
        duration_list = duration_string.split(' ')
        duration = int(duration_list[2]) * 60

        info = {
            'video': {
                'title': title,
                'aired': aired,
                'date': date,
                'duration': duration,
                'year': year,
                'mediatype': 'tvshow'
            }
        }

        download_video = (
            common.GETTEXT('Download'),
            'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                action='download_video',
                module_path=params.module_path,
                module_name=params.module_name,
                video_id=video_id) + ')'
        )
        context_menu = []
        context_menu.append(download_video)

        videos.append({
            'label': title,
            'thumb': img,
            'fanart': img,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='play_r',
                video_id=video_id
            ),
            'is_playable': True,
            'info': info,
            'context_menu': context_menu
        })

    # More videos...
    videos.append({
        'label': common.ADDON.get_localized_string(30700),
        'url': common.PLUGIN.get_url(
            module_path=params.module_path,
            module_name=params.module_name,
            action='replay_entry',
            category_url=params.category_url,
            category_name=params.category_name,
            next='list_videos',
            page=str(int(params.page) + 1),
            update_listing=True,
            previous_listing=str(videos)
        )
    })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_PLAYCOUNT,
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    video_id = ''

    html_live_equipe = utils.get_webcontent(URL_ROOT_VIDEO_LEQUIPE)
    video_id = re.compile(
        r'<iframe src="//www.dailymotion.com/embed/video/(.*?)\?',
        re.DOTALL).findall(html_live_equipe)[0]

    params['next'] = 'play_l'
    params['video_id'] = video_id
    return get_video_url(params)


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_r':
        return resolver.get_stream_dailymotion(params.video_id, False)
    elif params.next == 'play_l':
        return resolver.get_stream_dailymotion(params.video_id, False)
    elif params.next == 'download_video':
        return resolver.get_stream_dailymotion(params.video_id, True)
