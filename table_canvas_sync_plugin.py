''' Sync map and attribute table

Kai Borgolte, FORPLAN DR. SCHMIEDEL, 18.09.2017 '''

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt4.QtGui import QAction
from qgis.core import QgsFeature, QgsFeatureRequest, QgsApplication
from qgis.gui import QgsAttributeTableFilterModel
import sip

class Table_canvas_sync(QObject):

    currentChanged = pyqtSignal()

    def __init__(self, iface):
        QObject.__init__(self)
        self.name = 'Sync map and attribute table'
        self.iface = iface
        self.syncedTable = None
        self.currentChanged.connect(self.moveCanvas)

    def initGui(self):
        mw = self.iface.mainWindow()
        self.actionToggle = QAction('&Toggle synchronizing', mw, triggered=self.toggle)
        self.iface.addPluginToVectorMenu('&' + self.name, self.actionToggle)
        # doesn't work in undocked attribute table
        self.iface.registerMainWindowAction(self.actionToggle, 'F12')

    def unload(self):
        self.stopsync()
        self.iface.unregisterMainWindowAction(self.actionToggle)
        self.iface.removePluginVectorMenu('&' + self.name, self.actionToggle)

    @pyqtSlot()
    def stopsync(self):
        if self.syncedTable is not None:
            self.syncedTable = None
            bar = self.iface.messageBar()
            bar.pushMessage(self.name, 'Synchronizing stopped', bar.INFO, 3)

    @pyqtSlot()
    def moveCanvas(self):
        st = self.syncedTable
        ci = st.currentIndex()
        if self.lastRow != ci.row():
            model = sip.cast(ci.model(), QgsAttributeTableFilterModel)
            fid = model.rowToId(ci)
            layer = model.layer()
            f = QgsFeature()
            layer.getFeatures(QgsFeatureRequest(fid)).nextFeature(f)
            c = f.constGeometry().centroid().asPoint()
            mc = self.iface.mapCanvas()
            ms = mc.mapSettings()
            mc.setCenter(ms.layerToMapCoordinates(layer, c))
            mc.refresh()
            self.lastRow = ci.row()

    def eventFilter(self, object, event):
        st = self.syncedTable
        if st is not None and object == st.viewport() and event.type() == event.Paint:
            if st.currentIndex() != self.lastRow:
                self.currentChanged.emit()
        return False

    @pyqtSlot()
    def toggle(self):
        bar = self.iface.messageBar()
        st = self.syncedTable
        if st is None:
            st = QgsApplication.focusWidget()
            if st.objectName() == 'mTableView':
                self.syncedTable = st
                self.lastRow = -1
                st.destroyed.connect(self.stopsync)
                st.viewport().installEventFilter(self)
                self.moveCanvas()
                bar.pushMessage(self.name, 'Synchronizing started', bar.INFO, 3)
            else:
                self.syncedTable = None
                bar.pushMessage(self.name, "Can't start - first select docked attribute table",
                                bar.INFO, 10)
        else:
            st.viewport().removeEventFilter(self)
            self.stopsync()
