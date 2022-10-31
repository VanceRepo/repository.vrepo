# -*- coding: utf-8 -*-
from modules import kodi_utils
from modules.settings import skin_location
from modules.utils import manual_function_import

window_xml_dialog, logger, player, notification, make_listitem = kodi_utils.window_xml_dialog, kodi_utils.logger, kodi_utils.player, kodi_utils.notification, kodi_utils.make_listitem
build_url, execute_builtin, set_property, get_property, sleep = kodi_utils.build_url, kodi_utils.execute_builtin, kodi_utils.set_property, kodi_utils.get_property, kodi_utils.sleep
closing_actions, selection_actions, context_actions = kodi_utils.window_xml_closing_actions, kodi_utils.window_xml_selection_actions, kodi_utils.window_xml_context_actions
info_action, get_infolabel = kodi_utils.window_xml_info_action, kodi_utils.get_infolabel

def open_window(import_info, skin_xml, **kwargs):
	'''
	import_info: tuple with ('module', 'function')
	'''
	try:
		xml_window = create_window(import_info, skin_xml, **kwargs)
		choice = xml_window.run()
		del xml_window
		return choice
	except Exception as e:
		logger('error in open_window', str(e))

def create_window(import_info, skin_xml, **kwargs):
	'''
	import_info: tuple with ('module', 'function')
	'''
	try:
		function = manual_function_import(*import_info)
		args = (skin_xml, skin_location())
		xml_window = function(*args, **kwargs)
		return xml_window
	except Exception as e:
		logger('error in create_window', str(e))
		return notification(32574)

class BaseDialog(window_xml_dialog):
	def __init__(self, *args):
		window_xml_dialog.__init__(self, args)
		self.closing_actions, self.selection_actions, self.context_actions, self.info_action, self.player = closing_actions, selection_actions, context_actions, info_action, player

	def make_listitem(self):
		return make_listitem()

	def build_url(self, params):
		return build_url(params)

	def execute_code(self, command):
		return execute_builtin(command)
	
	def get_position(self, window_id):
		return self.getControl(window_id).getSelectedPosition()

	def get_listitem(self, window_id):
		return self.getControl(window_id).getSelectedItem()

	def make_contextmenu_item(self, label, action, params):
		cm_item = self.make_listitem()
		cm_item.setProperty('label', label)
		cm_item.setProperty('action', action % self.build_url(params))
		return cm_item

	def get_infolabel(self, label):
		return get_infolabel(label)
	
	def open_window(self, import_info, skin_xml, **kwargs):
		return open_window(import_info, skin_xml, **kwargs)

	def sleep(self, time):
		sleep(time)

	def set_home_property(self, prop, value):
		set_property('fen.%s' % prop, value)

	def get_home_property(self, prop):
		return get_property('fen.%s' % prop)

	def get_attribute(self, obj, attribute):
		return getattr(obj, attribute)

	def set_attribute(self, obj, attribute, value):
		return setattr(obj, attribute, value)
