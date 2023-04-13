class CustomDelegate(QStyledItemDelegate):
    def __init__(self, highlight_color, background_color):
        super(CustomDelegate, self).__init__()
        self.highlight_color = highlight_color
        self.background_color = background_color
        self.hover_row = -1
        
    def onHoverIndexChanged(self, index):
        if index is not None:
            self.hover_row = index.row()
        else:
            self.hover_row = -1

    def paint(self, painter: QtGui.QPainter, option, index: QModelIndex) -> None:
        if index.row() == self.hover_row:
            painter.fillRect(option.rect, self.highlight_color)
        else:
            painter.fillRect(option.rect, self.background_color)
        super(CustomDelegate, self).paint(painter, option, index)


class BorderlessTableView(QTableView):
    # Borderless tableview. When hovering, the whole row is selected

    hover_index_changed = pyqtSignal(object)

    def __init__(self, data, parent=None):
        super(BorderlessTableView, self).__init__(parent)
        highlight_color = self.get_hover_color()
        background_color = self.get_background_color()
        self.delegate = CustomDelegate(highlight_color, background_color)
        self.hover_index_changed.connect(self.delegate.onHoverIndexChanged)
        self.setFrameShape(QFrame.Shape.NoFrame)  # Remove frame
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().setVisible(False)  # Hide vertical header
        self.horizontalHeader().setVisible(False)  # Hide horizontal header
        self.setShowGrid(False)  # Hide grid
        self.setItemDelegate(self.delegate)
        self.setModel(self.create_model(data))

    def get_hover_color(self):
        app = QApplication.instance()
        stylesheet = QApplication.styleSheet(app)
        pattern = r'QTreeView::branch:!selected:hover\s*{\s*background-color:\s*rgba\((\d+\.\d+),\s*(\d+\.\d+),\s*(\d+\.\d+),\s*(\d+\.\d+)\);'

        match = re.search(pattern, stylesheet)

        if match:
            r, g, b, a = match.groups()
            color = QColor(int(float(r)), int(float(g)), int(float(b)), int(float(a) * 255.0))  # a is 0 - 1.0, not int
            return color
            # return QColor(231, 231, 231, 255)

        else:
            return QColor(231, 231, 231, 255)

    def get_background_color(self):
        app = QApplication.instance()
        stylesheet = QApplication.styleSheet(app)
        pattern = r'QWidget\s*{\s*background-color:\s*rgba\((\d+\.\d+),\s*(\d+\.\d+),\s*(\d+\.\d+),\s*(\d+\.\d+)\);'

        match = re.search(pattern, stylesheet)

        if match:
            r, g, b, a = match.groups()
            color = QColor(int(float(r)), int(float(g)), int(float(b)), int(float(a) * 255.0))  # a is 0 - 1.0, not int
            return color

        else:
            return QColor(231, 231, 231, 255)  # Just a gray hover color

    def leaveEvent(self, a0) -> None:
        self.hover_index_changed.emit(None)

    def mouseMoveEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid():
            self.hover_index_changed.emit(index)
        else:
            self.hover_index_changed.emit(None)
        super().mouseMoveEvent(event)

    def create_model(self, data):
        # Create a QStandardItemModel to store the data
        # Example data = [['A', 'B', 'C'], ['D', 'E', 'F'], ['G', 'H', 'I']]
        model = QStandardItemModel()
        for row in data:
            q_items = [QStandardItem(str(item)) for item in row]
            model.appendRow(q_items)
