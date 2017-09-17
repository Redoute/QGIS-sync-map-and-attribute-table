''' Sync map and attribute table

Kai Borgolte, FORPLAN DR. SCHMIEDEL, 18.09.2017 '''

from table_canvas_sync_plugin import Table_canvas_sync

def classFactory(iface):
    return Table_canvas_sync(iface)