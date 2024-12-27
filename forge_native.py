from forge_callable import ForgeCallable
from forge_function import ForgeFunction
from forge_class import ForgeClass
from forge_instance import ForgeInstance
from error import FunctionException
from forge_array import ForgeArray
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QCheckBox, QLineEdit, QMessageBox, QComboBox, QListWidget, QPlainTextEdit
from PyQt6.QtCore import QElapsedTimer, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QCursor
from preprocessor import HEADERS
import keyboard

import random
import ctypes
import sys
import math
import time
from pathlib import Path
import datetime

class ForgeNative(ForgeCallable):
    def __init__(self):
        self.name = None

    def arity(self):
        pass

    def call(self, interpreter, arguments):
        pass

    def variadic(self):
        return False

    def __str__(self):
        return "<native fn>"

#CLASSES AND METHODS
class SetHashMap(ForgeNative):
    def __init__(self, parent, token):
        self.name = "set"
        self.parent = parent
        self.token = token

    def arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        if arguments[0] in self.parent.fields:
            self.parent.fields[arguments[0]] = arguments[1]
            return arguments[1]
        elif str(arguments[0]) in self.parent.fields:
            self.parent.fields[str(arguments[0])] = arguments[1]
            return arguments[1]
        else:
            try:
                self.parent.fields[arguments[0]] = arguments[1]
                return arguments[1]
            except TypeError:
                raise FunctionException(f"Undefined property '{arguments[0]}'.", self.name)
            
class GetHashMap(ForgeNative):
    def __init__(self, parent, token):
        self.name = "get"
        self.parent = parent
        self.token = token

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return self.parent.fields.get(arguments[0])# or self.parent.fields.get(str(arguments[0]))
    
class RemoveHashMap(ForgeNative):
    def __init__(self, parent, token):
        self.name = "remove"
        self.parent = parent
        self.token = token

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        try:
            return self.parent.fields.pop(arguments[0])
        except Exception:
            raise FunctionException("Key is not in Hashmap.", self.name)

class RemoveValueHashMap(ForgeNative):
    def __init__(self, parent, token):
        self.name = "removeValue"
        self.parent = parent
        self.token = token

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        try:
            new_dict = {key: value for key, value in self.parent.fields.items()
                if value != arguments[0]}
            self.parent.fields = new_dict
            return self.parent.fields
        except Exception:
            raise FunctionException("Key is not in Hashmap.", self.name)

class ContainsKeyHashMap(ForgeNative):
    def __init__(self, parent, token):
        self.name = "containsKey"
        self.parent = parent
        self.token = token

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return arguments[0] in self.parent.fields.keys()
    
class ContainsValueHashMap(ForgeNative):
    def __init__(self, parent, token):
        self.name = "containsValue"
        self.parent = parent
        self.token = token

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return arguments[0] in self.parent.fields.values()

class HashMap(ForgeInstance):
    name = "HashMap"
    def __init__(self):
        self._class = HashMap
        self.fields = {}
        self.methods = {"set": SetHashMap, "get": GetHashMap, "remove": RemoveHashMap, "removeValue": RemoveValueHashMap, "containsKey": ContainsKeyHashMap, "containsValue": ContainsValueHashMap}

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)
        
    def __str__(self):
        return str(self.fields)
    
class RandomInt(ForgeNative):
    def __init__(self, parent, token):
        self.name = "int"
        self.parent = parent
        self.token = token

    def arity(self):
        return 2
    
    def variadic(self):
        return True
    
    def call(self, interpreter, arguments):
        if len(arguments) > 2:
            raise FunctionException("Expect max 2 arguments: (min: num !optional), (max: num !optional).", self.name)
        _min = 0
        _max = 0
        if len(arguments) > 0:
            if not isinstance(arguments[0], float):
                raise FunctionException("First argument must be 'num', the minimum of random (inclusive).")
            _min = int(arguments[0])
        if len(arguments) > 1:
            if not isinstance(arguments[1], float):
                raise FunctionException("Second argument must be 'num', the maximum of random (inclusive).")
            _max = int(arguments[1])
        return random.randint(_min, _max)
    
class RandomNum(ForgeNative):
    def __init__(self, parent, token):
        self.name = "num"
        self.parent = parent
        self.token = token

    def arity(self):
        return 2
    
    def variadic(self):
        return True
    
    def call(self, interpreter, arguments):
        if len(arguments) > 2:
            raise FunctionException("Expect max 2 arguments: (min: num !optional), (max: num !optional).", self.name)
        _min = 0
        _max = 0
        if len(arguments) > 0:
            if not isinstance(arguments[0], float):
                raise FunctionException("First argument must be 'num', the minimum of random (inclusive).")
            _min = arguments[0]
        if len(arguments) > 1:
            if not isinstance(arguments[1], float):
                raise FunctionException("Second argument must be 'num', the maximum of random (inclusive).")
            _max = arguments[1]
        return random.uniform(_min, _max)
    
class RandomChoice(ForgeNative):
    def __init__(self, parent, token):
        self.name = "choice"
        self.parent = parent
        self.token = token

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], ForgeArray):
            raise FunctionException("First argument must be 'array', the array the method returns a random element from.", self.name)
        return random.choice(arguments[0].elements)

class Random(ForgeInstance):
    name = "Random"
    def __init__(self):
        self._class = Random
        self.fields = {}
        self.methods = {"int": RandomInt, "num": RandomNum, "choice": RandomChoice}

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)

class SetButton(ForgeNative):
    def __init__(self, button, _):
        self.name = "setText"
        self.button = button
    
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], str):
            raise FunctionException("Expect type 'string'.", self.name)
        self.button.fields.get("button").setText(arguments[0])

class GetButton(ForgeNative):
    def __init__(self, button, _):
        self.name = "getText"
        self.button = button
    
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return self.button.fields.get("button").text()
    
class ClickButton(ForgeNative):
    def __init__(self, button, _):
        self.name = "click"
        self.button = button
    
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return self.button.fields.get("button").click()
    
class SetPos(ForgeNative):
    def __init__(self, parent, _):
        self.name = "setPos"
        self.parent = parent
    
    def arity(self):
        return 1 # [x, y]
    
    def call(self, interpreter, arguments):
        dims = arguments[0]
        if not isinstance(dims, ForgeArray) or dims.length() != 2:
            raise FunctionException("Argument must be array of position [x, y].", self.name)
        x = 0
        y = 0
        try:
            x = int(dims.elements[0])
            y = int(dims.elements[1])
        except Exception:
            raise FunctionException("Elements of array must be numbers.", self.name)
        self.parent.fields.get(self.parent.name.lower()).move(x, y)

class GetPos(ForgeNative):
    def __init__(self, parent, _):
        self.name = "getPos"
        self.parent = parent
    
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return ForgeArray([self.parent.fields.get(self.parent.name.lower()).x(), self.parent.fields.get(self.parent.name.lower()).y()])
    
class GetStyle(ForgeNative):
    def __init__(self, parent, _):
        self.name = "getStyle"
        self.parent = parent
    
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return self.parent.fields.get(self.parent.name.lower()).styleSheet()

class SetStyle(ForgeNative):
    def __init__(self, parent, _):
        self.name = "setStyle"
        self.parent = parent
    
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], str):
            raise FunctionException("First argument must be a string.", self.name)
        self.parent.fields.get(self.parent.name.lower()).setStyleSheet(arguments[0])

class GetSize(ForgeNative):
    def __init__(self, parent, _):
        self.name = "getSize"
        self.parent = parent
    
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return ForgeArray([self.parent.fields.get(self.parent.name.lower()).width(), self.parent.fields.get(self.parent.name.lower()).height()])

class SetSize(ForgeNative):
    def __init__(self, parent, _):
        self.name = "setSize"
        self.parent = parent
    
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], ForgeArray):
            raise FunctionException("First argument must be an array of [width, height].", self.name)
        dims = arguments[0]
        width = 0
        height = 0
        try:
            width = int(dims.elements[0])
            height = int(dims.elements[1])
        except Exception:
            raise FunctionException("Elements of array must be numbers.", self.name)
        
        self.parent.fields.get(self.parent.name.lower()).resize(width, height)

class RemoveComponent(ForgeNative):
    def __init__(self, parent, _):
        self.name = "remove"
        self.parent = parent

    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        component_type = self.parent.name.lower()  # Dynamically determine the type
        widget = self.parent.fields.get(component_type)
        if widget is not None:
            widget.deleteLater()
            self.parent.fields[component_type] = None
        else:
            raise FunctionException(f"{self.parent.name} is already removed or not initialized.", self.name)

class Button(ForgeInstance):
    name = "Button"
    def __init__(self, button):
        self._class = Button
        self.fields = {"button": button}
        self.methods = {"setText": SetButton, "getText": GetButton, "click": ClickButton, "setPos": SetPos, "getPos": GetPos, "setStyle": SetStyle, "getStyle": GetStyle, "setSize": SetSize, "getSize": GetSize, "remove": RemoveComponent}

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)
    
class AddButton(ForgeNative):
    def __init__(self, parent, token):
        self.name = "addButton"
        self.parent = parent
        self.token = token

    def arity(self):
        return 5 # text, position, size, callback, style
    
    def variadic(self):
        return True

    def call(self, interpreter, arguments):
        if len(arguments) < 4 or len(arguments) > 5:
            raise FunctionException("Expect at least 4 (max 5) arguments: Text: string, Position: [x, y], Size: [width, height], onClick: function, (style: string !optional).")
        text = arguments[0]
        position = arguments[1]
        size = arguments[2]
        callback = arguments[3]
        style = None
        if len(arguments) == 5:
            style = arguments[4]
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        if not isinstance(callback, ForgeFunction):
            raise FunctionException("Fourth argument must be a callable function.", self.name)
        if style and not isinstance(style, str):
            raise FunctionException("Fifth argument must be a string of the stylesheet.", self.name)
        
        button = QPushButton(text, self.parent.fields.get("window"))
        button.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
        if style:
            button.setStyleSheet(style)
        args = []
        if callback.arity() > 0:
            args.append(Button(button))
        button.clicked.connect(lambda: callback.call(interpreter, args))
        button.show()

        return Button(button)

class SetLabel(ForgeNative):
    def __init__(self, label, _):
        self.name = "set"
        self.label = label
    
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], str):
            raise FunctionException("Expect type 'string'.", self.name)
        self.label.fields.get("label").setText(arguments[0])

class GetLabel(ForgeNative):
    def __init__(self, label, _):
        self.name = "get"
        self.label = label
    
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return self.label.fields.get("label").text()

class Label(ForgeInstance):
    name = "Label"
    def __init__(self, label):
        self._class = Label
        self.fields = {"label": label}
        self.methods = {"set": SetLabel, "get": GetLabel, "setPos": SetPos, "getPos": GetPos, "setStyle": SetStyle, "getStyle": GetStyle, "setSize": SetSize, "getSize": GetSize, "remove": RemoveComponent}

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)

class AddLabel(ForgeNative):
    def __init__(self, parent, token):
        self.name = "addLabel"
        self.parent = parent
        self.token = token

    def arity(self):
        return 3 # text, position, size, style
    
    def variadic(self):
        return True
    
    def call(self, interpreter, arguments):
        if len(arguments) < 3 or len(arguments) > 4:
            raise FunctionException("Expect at least 3 (max 4) arguments: Text: string, Position: [x, y], Size: [width, height], (style: string !optional).")
        text = arguments[0]
        position = arguments[1]
        size = arguments[2]
        style = None
        if len(arguments) == 4:
            style = arguments[3]
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        if style and not isinstance(style, str):
            raise FunctionException("Fourth argument must be a string of the stylesheet.", self.name)
        
        label = QLabel(text, self.parent.fields.get("window"))
        label.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
        if style:
            label.setStyleSheet(style)
        label.show()

        return Label(label)
    
class AddCheckbox(ForgeNative):
    def __init__(self, parent, token):
        self.name = "addCheckbox"
        self.parent = parent
        self.token = token

    def arity(self):
        return 5 # label, position, size, callback, style
    
    def variadic(self):
        return True

    def call(self, interpreter, arguments):
        if len(arguments) < 3 or len(arguments) > 5:
            raise FunctionException('Expect at least 3 (max 5) arguments: Text: str, Position: [x, y], Size: [width, height], (onChange: function !optional), (style: str !optional).', self.name)
        text = arguments[0]
        position = arguments[1]
        size = arguments[2]
        callback = None
        if len(arguments) >= 4:
            callback = arguments[3]
        style = None
        if len(arguments) == 5:
            style = arguments[4]
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        if callback and not isinstance(callback, ForgeFunction):
            raise FunctionException("Fourth argument must be a callable function.", self.name)
        if style and not isinstance(style, str):
            raise FunctionException("Fifth argument must be a string of the stylesheet.", self.name)
        
        checkbox = QCheckBox(text, self.parent.fields.get("window"))
        checkbox.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
        if style:
            checkbox.setStyleSheet(style)
        if callback:
            checkbox.stateChanged.connect(lambda state: callback.call(interpreter, [state]))
        checkbox.show()

class SetTextbox(ForgeNative):
    def __init__(self, textbox, _):
        self.name = "set"
        self.textbox = textbox
    
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], str):
            raise FunctionException("Expect type 'string'.", self.name)
        self.textbox.fields.get("textbox").setText(arguments[0])

class GetTextbox(ForgeNative):
    def __init__(self, textbox, _):
        self.name = "get"
        self.textbox = textbox
    
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return self.textbox.fields.get("textbox").text()

class Textbox(ForgeInstance):
    name = "Textbox"
    def __init__(self, textbox):
        self._class = Textbox
        self.fields = {"textbox": textbox}
        self.methods = {"set": SetTextbox, "get": GetTextbox, "setPos": SetPos, "getPos": GetPos, "setStyle": SetStyle, "getStyle": GetStyle, "setSize": SetSize, "getSize": GetSize, "remove": RemoveComponent}

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)

class AddTextbox(ForgeNative):
    def __init__(self, parent, token):
        self.name = "addTextbox"
        self.parent = parent
        self.token = token

    def arity(self):
        return 4 # label, position, size, style
    
    def variadic(self):
        return True
    
    def call(self, interpreter, arguments):
        if len(arguments) < 3 or len(arguments) > 4:
            raise FunctionException("Expect at least 3 (max 4) arguments: Text: string, Position: [x, y], Size: [width, height], (style: string !optional).")
        text = arguments[0]
        position = arguments[1]
        size = arguments[2]
        style = None
        if len(arguments) == 4:
            style = arguments[3]
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        if style and not isinstance(style, str):
            raise FunctionException("Fourth argument must be a string of the stylesheet.", self.name)
        
        textbox = QLineEdit(self.parent.fields.get("window"))
        textbox.setPlaceholderText(text)
        textbox.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
        if style:
            textbox.setStyleSheet(style)
        textbox.show()
        return Textbox(textbox)
    
class GetTextArea(ForgeNative):
    def __init__(self, textarea, _):
        self.name = "getTextArea"
        self.textarea = textarea

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return self.textarea.fields.get("textarea").toPlainText()
    
class SetTextArea(ForgeNative):
    def __init__(self, textarea, _):
        self.name = "setTextArea"
        self.textarea = textarea

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], str):
            raise FunctionException("Expect type 'string'.", self.name)
        return self.textarea.fields.get("textarea").setPlainText(arguments[0])

class TextArea(ForgeInstance):
    name = "TextArea"
    def __init__(self, textarea):
        self._class = TextArea
        self.fields = {"textarea": textarea}
        self.methods = {"get": GetTextArea, "set": SetTextArea, "setPos": SetPos, "getPos": GetPos, "setStyle": SetStyle, "getStyle": GetStyle, "setSize": SetSize, "getSize": GetSize, "remove": RemoveComponent}

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)

class AddTextArea(ForgeNative):
    def __init__(self, parent, token):
        self.name = "addTextArea"
        self.parent = parent
        self.token = token

    def arity(self):
        return 4 # label, position, size, style
    
    def variadic(self):
        return True
    
    def call(self, interpreter, arguments):
        if len(arguments) < 3 or len(arguments) > 4:
            raise FunctionException("Expect at least 3 (max 4) arguments: Text: string, Position: [x, y], Size: [width, height], (style: string !optional).")
        text = arguments[0]
        position = arguments[1]
        size = arguments[2]
        style = None
        if len(arguments) == 4:
            style = arguments[3]
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        if style and not isinstance(style, str):
            raise FunctionException("Fourth argument must be a string of the stylesheet.", self.name)
        
        textarea = QPlainTextEdit(self.parent.fields.get("window"))
        textarea.setPlaceholderText(text)
        textarea.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
        if style:
            textarea.setStyleSheet(style)
        textarea.show()
        return TextArea(textarea)

class GetDropdown(ForgeNative):
    def __init__(self, dropdown, _):
        self.name = "getDropdown"
        self.dropdown = dropdown

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        return self.dropdown.fields.get("dropdown").currentText()
    
class SetDropdown(ForgeNative):
    def __init__(self, dropdown, _):
        self.name = "setDropdown"
        self.dropdown = dropdown

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        if isinstance(arguments[0], str):
            index = self.dropdown.fields.get("dropdown").findText(arguments[0])
            if index:
                self.dropdown.fields.get("dropdown").setCurrentIndex(index)
        elif isinstance(arguments[0], float):
            index = int(arguments[0])
            self.dropdown.fields.get("dropdown").setCurrentIndex(index)
        else:
            raise FunctionException("Expect type 'string' for value, or 'int' for index.", self.name)
        
class Dropdown(ForgeInstance):
    name = "Dropdown"
    def __init__(self, dropdown):
        self._class = Dropdown
        self.fields = {"dropdown": dropdown}
        self.methods = {"get": GetDropdown, "set": SetDropdown, "setPos": SetPos, "getPos": GetPos, "setStyle": SetStyle, "getStyle": GetStyle, "setSize": SetSize, "getSize": GetSize, "remove": RemoveComponent}

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)

class AddDropdown(ForgeNative):
    def __init__(self, parent, token):
        self.name = "addDropdown"
        self.parent = parent
        self.token = token

    def arity(self):
        return 3  # Options, position, size, style
    
    def variadic(self):
        return True
    
    def call(self, interpreter, arguments):
        if len(arguments) < 3 or len(arguments) > 4:
            raise FunctionException("Expect at least 3 (max 4) arguments: Options: [items...], Position: [x, y], Size: [width, height], (style: string !optional).")
        options = arguments[0]
        position = arguments[1]
        size = arguments[2]
        style = None
        if len(arguments) == 4:
            style = arguments[3]
        if not isinstance(options, ForgeArray):
            raise FunctionException("First argument must be an array of options.", self.name)
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        if style and not isinstance(style, str):
            raise FunctionException("Fourth argument must be a string of the stylesheet.", self.name)

        dropdown = QComboBox(self.parent.fields.get("window"))
        dropdown.addItems([str(option) for option in options.elements])
        dropdown.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
        if style:
            dropdown.setStyleSheet(style)
        dropdown.show()
        return Dropdown(dropdown)

class GetListView(ForgeNative):
    def __init__(self, listview, _):
        self.name = "getListView"
        self.listview = listview

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        if self.listview.fields.get("listview").currentItem():
            return self.listview.fields.get("listview").currentItem().text()
        return ""

class SetListView(ForgeNative):
    def __init__(self, listview, _):
        self.name = "setListView"
        self.listview = listview

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        if isinstance(arguments[0], str):
            x = self.listview.fields.get("listview").findItems(arguments[0])
            if x:
                self.listview.fields.get("listview").setCurrentItem(x)
        elif isinstance(arguments[0], float):
            index = int(arguments[0])
            self.listview.fields.get("listview").setCurrentRow(index)

class ListView(ForgeInstance):
    name = "ListView"
    def __init__(self, listview):
        self._class = ListView
        self.fields = {"listview": listview}
        self.methods = {"get": GetListView, "set": SetListView, "setPos": SetPos, "getPos": GetPos, "setStyle": SetStyle, "getStyle": GetStyle, "setSize": SetSize, "getSize": GetSize, "remove": RemoveComponent}

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)

class AddListView(ForgeNative):
    def __init__(self, parent, token):
        self.name = "addListView"
        self.parent = parent
        self.token = token

    def arity(self):
        return 3  # Items, position, size, style
    
    def variadic(self):
        return True
    
    def call(self, interpreter, arguments):
        if len(arguments) < 3 or len(arguments) > 4:
            raise FunctionException("Expect at least 3 (max 4) arguments: Options: [items...], Position: [x, y], Size: [width, height], (style: string !optional).")
        items = arguments[0]
        position = arguments[1]
        size = arguments[2]
        style = None
        if len(arguments) == 4:
            style = arguments[3]
        if not isinstance(items, ForgeArray):
            raise FunctionException("First argument must be an array of items.", self.name)
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        if style and not isinstance(style, str):
            raise FunctionException("Fourth argument must be a string of the stylesheet.", self.name)

        list_view = QListWidget(self.parent.fields.get("window"))
        list_view.addItems([str(item) for item in items.elements])
        list_view.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
        if style:
            list_view.setStyleSheet(style)
        list_view.show()
        return ListView(list_view)

class ShowDialog(ForgeNative):
    def __init__(self, parent, token):
        self.name = "showDialog"
        self.parent = parent
        self.token = token

    def arity(self):
        return 3  # message, title, style
    
    def variadic(self):
        return True
    
    def call(self, interpreter, arguments):
        if len(arguments) < 2 or len(arguments) > 3:
            raise FunctionException("Expect at least 2 (max 3) arguments: Message: string, Title: string, (style: string !optional).")
        message = arguments[0]
        title = arguments[1]
        style = None
        if len(arguments) == 3:
            style = arguments[2]
        if not isinstance(message, str):
            raise FunctionException("First argument must be a string of the message.", self.name)
        if not isinstance(message, str):
            raise FunctionException("Second argument must be a string of the title.", self.name)
        if style and not isinstance(style, str):
            raise FunctionException("Third argument must be a string of the stylesheet.", self.name)
        
        dialog = QMessageBox()
        dialog.setText(message)
        dialog.setWindowTitle(title)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        if style:
            dialog.setStyleSheet(style)

        result = dialog.exec()
        return result == QMessageBox.StandardButton.Ok  # Returns true if "Ok" is clicked

class ShowWindow(ForgeNative):
    def __init__(self, parent, token):
        self.name = "show"
        self.parent = parent
        self.token = token

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        self.parent.fields.get("window").show()
        self.parent.fields.get("app").exec()

class TimerThread(QThread):
    timeout = pyqtSignal()  # Custom signal to trigger the callback

    def __init__(self, interval_ms):
        super().__init__()
        self.interval_ms = interval_ms
        self.running = False

    def run(self):
        self.running = True
        timer = QElapsedTimer()
        timer.start()

        while self.running:
            elapsed = timer.elapsed()  # Time in ms
            if elapsed >= self.interval_ms:
                self.timeout.emit()  # Trigger the callback
                timer.restart()  # Reset timer

            # Sleep briefly to reduce CPU usage
            time.sleep(0.001)

    def stop(self):
        self.running = False
        self.wait()


class StartTimer(ForgeNative):
    def __init__(self, timer, _):
        self.name = "start"
        self.timer = timer

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        self.timer.fields.get("timer").run()

class StopTimer(ForgeNative):
    def __init__(self, timer, _):
        self.name = "stop"
        self.timer = timer

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        self.timer.fields.get("timer").stop()

class Timer(ForgeInstance):
    name = "Timer"
    def __init__(self, timer):
        self._class = Timer
        self.fields = {"timer": timer}
        self.methods = {"start": StartTimer}

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)

class AddTimer(ForgeNative):
    def __init__(self, parent, token):
        self.name = "addTimer"
        self.parent = parent
        self.token = token

    def arity(self):
        return 2 # interval, callback
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], float):
            raise FunctionException("First argument must be number type (interval in msec).", self.name)
        if not isinstance(arguments[1], ForgeFunction):
            raise FunctionException("Second argument must be a callable function.", self.name)
        interval_ms = int(arguments[0])
        callback = arguments[1]
        timer = TimerThread(interval_ms)
        timer.timeout.connect(lambda: callback.call(interpreter, []))
        timer.start()
        return Timer(timer)

class SetFullscreen(ForgeNative):
    def __init__(self, parent, token):
        self.name = "setFullscreen"
        self.parent = parent
        self.token = token

    def arity(self):
        return 1 # isFullscreen
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], bool):
            raise FunctionException("First argument must be bool type.", self.name)
        if arguments[0] == True:
            self.parent.fields.get("window").showFullScreen()

class IsMousePressed(ForgeNative):
    def __init__(self, parent, token):
        self.name = "isMousePressed"
        self.parent = parent
        self.token = token

    def arity(self):
        return 1 # button
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], str):
            raise FunctionException("First argument must be type 'string'.", self.name)
        button = arguments[0]
        if not button in ["left", "right", "middle"]:
            raise FunctionException('First argument must be "left", "middle", or "right".')
        if button == "left":
            return self.parent.fields.get("app").instance().mouseButtons() == Qt.MouseButton.LeftButton
        elif button == "middle":
            return self.parent.fields.get("app").instance().mouseButtons() == Qt.MouseButton.MiddleButton
        elif button == "right":
            return self.parent.fields.get("app").instance().mouseButtons() == Qt.MouseButton.RightButton

class MousePosMiddle(ForgeNative):
    def __init__(self, parent, token):
        self.name = "mousePosMiddle"
        self.parent = parent
        self.token = token

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        window = self.parent.fields.get("window")
        cursorPos = window.mapFromGlobal(QCursor.pos())
        cursorPos = [cursorPos.x() - (window.width() / 2), cursorPos.y() - (window.height() / 2)]
        cursorPos[0] = max((window.width() / -2), min(cursorPos[0], (window.width() / 2)))
        cursorPos[1] = -1 * max((window.height() / -2), min(cursorPos[1], (window.height() / 2)))
        return ForgeArray(cursorPos)

class MousePos(ForgeNative):
    def __init__(self, parent, token):
        self.name = "mousePos"
        self.parent = parent
        self.token = token

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        window = self.parent.fields.get("window")
        cursorPos = window.mapFromGlobal(QCursor.pos())
        cursorPos = [cursorPos.x(), cursorPos.y()]
        return ForgeArray(cursorPos)

class Window(ForgeInstance):
    name = "Window"
    def __init__(self, width, height, title, logo):
        self._class = Window
        self.fields = {"app": QApplication(sys.argv), "window": QWidget()}
        self.fields.get("window").setWindowTitle(title)
        self.fields.get("window").resize(width, height)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(title)
        self.fields.get("window").setWindowIcon(QIcon(f"{HEADERS}/FL.png"))
        if logo:
            self.fields.get("window").setWindowIcon(QIcon(logo))
        self.methods = {
            "addButton": AddButton, 
            "addLabel": AddLabel, 
            "addCheckbox": AddCheckbox, 
            "addTextbox": AddTextbox,
            "addTextArea": AddTextArea,
            "addDropdown": AddDropdown,
            "addListView": AddListView,
            "showDialog": ShowDialog,
            "addTimer": AddTimer,
            "show": ShowWindow,
            "setFullscreen": SetFullscreen,
            "isMousePressed": IsMousePressed,
            "mousePosMiddle": MousePosMiddle,
            "mousePos": MousePos
            }

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)
    
#FUNCTIONS
class IsKeyPressed(ForgeNative):
    def __init__(self):
        self.name = "isKeyPressed"

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        if not isinstance(arguments[0], str):
            raise FunctionException("First argument must be type 'string'.", self.name)
        key = arguments[0]
        return keyboard.is_pressed(key)

class SpawnRandom(ForgeNative):
    def __init__(self):
        self.name = "random"

    def arity(self):
        return 0

    def call(self, interpreter, _):
        return Random()

class SpawnWindow(ForgeNative):
    def __init__(self):
        self.name = "window"

    def arity(self):
        return 0
    
    def variadic(self):
        return True
    
    def call(self, interpreter, arguments):
        width = 500
        height = 500
        title = "Forge App"
        logo = None
        if len(arguments) > 3:
            raise FunctionException("Expect at least 0 (max 3) arguments: [width, height]: array, Title: string, logoURL: string")
        if len(arguments) > 0:
            if not isinstance(arguments[0], ForgeArray) or arguments[0].length() != 2:
                raise FunctionException("First argument must be an array of [width, height].", self.name)
            dims = arguments[0]
            try:
                width = int(dims.elements[0])
                height = int(dims.elements[1])
            except Exception:
                raise FunctionException("Elements of array must be numbers.", self.name)
        if len(arguments) > 1:
            if not isinstance(arguments[1], str):
                raise FunctionException("Second argument must be a string.", self.name)
            title = arguments[1]
        if len(arguments) > 2:
            if not isinstance(arguments[2], str):
                raise FunctionException("Third argument must be a string.", self.name)
            logo = arguments[2]
        return Window(width, height, title, logo)

class Hash(ForgeNative):
    def __init__(self):
        self.name = "hashMap"

    def arity(self):
        return 0

    def call(self, interpreter, _):
        return HashMap()
    
class Clock(ForgeNative):
    def __init__(self):
        self.name = "clock"

    def arity(self):
        return 0

    def call(self, interpreter, _):
        return time.time()
        
class GetLine(ForgeNative):
    def __init__(self):
        self.name = "getline"

    def arity(self):
        return 0

    def call(self, interpreter, _):
        return input()
    
class Type(ForgeNative):
    def __init__(self):
        self.name = "type"

    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        obj = arguments[0]

        if isinstance(obj, bool):
            return "boolean"
        elif isinstance(obj, float) or isinstance(obj, int):
            return "number"
        elif isinstance(obj, str):
            return "string"
        elif isinstance(obj, (ForgeFunction, ForgeNative)):
            return "function"
        elif isinstance(obj, ForgeClass):
            return "class"
        elif isinstance(obj, ForgeArray):
            return "array"
        elif isinstance(obj, ForgeInstance):
            return obj._class.name
        elif obj is None:
            return "null"

        return str(obj)
    
class Now(ForgeNative):
    def __init__(self):
        self.name = "now"

    def arity(self):
        return 0
    
    def call(self, interpreter, arguments):
        temp = datetime.datetime.now()
        return ForgeArray([float(temp.year), float(temp.month), float(temp.day)])
    
class ToString(ForgeNative):
    def __init__(self):
        self.name = "toString"

    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        obj = arguments[0]

        if isinstance(obj, ForgeNative):
            return f"fn <{obj.name}>"

        if isinstance(obj, ForgeArray):
            return "".join(map(str, obj.elements))
        return str(obj)
    
class ToUpper(ForgeNative):
    def __init__(self):
        self.name = "toUpper"

    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        obj = arguments[0]

        if not isinstance(obj, str):
            raise FunctionException("Expect type 'string'.", self.name)
        return obj.upper()
    
class ToLower(ForgeNative):
    def __init__(self):
        self.name = "toLower"

    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        obj = arguments[0]

        if not isinstance(obj, str):
            raise FunctionException("Expect type 'string'.", self.name)
        return obj.lower()

class ToNumber(ForgeNative):
    def __init__(self):
        self.name = "toNum"

    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        obj = arguments[0]

        try:
            return float(obj)
        except ValueError:
            raise FunctionException("The string doesn't represent a valid number.", self.name)
        
class ToArray(ForgeNative):
    def __init__(self):
        self.name = "toArray"

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        obj = arguments[0]
        if not isinstance(obj, str):
            raise FunctionException("Expect type 'string'.", self.name)
        
        try:
            return ForgeArray(list(obj))
        except Exception:
            raise FunctionException("Error during forming array.", self.name)
        
class WriteToFile(ForgeNative):
    def __init__(self):
        self.name = "write"
    
    def arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        lib = arguments[0]
        lib_path = Path(str(lib))

        if lib_path.is_file():
            try:
                with open(lib_path, "a") as f:
                    f.write(arguments[1])
            except Exception as e:
                raise FunctionException(e, self.name)
        else:
            raise FunctionException("The specified file cannot be found.", self.name)
        
class ClearFile(ForgeNative):
    def __init__(self):
        self.name = "clear"

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        lib = arguments[0]
        lib_path = Path(str(lib))

        try:
            open(lib_path, "w").close()
        except Exception as e:
            raise FunctionException(e, self.name)
        
class ReadFile(ForgeNative):
    def __init__(self):
        self.name = "read"

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        lib = arguments[0]
        lib_path = Path(str(lib))

        if lib_path.is_file():
            try:
                with open(lib_path, "r") as f:
                    return f.read()
            except Exception as e:
                raise FunctionException(e, self.name)
        else:
            raise FunctionException("The specified file cannot be found.", self.name)
        
class CreateFile(ForgeNative):
    def __init__(self):
        self.name = "create"

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        lib = arguments[0]
        lib_path = Path(str(lib))

        if not lib_path.is_file():
            try:
                open(lib_path, "w").close()
            except Exception as e:
                raise FunctionException(e, self.name)

class Exit(ForgeNative):
    def __init__(self):
        self.name = "exit"

    def arity(self):
        return 1
    
    def variadic(self):
        return True
    
    def call(self, interpreter, arguments):
        if len(arguments) > 1:
            raise FunctionException("Expect max 1 arguments: (exit code: num !optional)")
        if len(arguments) == 1:
            code = arguments[0]
            if not isinstance(code, float) or not isinstance(code, int):
                raise FunctionException("First argumets must be type 'num'.")
            exit(math.floor(code))
        exit(0)


class MathFunction(ForgeNative):
    def __init__(self):
        self.name = None

    def arity(self) -> int:
        return 1

    def check_number(self, argument):
        if not isinstance(argument, float):
            raise FunctionException("Expect type 'number'.", self.name)

        return argument

    def call(self, interpreter, arguments):
        pass

class Exponent(MathFunction):
    def __init__(self):
        self.name = "exp"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.exp(obj)
    
class Power(MathFunction):
    def __init__(self):
        self.name = "pow"

    def arity(self):
        return 2

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        obj2 = self.check_number(arguments[1])
        return math.pow(obj, obj2)

class Sqrt(MathFunction):
    def __init__(self):
        self.name = "sqrt"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.sqrt(obj)

class Log(MathFunction):
    def __init__(self):
        self.name = "log"
    
    def arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        obj2 = self.check_number(arguments[1])
        return math.log(obj2, obj)

class ToRadian(MathFunction):
    def __init__(self):
        self.name = "rad"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.radians(obj)
    
class Sin(MathFunction):
    def __init__(self):
        self.name = "sin"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.sin(obj)
    
class ArcSin(MathFunction):
    def __init__(self):
        self.name = "arcsin"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.asin(obj)
    
class Cos(MathFunction):
    def __init__(self):
        self.name = "cos"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.cos(obj)
    
class ArcCos(MathFunction):
    def __init__(self):
        self.name = "arccos"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.acos(obj)
    
class Tan(MathFunction):
    def __init__(self):
        self.name = "tan"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.tan(obj)
    
class ArcTan(MathFunction):
    def __init__(self):
        self.name = "arctan"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.atan(obj)
    
class Floor(MathFunction):
    def __init__(self):
        self.name = "floor"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.floor(obj)
    
class Ceiling(MathFunction):
    def __init__(self):
        self.name = "ceiling"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return math.ceil(obj)
    
class Round(MathFunction):
    def __init__(self):
        self.name = "round"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return round(obj)
    
class Absolute(MathFunction):
    def __init__(self):
        self.name = "abs"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        return abs(obj)
    
class Sign(MathFunction):
    def __init__(self):
        self.name = "sign"

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        if obj > 0:
            return 1
        elif obj < 0:
            return -1
        return 0
    
class Min(MathFunction):
    def __init__(self):
        self.name = "min"

    def arity(self):
        return 2

    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        obj2 = self.check_number(arguments[1])
        return min(obj, obj2)
    
class Max(MathFunction):
    def __init__(self):
        self.name = "max"

    def arity(self):
        return 2
    
    def call(self, interpreter, arguments):
        obj = self.check_number(arguments[0])
        obj2 = self.check_number(arguments[1])
        return max(obj, obj2)

nativeFunctions = [IsKeyPressed, SpawnRandom, SpawnWindow, Hash, Clock, GetLine, Type, Now, ToString, ToUpper, ToLower, ToNumber, ToArray, Exponent, Power, Sqrt, Log, ToRadian, Sin, ArcSin, Cos, ArcCos, Tan, ArcTan, Floor, Ceiling, Round, Absolute, Sign, Min, Max, WriteToFile, ReadFile, ClearFile, CreateFile, Exit]
nativeGlobals = {"PI": math.pi, "E": math.e}