from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont

class CustomPlainTextEdit(QPlainTextEdit):
    """
    =================================================================
    webui同様にctrl + ↑↓でのウェイト変更に対応したQPlainTextEdit
    また、フォントサイズを10に設定している
    =================================================================
    """
    def __init__(self):
        super().__init__()
        
        # font設定
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
    
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Up:
                self.isPlus = True
                self.isMinus = False
            elif event.key() == Qt.Key_Down:
                self.isPlus = False
                self.isMinus = True
            else:
                return super().keyPressEvent(event)
            
            if not self.isPlus and not self.isMinus: return
            
            self.cursor = self.textCursor()
            self.selectionStart = self.cursor.selectionStart()
            self.selectionEnd = self.cursor.selectionEnd()
            self.text = self.toPlainText()
            
            if not self.selectCurrentParenthesisBlock("(", ")") and \
                not self.selectCurrentParenthesisBlock("<", ">"):
                    self.selectCurrentWord()
            self.changeWeight()
        else:
            super().keyPressEvent(event)
        
        # Don't pass the event to the base class handler (prevents default)
        return
    
    def selectCurrentParenthesisBlock(self, OPEN, CLOSE):
        if self.selectionStart != self.selectionEnd: return False
        
        # Find opening parenthesis around current cursor
        before = self.text[:self.selectionStart]
        beforeParen = before.rfind(OPEN)
        if beforeParen == -1: return False
        beforeParenClose = before.rfind(CLOSE)
        while beforeParenClose != -1 and beforeParenClose > beforeParen:
            beforeParen = before.rfind(OPEN, 0, beforeParen)
            beforeParenClose = before.rfind(CLOSE, 0, beforeParenClose)
        
        # Find closing parenthesis around current cursor
        after = self.text[self.selectionStart:]
        afterParen = after.find(CLOSE)
        if afterParen == -1: return False
        
        afterParenOpen = after.find(OPEN)
        while afterParenOpen != -1 and afterParen > afterParenOpen:
            afterParen = after.find(CLOSE, 0, afterParen)
            afterParenOpen = after.find(OPEN, 0, afterParenOpen)
        
        if beforeParen == -1 or afterParen == -1: return False
        
        # Set the selection to the text between the parenthesis
        parenContent = self.text[beforeParen + 1:self.selectionStart + afterParen]
        lastColon = parenContent.rfind(":")
        if lastColon == -1: return False

        self.selectionStart = beforeParen + 1
        self.selectionEnd = self.selectionStart + lastColon
        self.cursor.setPosition(self.selectionStart)
        self.cursor.setPosition(self.selectionEnd, QTextCursor.KeepAnchor)
        self.setTextCursor(self.cursor)
        return True
    
    def selectCurrentWord(self):
        if self.selectionStart != self.selectionEnd: return False
        delimiters =  " \r\n\t()<>,"
        
        # seek backward until to find beggining
        while self.selectionStart > 0 and self.text[self.selectionStart - 1] not in delimiters:
            self.selectionStart -= 1
        
        while self.selectionEnd < len(self.text) and self.text[self.selectionEnd] not in delimiters:
            self.selectionEnd += 1
        
        self.cursor.setPosition(self.selectionStart)
        self.cursor.setPosition(self.selectionEnd, QTextCursor.KeepAnchor)
        self.setTextCursor(self.cursor)
        return True
    
    def changeWeight(self):
        closeCharacter = ")"
        delta = 0.1

        if self.selectionStart > 0 and self.text[self.selectionStart - 1] == "<":
            closeCharacter = ">"
        elif self.selectionStart == 0 or self.text[self.selectionStart - 1] != "(":
            # do not include spaces at the end
            while (self.selectionEnd > self.selectionStart and self.text[self.selectionEnd - 1] == " "):
                self.selectionEnd -= 1
            
            if self.selectionStart == self.selectionEnd:
                return
            
            self.text = "{}({}:1.0){}".format(self.text[:self.selectionStart], self.text[self.selectionStart:self.selectionEnd], self.text[self.selectionEnd:])
            self.selectionStart += 1
            self.selectionEnd += 1
        
        end = self.text[self.selectionEnd + 1:].find(closeCharacter) + 1
        
        try:
            weight = float(self.text[self.selectionEnd + 1:self.selectionEnd + end])
        except ValueError:
            return
        
        weight += delta if self.isPlus else -delta
        weight = float("{:.12g}".format(weight))
        if len(str(weight)) == 1:
            weight = str(weight) + ".0"
        
        if closeCharacter == ")" and weight == 1:
            endParenPos = self.text[self.selectionEnd:].find(")")
            self.text = self.text[:self.selectionStart - 1] + self.text[self.selectionStart:self.selectionEnd] + self.text[self.selectionEnd + endParenPos + 1:]
            self.selectionStart -= 1
            self.selectionEnd -= 1
        else:
            self.text = self.text[:self.selectionEnd + 1] + str(weight) + self.text[self.selectionEnd + end:]
        
        # Update the QPlainTextEdit
        self.setFocus()
        self.setPlainText(self.text)
        self.cursor.setPosition(self.selectionStart)
        self.cursor.setPosition(self.selectionEnd, QTextCursor.KeepAnchor)
        self.setTextCursor(self.cursor)
        
        