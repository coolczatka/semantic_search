from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QLineEdit, QPushButton, QWidget, QVBoxLayout, QComboBox, \
    QApplication, QPlainTextEdit, QGridLayout, QLabel
import sys, traceback
from SemanticSearchEngine import SemanticSearchEngine
import re
from xml.etree.ElementTree import iterparse

def loadCorpusMock():
    ye = open('YorkEngland.txt', 'r')
    yeText = ye.read()
    ye.close()
    ya = open('YorkAustralia.txt', 'r')
    yaText = ya.read()
    ya.close()
    ny = open('NewYork.txt', 'r')
    nyText = ny.read()
    ny.close()
    return [yeText, yaText, nyText], ['YorkEngland', 'YorkAustraila', 'NewYork']

def loadCorpus():
    file_path = r"./enwiki-20211201-pages-articles-multistream.xml"
    corpus = []
    title = []
    page_flag = False
    title_good = False
    counter = 0
    print("--parsing start--")

    for event, elem in iterparse(file_path, events=("start", "end")):
        if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}page" and event == "start":
            page_flag = True
        if page_flag:
            if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}title" and event == "end":
                title_good = True
                title.append(elem.text)
            if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}text" and event == "end":
                parsed = elem.text
                if parsed.startswith('#REDIRECT'):
                    title.pop()
                else:
                    parsed = re.sub("\{\{.*?\}\}", "", parsed)
                    parsed = re.sub("\n", "", parsed)
                    parsed = parsed.split("==")[0]
                    parsed = re.sub("\\'", "", parsed)
                    parsed = re.sub("(\[\[Category\:.*?\]\])|(\[\[File\:.*?\]\])", "", parsed)
                    parsed = re.sub("\[\[", "", parsed)
                    parsed = re.sub("\|.*?\]\]", "", parsed)
                    parsed = re.sub("\]\]", "", parsed)
                    parsed = re.sub("\<\!\-\-.*?\-\-\>", "", parsed)
                    parsed = re.sub("\<ref\>.*?\<\/ref\>", "", parsed)
                    # parsed = re.sub("\=\= See also \=\=.*", "aa", parsed)
                    corpus.append(parsed.lower())
        if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}page" and event == "end":
            counter += 1
            page_flag = False
            title_good = False
        if counter > 5000:
            break
    print("--parsing end: ", len(title), " records--")

    return corpus, title

class MainWindow(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setGeometry(50, 50, 500, 400)
        self.setWindowTitle("Semantic search engine")

        cw = QWidget(self)
        self.setCentralWidget(cw)
        layout = QVBoxLayout(cw)

        topBarLayout = QHBoxLayout(self)
        self.searchbox = QLineEdit(self)
        self.triggerButton = QPushButton('Search')
        self.triggerButton.clicked.connect(self.search)
        self.searchbox.returnPressed.connect(self.search)
        topBarLayout.addWidget(self.searchbox)
        topBarLayout.addWidget(self.triggerButton)
        self.topBar = QWidget(self)
        self.topBar.setLayout(topBarLayout)

        layout.addWidget(self.topBar)

        self.gridlayoutW = QWidget()
        glay = QGridLayout()
        self.vectorTypeCombobox = QComboBox()
        self.vectorTypeLabel = QLabel('Vector type')
        self.vectorTypeCombobox.addItems(['BoW', 'TFIDF'])
        self.distanceCombobox = QComboBox()
        self.distanceLabel = QLabel('Distance')
        self.distanceCombobox.addItems(['L1', 'L2', 'Cosine'])
        self.decompositionAlgCombobox = QComboBox()
        self.dalabel = QLabel('Decomposition algorithm')
        self.decompositionAlgCombobox.addItems(['SVD', 'PCA', 'LDiA'])
        self.nInput = QLineEdit()
        self.nLabel = QLabel('N - compositions')
        self.nInput.setText('1')


        glay.addWidget(self.vectorTypeLabel, 0, 0)
        glay.addWidget(self.vectorTypeCombobox, 0, 1)
        glay.addWidget(self.distanceLabel, 1, 0)
        glay.addWidget(self.distanceCombobox, 1, 1)
        glay.addWidget(self.dalabel, 2, 0)
        glay.addWidget(self.decompositionAlgCombobox, 2, 1)
        glay.addWidget(self.nLabel, 3, 0)
        glay.addWidget(self.nInput, 3, 1)
        self.gridlayoutW.setLayout(glay)

        layout.addWidget(self.gridlayoutW)

        self.output = QPlainTextEdit()
        layout.addWidget(self.output)

    def search(self):
        try:
            vectortype = self.vectorTypeCombobox.currentText().lower()
            distance = self.distanceCombobox.currentText().lower()
            da = self.decompositionAlgCombobox.currentText().lower()
            n = int(self.nInput.text())
            question = self.searchbox.text().lower()
            sse = SemanticSearchEngine(distance, vectortype, da, n)
            corpus, labels = loadCorpus() # loadCorpusMock()
            sse.loadData(corpus, labels)
            answer = sse.answerQuestion(question)
            self.output.setPlainText(answer)
        except Exception as e:
            print(traceback.format_exc())

if __name__ == '__main__':
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec_())
