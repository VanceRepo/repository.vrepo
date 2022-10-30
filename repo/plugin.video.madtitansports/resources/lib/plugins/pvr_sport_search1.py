###########################################
#     GIVE CREDIT WHERE CREDIT IS DUE     #
#                                         #
#          T4ILS AND JETJET               #
###########################################




import json, sys, time, operator, os, requests,base64
from ..util.dialogs import link_dialog
from xbmcvfs import translatePath
from concurrent.futures import ThreadPoolExecutor
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
from resources.lib.plugin import Plugin
from datetime import datetime, timedelta
import calendar, inputstreamhelper
from jetextractors import extractor
from resources.lib.plugin import run_hook
import urllib.parse

import operator, traceback

CACHE_TIME = 0  # change to wanted cache time in seconds

addon_fanart = xbmcaddon.Addon().getAddonInfo('fanart')
addon_icon = xbmcaddon.Addon().getAddonInfo('icon')

class DirectSearch(Plugin):
    name = "pvr_sport_search1"
    priority = 100

    @property
    def search_include(self):
        r = requests.get(base64.b64decode("aHR0cHM6Ly9tYWduZXRpYzEucmF0cGFjay5hcHBib3hlcy5jby9NQURfVElUQU5fU1BPUlRTL1NQT1JUUy9zZWFyY2hfaW5jbHVkZTEuanNvbg==").decode("utf-8")).json()
        return r

    def process_item(self, item):
        if self.name in item:
            link = item.get(self.name, "")
            thumbnail = item.get("thumbnail", "")
            fanart = item.get("fanart", "")
            icon = item.get("icon", "")
            if link.startswith("search"):
                item["is_dir"] = True
                item["link"] = f"{self.name}/{link}"
                list_item = xbmcgui.ListItem(item.get("title", item.get("name", "")), offscreen=True)
                list_item.setArt({"thumb": thumbnail, "fanart": fanart})
                item["list_item"] = list_item
                return item
        
            
    def routes(self, plugin):
        @plugin.route(f"/{self.name}/search/<path:query>")
        def search(query):
            query = urllib.parse.unquote_plus(query)
            if query == "*":
                query = xbmcgui.Dialog().input("Search game")
                if query == "": return
            games = extractor.search_extractors(query, include=self.search_include)
            empty_date = datetime(year=2030, month=12, day=31)
            jen_list = []
            for game in games:
                jen_data = {
                    "title": "[COLORdodgerblue]%s[COLORwhite] |[B][I] %s[/B][/I]\n  [COLORred]%s | %s[/COLOR]" % (game.league.replace("'", "") if game.league is not None else "", game.title, game.extractor, format_time(game.starttime)),
                    "thumbnail": game.icon,
                    "fanart": game.icon,
                    "summary": game.title,
                    "sportjetextractors": [link.to_dict() for link in game.links],
                    "time": game.starttime.timestamp() if game.starttime != None else empty_date.timestamp(),
                    "type": "item"
                }
                jen_list.append(jen_data)
            
            jen_list = sorted(jen_list, key=lambda x: x["time"])
            jen_list = [run_hook("process_item", item) for item in jen_list]
            jen_list = [run_hook("get_metadata", item, return_item_on_failure=True) for item in jen_list]
            run_hook("display_list", jen_list)

        @plugin.route(f"/{self.name}/search_dialog/<path:query>")
        def search_dialog(query):
            query = urllib.parse.unquote_plus(query)
            if query == "*":
                query = xbmcgui.Dialog().input("Search game")
                if query == "": return
            games = extractor.search_extractors(query, include=self.search_include)
            empty_date = datetime(year=2030, month=12, day=31)
            jen_list = []
            for game in games:
                jen_data = {
                    "title": "[COLORdodgerblue]%s[COLORwhite] |[B][I] %s[/B][/I]\n  [COLORred]%s | %s[/COLOR]" % (game.league.replace("'", "") if game.league is not None else "", game.title, game.extractor, format_time(game.starttime)),
                    "thumbnail": game.icon,
                    "fanart": game.icon,
                    "summary": game.title,
                    "sportjetextractors": [link.to_dict() for link in game.links],
                    "time": game.starttime.timestamp() if game.starttime != None else empty_date.timestamp(),
                    "type": "item"
                }
                jen_list.append(jen_data)
            
            idx = link_dialog([game["title"] for game in jen_list], return_idx=True, hide_links=False)
            if idx == None:
                return True

            run_hook("play_video", json.dumps(jen_list[idx]))



def format_time(date):
    return utc_to_local(date).strftime("%m/%d %I:%M %p") if date != None else ""

# https://stackoverflow.com/questions/4563272/convert-a-python-utc-datetime-to-a-local-datetime-using-only-python-standard-lib
def utc_to_local(utc_dt):
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)


#"Direct_CH","Aust","Direct_CH2","Inter_sports","Sling","USTVGO","Yahoo Sports"