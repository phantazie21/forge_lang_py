from forge_callable import ForgeCallable
from forge_function import ForgeFunction
from forge_class import ForgeClass
from forge_instance import ForgeInstance
from error import FunctionException
from forge_array import ForgeArray
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QCheckBox, QLineEdit, QMessageBox, QComboBox, QListWidget, QPlainTextEdit
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
                raise FunctionException(f"Undefined property '{arguments[0]}'.", "set")
            
class GetHashMap(ForgeNative):
    def __init__(self, parent, token):
        self.name = "get"
        self.parent = parent
        self.token = token

    def arity(self):
        return 1
    
    def call(self, interpreter, arguments):
        return self.parent.fields.get(arguments[0]) or self.parent.fields.get(str(arguments[0]))

class HashMap(ForgeInstance):
    name = "HashMap"
    def __init__(self):
        self._class = HashMap
        self.fields = {}
        self.methods = {"set": SetHashMap, "get": GetHashMap}

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)
        
    def __str__(self):
        return str(self.fields)
    
class AddButton(ForgeNative):
    def __init__(self, parent, token):
        self.name = "addButton"
        self.parent = parent
        self.token = token

    def arity(self):
        return 4 # text, position, size, callback
    
    def call(self, interpreter, arguments):
        text = arguments[0]
        position = arguments[1]
        size = arguments[2]
        callback = arguments[3]
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        if not isinstance(callback, ForgeFunction):
            raise FunctionException("Fourth argument must be a callable function.", self.name)
        
        button = QPushButton(text, self.parent.fields.get("window"))
        button.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
        button.clicked.connect(lambda: callback.call(interpreter, []))
        button.show()

class AddLabel(ForgeNative):
    def __init__(self, parent, token):
        self.name = "addLabel"
        self.parent = parent
        self.token = token

    def arity(self):
        return 3 # text, position, size
    
    def call(self, interpreter, arguments):
        text = arguments[0]
        position = arguments[1]
        size = arguments[2]
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        
        label = QLabel(text, self.parent.fields.get("window"))
        label.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
        label.show()
    
class AddCheckbox(ForgeNative):
    def __init__(self, parent, token):
        self.name = "addCheckbox"
        self.parent = parent
        self.token = token

    def arity(self):
        return 4 # label, position, size, callback
    
    def variadic(self):
        return True

    def call(self, interpreter, arguments):
        if len(arguments) < 3:
            raise FunctionException('Give at least 3 arguments: Text: str, Position: [x, y], Size: [width, height], (onChange: function !optional).', self.name)
        text = arguments[0]
        position = arguments[1]
        size = arguments[2]
        callback = None
        if len(arguments) == 4:
            callback = arguments[3]
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        if callback and not isinstance(callback, ForgeFunction):
            raise FunctionException("Fourth argument must be a callable function.", self.name)
        
        checkbox = QCheckBox(text, self.parent.fields.get("window"))
        checkbox.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
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
        self.methods = {"set": SetTextbox, "get": GetTextbox}

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
        return 3 # label, position, size
    
    def call(self, interpreter, arguments):
        text = arguments[0]
        position = arguments[1]
        size = arguments[2]
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        
        textbox = QLineEdit(self.parent.fields.get("window"))
        textbox.setPlaceholderText(text)
        textbox.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
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
        self.methods = {"get": GetTextArea, "set": SetTextArea}

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
        return 3 # label, position, size
    
    def call(self, interpreter, arguments):
        text = arguments[0]
        position = arguments[1]
        size = arguments[2]
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)
        
        textarea = QPlainTextEdit(self.parent.fields.get("window"))
        textarea.setPlaceholderText(text)
        textarea.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
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
        self.methods = {"get": GetDropdown, "set": SetDropdown}

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
        return 3  # Options, position, size
    
    def call(self, interpreter, arguments):
        options = arguments[0]
        position = arguments[1]
        size = arguments[2]
        if not isinstance(options, ForgeArray):
            raise FunctionException("First argument must be an array of options.", self.name)
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)

        dropdown = QComboBox(self.parent.fields.get("window"))
        dropdown.addItems([str(option) for option in options.elements])
        dropdown.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )
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
        self.methods = {"get": GetListView, "set": SetListView}

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
        return 3  # Items, position, size
    
    def call(self, interpreter, arguments):
        items = arguments[0]
        position = arguments[1]
        size = arguments[2]
        if not isinstance(items, ForgeArray):
            raise FunctionException("First argument must be an array of items.", self.name)
        if not isinstance(position, ForgeArray) or position.length() != 2:
            raise FunctionException("Second argument must be an array of [x, y].", self.name)
        if not isinstance(size, ForgeArray) or size.length() != 2:
            raise FunctionException("Third argument must be an array of [width, height].", self.name)

        list_view = QListWidget(self.parent.fields.get("window"))
        list_view.addItems([str(item) for item in items.elements])
        list_view.setGeometry(
            int(position.elements[0]), int(position.elements[1]),
            int(size.elements[0]), int(size.elements[1])
        )

        list_view.show()
        return ListView(list_view)

class ShowDialog(ForgeNative):
    def __init__(self, parent, token):
        self.name = "showDialog"
        self.parent = parent
        self.token = token

    def arity(self):
        return 2  # Message and Title
    
    def call(self, interpreter, arguments):
        message = arguments[0]
        title = arguments[1]

        dialog = QMessageBox()
        dialog.setText(message)
        dialog.setWindowTitle(title)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

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

class Window(ForgeInstance):
    name = "Window"
    def __init__(self, width, height, title):
        self._class = Window
        self.fields = {"app": QApplication(sys.argv), "window": QWidget()}
        self.fields.get("window").setWindowTitle(title)
        self.fields.get("window").resize(width, height)
        self.methods = {
            "addButton": AddButton, 
            "addLabel": AddLabel, 
            "addCheckbox": AddCheckbox, 
            "addTextbox": AddTextbox,
            "addTextArea": AddTextArea,
            "addDropdown": AddDropdown,
            "addListView": AddListView,
            "showDialog": ShowDialog,
            "show": ShowWindow
            }

    def get(self, name):
        try:
            return self.methods[name.lexeme](self, name)  # type: ignore
        except KeyError:
            raise FunctionException(f"Undefined method.", name.lexeme)
    
#FUNCTIONS
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
        if len(arguments) > 0:
            if not isinstance(arguments[0], ForgeArray) or arguments[0].length() != 2:
                raise FunctionException("First argument must be an array of [width, height].", self.name)
            dims = arguments[0]
            width = int(dims.elements[0])
            height = int(dims.elements[1])
        if len(arguments) > 1:
            if not isinstance(arguments[1], str):
                raise FunctionException("Second argument must be a string.", self.name)
            title = arguments[1]
        return Window(width, height, title)

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
        elif isinstance(obj, float):
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

nativeFunctions = [SpawnWindow, Hash, Clock, GetLine, Type, Now, ToString, ToUpper, ToLower, ToNumber, ToArray, Exponent, Power, Sqrt, Log, ToRadian, Sin, ArcSin, Cos, ArcCos, Tan, ArcTan, Floor, Ceiling, Round, Absolute, Sign, WriteToFile, ReadFile, ClearFile, CreateFile]
nativeGlobals = {"PI": math.pi, "E": math.e}