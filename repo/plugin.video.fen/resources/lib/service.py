# -*- coding: utf-8 -*-
from modules import service_functions
from modules.kodi_utils import Thread, get_property, xbmc_monitor, make_settings_dict, make_window_properties, get_setting, logger, local_string as ls

fen_str = ls(32036).upper()
OnNotificationActions = service_functions.OnNotificationActions()

class FenMonitor(xbmc_monitor):
	def __init__ (self):
		xbmc_monitor.__init__(self)
		self.startUpServices()
	
	def startUpServices(self):
		try: service_functions.InitializeDatabases().run()
		except Exception as e: logger('error in service: InitializeDatabases', str(e))
		Thread(target=service_functions.DatabaseMaintenance().run).start()
		try: service_functions.CheckSettings().run()
		except Exception as e: logger('error in service: DatabaseMaintenance', str(e))
		try: service_functions.CleanSettings().run()
		except Exception as e: logger('error in service: CleanSettings', str(e))
		try: service_functions.FirstRunActions().run()
		except Exception as e: logger('error in service: FirstRunActions', str(e))
		try: service_functions.ReuseLanguageInvokerCheck().run()
		except Exception as e: logger('error in service: ReuseLanguageInvokerCheck', str(e))
		Thread(target=service_functions.TraktMonitor().run).start()
		Thread(target=service_functions.CustomActions().run, args=('context_menu',)).start()
		Thread(target=service_functions.CustomActions().run, args=('info_dialog',)).start()
		try: service_functions.ClearSubs().run()
		except Exception as e: logger('error in service: ClearSubs', str(e))
		try: service_functions.AutoRun().run()
		except Exception as e: logger('error in service: AutoRun', str(e))

	def onSettingsChanged(self):
		if get_property('fen_pause_onSettingsChanged') != 'true':
			make_settings_dict()
			make_window_properties(override=True)

	def onNotification(self, sender, method, data):
		OnNotificationActions.run(sender, method, data)

	def onAction(self, action):
		pass

logger(fen_str, 'Main Monitor Service Starting')
logger(fen_str, 'Settings Monitor Service Starting')
FenMonitor().waitForAbort()
logger(fen_str, 'Settings Monitor Service Finished')
logger(fen_str, 'Main Monitor Service Finished')