from PyQt5.QtWidgets import QTextEdit, QSizePolicy

from commons.common import Common


class GrowingTextEdit(QTextEdit):

    def __init__(self, *args, **kwargs):
        super(GrowingTextEdit, self).__init__(*args, **kwargs)
        self.document().contentsChanged.connect(self.size_change)

        self.heightMin = 0
        self.heightMax = 65000
        self.setVerticalScrollBarPolicy(1)

    def size_change(self):
        doc_height = self.document().size().height()
        if self.heightMin <= doc_height <= self.heightMax:
            self.setMinimumHeight(doc_height)
