import random
import time
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import scrolledtext, ttk, messagebox
from typing import Any, Dict, List, Optional, Tuple, Type, Union, cast


Parent = Union["Component", tk.Tk, ttk.Frame]


class Checkbutton(ttk.Checkbutton):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.variable = tk.IntVar()
        self.configure(variable=self.variable)

    def isSelected(self) -> bool:
        return self.variable.get() == 1


@dataclass
class GridArgs:
    column: int
    row: int
    columnspan: int = 1
    rowspan: int = 1
    padx: Union[Tuple[int, int], int] = 0
    pady: Union[Tuple[int, int], int] = 0
    sticky: str = ""

    def next_row(self) -> int:
        self.row += 1
        return self.row

    def next_column(self) -> int:
        self.column += 1
        return self.column

    def reset_column(self):
        self.column = 0

    def wrap(self):
        self.next_row()
        self.reset_column()

    def reset_span(self):
        self.columnspan = 1
        self.rowspan = 1

    def reset_sticky(self):
        self.sticky = ""

    def reset_padx(self):
        self.padx = 0

    def reset_pady(self):
        self.pady = 0


class Component:
    def __init__(self, parent: Parent, label_frame=False, **kwargs):
        self.parent = parent
        self.frame = self._create_frame(parent, label_frame, **kwargs)
        self.children_widgets: Dict[str, ttk.Widget] = {}
        self.children_components: Dict[str, Component] = {}
        self.grid_args = GridArgs(0, 0)
        self.setup()
        self.initialize()

    def _create_frame(self, parent: Parent, label_frame, **kwargs) -> ttk.Frame:
        frame_class = ttk.Frame
        if label_frame:
            frame_class = ttk.LabelFrame
        if parent is None:
            frame = frame_class(None, **kwargs)
        elif isinstance(parent, tk.Tk):
            frame = frame_class(parent, **kwargs)
            frame.grid(sticky="NSWE")
        elif isinstance(parent, ttk.Frame):
            frame = frame_class(parent, **kwargs)
            frame.grid(sticky="NSWE")
        else:
            frame = frame_class(parent.frame, **kwargs)
        return frame

    def __getitem__(self, key: str):
        if not isinstance(key, str):
            raise TypeError(f"Wrong key type, must be str, was: {type(key)}")
        if key in self.children_components:
            return self.children_components[key]
        if key in self.children_widgets:
            return self.children_widgets[key]
        raise KeyError(f"{key}")

    def place_widget(self, widget: ttk.Widget):
        widget.grid(
            column=self.grid_args.column,
            row=self.grid_args.row,
            columnspan=self.grid_args.columnspan,
            rowspan=self.grid_args.rowspan,
            padx=self.grid_args.padx,
            pady=self.grid_args.pady,
            sticky=self.grid_args.sticky,
        )

    def create_widget(
        self, widget_id: str, widget_class: Type[ttk.Widget], **widget_args
    ) -> ttk.Widget:
        widget = widget_class(self.frame, **widget_args)
        self.place_widget(widget)
        self.children_widgets[widget_id] = widget
        return widget

    def create_component(
        self, component_id: str, component_class: Type["Component"], **component_args
    ):
        component = component_class(self, **component_args)
        self.place_widget(component.frame)
        self.children_components[component_id] = component
        return component

    def setup(self):
        pass

    def initialize(self):
        pass


class TabbedComponent(Component):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.notebook = ttk.Notebook(self.frame, **kwargs)
        self.notebook.grid(sticky="NSWE")
        self.tabs: Dict[str, ttk.Frame] = {}

    def create_component_tab(
        self,
        tab_id: str,
        component_id: str,
        component_class: Type["Component"],
        **component_args,
    ):
        component = component_class(self.tabs[tab_id], **component_args)
        self.place_widget(component.frame)
        self.children_components[component_id] = component
        return component

    def create_tab(self, tab_id: str, tab_text: str, **kwargs):
        tab = ttk.Frame(self.notebook, **kwargs)
        tab.columnconfigure(0, weight=1)
        self.notebook.add(tab, text=tab_text)
        self.tabs[tab_id] = tab


class Menu:
    def __init__(self, component: Component):
        self.parent = component
        self.window = cast(tk.Tk, component.parent)
        self.menu = tk.Menu(self.window)
        self.window.configure(menu=self.menu)
        self.submenus: Dict[str, tk.Menu] = {}

    def create_item(self, item_id: str, item_name: str, **kwargs):
        submenu = tk.Menu(self.menu, **kwargs)
        self.menu.add_cascade(label=item_name, menu=submenu)
        self.submenus[item_id] = submenu

    def create_submenu_item(self, submenu_id: str, item_name: str, **kwargs):
        self.submenus[submenu_id].add_command(label=item_name, **kwargs)
        self.menu.update()

    def create_submenu_separator(self, submenu_id: str):
        self.submenus[submenu_id].add_separator()


class ProgramMenu(Menu):
    def __init__(self, window):
        super().__init__(window)
        self.initialize()

    def initialize(self):
        self.create_item("sistema", "Sistema", tearoff=0)
        self.create_submenu_item("sistema", "Imprimir", command=self.imprimir)
        self.create_submenu_item("sistema", "Salir", command=self.exit_program)
        self.create_item("help", "Ayuda", tearoff=0)
        self.create_submenu_item("help", "Acerca de", command=self.help_message)

    def help_message(self):
        message = "Joel Gomez Sanchez\n" "Copyright 2020\n" "JGS Inc\n"
        messagebox.showinfo(title="Acerca de", message=message)

    def imprimir(self):
        data = self.parent["tabbed"]["datos"].get_data()
        pasatiempos = self.parent["tabbed"]["extras"].get_pasatiempos()
        estado = self.parent["tabbed"]["extras"].get_estado()
        objetivo = self.parent["tabbed"]["extras"].get_objetivo()
        fields = [
            "Nombre",
            "Apellido Paterno",
            "Apellido Materno",
            "Direccion",
            "Colonia",
            "Ciudad",
            "Municipio",
        ]
        message = ""
        for k, v in data.items():
            if not v:
                messagebox.showinfo(
                    title="Datos", message="Los campos estan incompletos"
                )
                return
        else:
            for i in zip(fields, data.values()):
                message += f"{i[0]}: {i[1]}\n"
        if not pasatiempos or not objetivo:
            messagebox.showinfo(title="Datos", message="Los campos estan incompletos")
            return
        message += "Pasatiempos:\n"
        for i in pasatiempos:
            message += f"  * {i}\n"
        message += f"Estado:\n  * {estado}\n"
        message += f"Objetivo en la vida:\n  {objetivo}"
        messagebox.showinfo(title="Datos extras", message=message)

    def exit_program(self):
        self.window.quit()
        self.window.destroy()
        exit()


class Datos(Component):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

    def get_data(self) -> Dict[str, str]:
        return {
            k: v.get()
            for k, v in self.children_widgets.items()
            if isinstance(v, ttk.Entry)
        }

    def setup(self):
        self.grid_args.pady = (0, 5)
        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)
        self.grid_args.sticky = "WE"

    def initialize(self):
        self.initialize_entries()
        self.initialize_comboboxes()
        self.initialize_button()

    def initialize_entries(self):
        self.create_label("label_nombre", text="Nombre")
        self.create_entry("entry_nombre")
        self.create_label("label_apellido_paterno", text="Apellido Paterno")
        self.create_entry("entry_apellido_paterno")
        self.create_label("label_apellido_materno", text="Apellido Materno")
        self.create_entry("entry_apellido_materno")
        self.create_label("label_direccion", text="Direccion")
        self.create_entry("entry_direccion")

    def create_label(self, label_id: str, **kwargs):
        self.grid_args.padx = (0, 20)
        self.create_widget(label_id, ttk.Label, **kwargs)
        self.grid_args.reset_padx()
        self.grid_args.next_column()

    def create_entry(self, entry_id: str, **kwargs):
        self.create_widget(entry_id, ttk.Entry, **kwargs)
        self.grid_args.wrap()

    def initialize_comboboxes(self):
        values_colonia = ("Tepeyac", "Morelos", "Lazaro Cardenas")
        self.create_label("label_colonia", text="Colonia")
        self.create_combobox("combobox_colonia", values=values_colonia)
        values_ciudad = ("Morelia", "Zinapecuaro", "Lazaro Cardenas")
        self.create_label("label_ciudad", text="Ciudad")
        self.create_combobox("combobox_ciudad", values=values_ciudad)
        values_municipio = ("Zinapecuaro", "Tangamandapio", "Zitacuaro")
        self.create_label("label_municipio", text="Municipio")
        self.create_combobox("combobox_municipio", values=values_municipio)

    def create_combobox(self, combobox_id: str, **kwargs):
        widget = self.create_widget(combobox_id, ttk.Combobox, **kwargs)
        combobox = cast(ttk.Combobox, widget)
        combobox["state"] = "readonly"
        combobox.current(0)
        self.grid_args.wrap()

    def initialize_button(self):
        self.grid_args.sticky = "E"
        self.grid_args.padx = (10, 0)
        self.grid_args.row -= 1
        self.grid_args.column = 2
        self.create_widget(
            "button_imprimir",
            ttk.Button,
            text="Imprimir Datos Personales",
            command=self.button_imprimir_callback,
        )

    def button_imprimir_callback(self):
        data = self.get_data()
        fields = [
            "Nombre",
            "Apellido Paterno",
            "Apellido Materno",
            "Direccion",
            "Colonia",
            "Ciudad",
            "Municipio",
        ]
        for k, v in data.items():
            if not v:
                messagebox.showinfo(title="Datos", message="Registro Incompleto")
                break
        else:
            message = ""
            for i in zip(fields, data.values()):
                message += f"{i[0]}: {i[1]}\n"
            messagebox.showinfo(title="Datos", message=message)


class Pasatiempos(Component):
    def __init__(self, parent, **kwargs):
        self.radiobutton_value = tk.IntVar(value=0)
        super().__init__(parent, **kwargs)

    def get_pasatiempos(self) -> List[str]:
        return [
            v.cget("text")
            for k, v in self.children_widgets.items()
            if isinstance(v, Checkbutton) and v.isSelected()
        ]

    def get_estado(self) -> str:
        for k, v in self.children_widgets.items():
            if (
                isinstance(v, ttk.Radiobutton)
                and v.cget("value") == self.radiobutton_value.get()
            ):
                return v.cget("text")
        return ""

    def get_objetivo(self) -> str:
        entry: ttk.Entry = self["entry_objetivo"]
        return entry.get()

    def setup(self):
        self.grid_args.pady = (0, 5)
        self.grid_args.sticky = "NSWE"
        for i in range(3):
            self.frame.columnconfigure(i, weight=1)

    def initialize(self):
        self.initialize_checkbuttons()
        self.initialize_radiobuttons()
        self.intialize_entry()
        self.initialize_button()

    def initialize_checkbuttons(self):
        self.grid_args.columnspan = 99
        self.create_label("label_pasatiempos", text="Pasatiempos")
        self.grid_args.reset_span()
        self.grid_args.wrap()
        self.create_checkbutton("checkbutton_leer", text="Leer")
        self.create_checkbutton("checkbutton_peliculas", text="Peliculas")
        self.create_checkbutton("checkbutton_redes", text="Redes Sociales")
        self.grid_args.wrap()

    def create_label(self, label_id: str, **kwargs):
        self.create_widget(label_id, ttk.Label, **kwargs)

    def create_checkbutton(self, checkbutton_id, **kwargs):
        self.create_widget(checkbutton_id, Checkbutton, **kwargs)
        self.grid_args.next_column()

    def initialize_radiobuttons(self):
        self.grid_args.columnspan = 99
        self.create_label("label_estado", text="Estado Civil")
        self.grid_args.reset_span()
        self.grid_args.wrap()
        self.create_radiobutton("radiobutton_soltero", text="Soltero", value=0)
        self.create_radiobutton("radiobutton_casado", text="Casado", value=1)
        self.create_radiobutton("radiobutton_viduo", text="Viudo", value=2)
        self.grid_args.wrap()

    def create_radiobutton(self, radiobutton_id, **kwargs):
        var = self.radiobutton_value
        self.create_widget(radiobutton_id, ttk.Radiobutton, variable=var, **kwargs)
        self.grid_args.next_column()

    def intialize_entry(self):
        self.grid_args.columnspan = 2
        self.create_widget("label_objetivo", ttk.Label, text="Objetivo en la vida")
        self.grid_args.next_row()
        self.grid_args.padx = (0, 10)
        self.create_widget("entry_objetivo", ttk.Entry)
        self.grid_args.reset_padx()

    def initialize_button(self):
        self.grid_args.reset_span()
        self.grid_args.row -= 1
        self.grid_args.column = 2
        self.grid_args.rowspan = 2
        self.grid_args.sticky = "NSWE"
        self.create_widget(
            "button_imprimir",
            ttk.Button,
            text="Imprimir Datos",
            command=self.button_callback,
        )
        self.grid_args.reset_span()
        self.grid_args.wrap()

    def button_callback(self):
        pasatiempos = self.get_pasatiempos()
        estado = self.get_estado()
        objetivo = self.get_objetivo()
        if not pasatiempos or not objetivo:
            messagebox.showinfo(
                title="Datos extras", message="Debe llenar todos los campos"
            )
            return
        text = "Pasatiempo:\n"
        for i in pasatiempos:
            text += f"  * {i}\n"
        text += f"Estado:\n  * {estado}\n"
        text += f"Objetivo en la vida:\n  {objetivo}"
        messagebox.showinfo(title="Datos extras", message=text)


class ProgramTabs(TabbedComponent):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_args.sticky = "NSWE"
        self.frame.columnconfigure(0, weight=1)
        self.create_tab("1", "Datos Personales")
        self.create_tab("2", "Datos Extras")
        self.tabs["1"].configure(padding=10)
        self.tabs["2"].configure(padding=10)
        self.create_component_tab("1", "datos", Datos)
        self.create_component_tab("2", "extras", Pasatiempos)


class MainWindow(Component):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        self.frame.configure(padding=20)
        self.grid_args.sticky = "NSWE"
        self.frame.columnconfigure(0, weight=1)

    def initialize(self):
        self.create_menu(ProgramMenu)
        self.create_component("tabbed", ProgramTabs)

    def create_menu(self, menu_type: Type[Menu]):
        return menu_type(self)


def main():
    window = tk.Tk()
    window.minsize(640, 480)
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)
    window.title("My Program")
    main_window = MainWindow(window)
    window.mainloop()


main()
