# -*- coding: utf-8 -*-
from windows import BaseDialog
from modules.settings import get_art_provider
from modules.kodi_utils import addon_icon, addon_fanart, local_string as ls
# from modules.kodi_utils import logger

class NextEpisodeDialog(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.is_canceled = False
		self.meta = kwargs.get('meta')
		self.make_items()
		self.set_properties()

	def run(self):
		self.doModal()
		self.clearProperties()

	def iscanceled(self):
		return self.is_canceled

	def onAction(self, action):
		if action in self.closing_actions:
			self.is_canceled = True
			self.close()

	def make_items(self):
		self.poster_main, self.poster_backup, self.fanart_main, self.fanart_backup, self.clearlogo_main, self.clearlogo_backup = get_art_provider()
		self.title = self.meta['title']
		self.year = str(self.meta['year'])
		self.fanart = self.meta.get('custom_fanart') or self.meta.get(self.fanart_main) or self.meta.get(self.fanart_backup) or addon_fanart
		self.clearlogo = self.meta.get('custom_clearlogo') or self.meta.get(self.clearlogo_main) or self.meta.get(self.clearlogo_backup) or ''
		self.text = '%s[CR][CR][CR][B]%s - %02dx%02d[/B] - %s[CR][CR]%s' % (ls(32801), self.title, self.meta['season'], self.meta['episode'], self.meta['ep_name'], self.meta['plot'])

	def set_properties(self):
		self.setProperty('title', self.title)
		self.setProperty('fanart', self.fanart)
		self.setProperty('clearlogo', self.clearlogo)
		self.setProperty('text', self.text)
