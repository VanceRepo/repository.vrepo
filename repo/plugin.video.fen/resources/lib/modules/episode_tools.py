# -*- coding: utf-8 -*-
from random import choice
from datetime import date
from windows import open_window
from apis.trakt_api import trakt_get_hidden_items
from metadata import tvshow_meta, season_episodes_meta, all_episodes_meta
from modules import kodi_utils, settings
from modules.sources import Sources
from modules.player import FenPlayer
from modules.watched_status import get_next_episodes, get_watched_info_tv
from modules.utils import adjust_premiered_date, get_datetime, make_thread_list, title_key
# logger = kodi_utils.logger

ls, sys, build_url, json, notification, run_plugin = kodi_utils.local_string, kodi_utils.sys, kodi_utils.build_url, kodi_utils.json, kodi_utils.notification, kodi_utils.run_plugin
Thread, focus_index, get_property, set_property = kodi_utils.Thread, kodi_utils.focus_index, kodi_utils.get_property, kodi_utils.set_property
make_listitem, add_dir, add_items, sleep = kodi_utils.make_listitem, kodi_utils.add_dir, kodi_utils.add_items, kodi_utils.sleep
set_content, end_directory, set_view_mode = kodi_utils.set_content, kodi_utils.end_directory, kodi_utils.set_view_mode
trakt_icon, addon_fanart, fen_clearlogo = kodi_utils.get_icon('trakt'), kodi_utils.addon_fanart, kodi_utils.addon_clearlogo
included_str, excluded_str, heading = ls(32804).upper(), ls(32805).upper(), ls(32806)

def build_next_episode_manager():
	def build_content(item):
		try:
			listitem = make_listitem()
			tmdb_id, title = item['media_ids']['tmdb'], item['title']
			if tmdb_id in exclude_list: color, action, status, sort_value = 'red', 'unhide', excluded_str, 1
			else: color, action, status, sort_value = 'green', 'hide', included_str, 0
			display = '[COLOR=%s][%s][/COLOR] %s' % (color, status, title)
			url_params = {'mode': 'trakt.hide_unhide_trakt_items', 'action': action, 'media_type': 'shows', 'media_id': tmdb_id, 'section': 'progress_watched'}
			url = build_url(url_params)
			listitem.setLabel(display)
			listitem.setArt({'poster': trakt_icon, 'fanart': addon_fanart, 'icon': trakt_icon, 'clearlogo': fen_clearlogo})
			listitem.setInfo('video', {'plot': ' '})
			append({'listitem': (url, listitem, False), 'sort_value': sort_value, 'sort_title': title})
		except: pass
	handle = int(sys.argv[1])
	list_items = []
	append = list_items.append
	show_list = get_next_episodes(get_watched_info_tv(1))
	try: exclude_list = trakt_get_hidden_items('progress_watched')
	except: exclude_list = []
	threads = list(make_thread_list(build_content, show_list))
	[i.join() for i in threads]
	item_list = sorted(list_items, key=lambda k: (k['sort_value'], title_key(k['sort_title'], settings.ignore_articles())), reverse=False)
	item_list = [i['listitem'] for i in item_list]
	add_dir({'mode': 'nill'}, '[I][COLOR=grey2]%s[/COLOR][/I]' % heading.upper(), handle, iconImage='settings', isFolder=False)
	add_items(handle, item_list)
	set_content(handle, '')
	end_directory(handle, cacheToDisc=False)
	set_view_mode('view.main', '')
	focus_index(1)

def nextep_playback_info(meta):
	def _build_next_episode_play():
		ep_data = season_episodes_meta(season, meta, settings.metadata_user_info())
		if not ep_data: return 'no_next_episode'
		ep_data = [i for i in ep_data if i['episode'] == episode][0]
		airdate = ep_data['premiered']
		d = airdate.split('-')
		episode_date = date(int(d[0]), int(d[1]), int(d[2]))
		if current_date < episode_date: return 'no_next_episode'
		custom_title = meta_get('custom_title', None)
		title = custom_title or meta_get('title')
		display_name = '%s - %dx%.2d' % (title, int(season), int(episode))
		meta.update({'media_type': 'episode', 'rootname': display_name, 'season': season, 'ep_name': ep_data['title'],
					'episode': episode, 'premiered': airdate, 'plot': ep_data['plot']})
		url_params = {'mode': 'play_media', 'media_type': 'episode', 'tmdb_id': tmdb_id, 'tvshowtitle': meta_get('rootname'), 'season': season,
					'episode': episode, 'background': 'true'}
		if custom_title: url_params['custom_title'] = custom_title
		if 'custom_year' in meta: url_params['custom_year'] = meta_get('custom_year')
		return url_params
	meta_get = meta.get
	tmdb_id, current_season, current_episode = meta_get('tmdb_id'), int(meta_get('season')), int(meta_get('episode'))
	try:
		current_date = get_datetime()
		season_data = meta_get('season_data')
		curr_season_data = [i for i in season_data if i['season_number'] == current_season][0]
		season = current_season if current_episode < curr_season_data['episode_count'] else current_season + 1
		episode = current_episode + 1 if current_episode < curr_season_data['episode_count'] else 1
		nextep_info = _build_next_episode_play()
	except: nextep_info = 'error'
	return meta, nextep_info

def execute_nextep(meta, nextep_settings):
	try:
		action = None
		player = FenPlayer()
		display_nextep_popup = nextep_settings['window_time']
		nextep_meta, nextep_params = nextep_playback_info(meta)
		if nextep_params == 'error': return notification(32574, 3000)
		elif nextep_params == 'no_next_episode': return
		nextep_url = Sources().playback_prep(nextep_params)
		if not nextep_url: return notification(32760, 3000)
		use_window = nextep_settings['alert_method'] == 0
		default_action = nextep_settings['default_action'] if use_window else 'close'
		while player.isPlayingVideo():
			try:
				sleep(200)
				total_time = player.getTotalTime()
				curr_time = player.getTime()
				if round(total_time - curr_time) <= display_nextep_popup:
					if use_window: action = open_window(('windows.next_episode', 'NextEpisode'), 'next_episode.xml', meta=nextep_meta, default_action=default_action)
					else: notification('%s %s S%02dE%02d' % (ls(32801), nextep_meta['title'], nextep_meta['season'], nextep_meta['episode']), 6500, nextep_meta['poster'])
					break
			except: pass
		if not action: action = default_action
		if action == 'cancel': return notification(' '.join([ls(32483), ls(32736)]), 3000)
		set_property('fen_cancel_content_build', 'true')
		if action == 'close':
			while player.isPlayingVideo(): sleep(100)
		# from windows import create_window
		# nextep_dialog = create_window(('windows.next_episode_dialog', 'NextEpisodeDialog'), 'next_episode_dialog.xml', meta=nextep_meta)
		# Thread(target=nextep_dialog.run).start()
		if action == 'play':
			player.stop()
			sleep(1000)
			while player.isPlayingVideo(): sleep(100)
		sleep(2000)
		set_property('fen_cancel_content_build', 'false')
		Thread(target=player.run, args=(nextep_url, nextep_meta)).start()
		# while not player.isPlayingVideo():
		# 	if nextep_dialog.iscanceled(): break
		# 	sleep(100)
		# nextep_dialog.close()
	except: set_property('fen_cancel_content_build', 'false')

def get_random_episode(tmdb_id, continual=False):
	meta_user_info, adjust_hours, current_date = settings.metadata_user_info(), settings.date_offset(), get_datetime()
	tmdb_key = str(tmdb_id)
	meta = tvshow_meta('tmdb_id', tmdb_id, meta_user_info, current_date)
	try: episodes_data = [i for i in all_episodes_meta(meta, meta_user_info) if i['premiered'] and adjust_premiered_date(i['premiered'], adjust_hours)[0] <= current_date]
	except: return
	if continual:
		episode_list = []
		try:
			episode_history = json.loads(get_property('fen_random_episode_history'))
			if tmdb_key in episode_history: episode_list = episode_history[tmdb_key]
			else: set_property('fen_random_episode_history', '')
		except: pass
		first_run = len(episode_list) == 0
		episodes_data = [i for i in episodes_data if not i in episode_list]
		if not episodes_data:
			set_property('fen_random_episode_history', '')
			return get_random_episode(tmdb_id, continual=True)
	else: first_run = True
	chosen_episode = choice(episodes_data)
	if continual:
		episode_list.append(chosen_episode)
		episode_history = {str(tmdb_id): episode_list}
		set_property('fen_random_episode_history', json.dumps(episode_history))
	title, season, episode = meta['title'], int(chosen_episode['season']), int(chosen_episode['episode'])
	query = title + ' S%.2dE%.2d' % (season, episode)
	display_name = '%s - %dx%.2d' % (title, season, episode)
	ep_name, plot = chosen_episode['title'], chosen_episode['plot']
	try: premiered = adjust_premiered_date(chosen_episode['premiered'], adjust_hours)[1]
	except: premiered = chosen_episode['premiered']
	meta.update({'media_type': 'episode', 'rootname': display_name, 'season': season, 'episode': episode, 'premiered': premiered, 'ep_name': ep_name, 'plot': plot})
	if continual: meta['random_continual'] = 'true'
	else: meta['random'] = 'true'
	url_params = {'mode': 'play_media', 'media_type': 'episode', 'tmdb_id': meta['tmdb_id'], 'query': query,
					'tvshowtitle': meta['rootname'], 'season': season, 'episode': episode, 'autoplay': 'true', 'meta': json.dumps(meta)}
	if not first_run: url_params['background'] = 'true'
	return url_params

def play_random(tmdb_id):
	url_params = get_random_episode(tmdb_id)
	if not url_params: return {'pass': True}
	return run_plugin(url_params)

def play_random_continual(tmdb_id):
	url_params = get_random_episode(tmdb_id, continual=True)
	if not url_params: return {'pass': True}
	player = FenPlayer()
	url = Sources().playback_prep(url_params)
	while player.isPlayingVideo(): sleep(100)
	player.run(url, json.loads(url_params['meta']))


