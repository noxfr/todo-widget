#!/usr/bin/env python3
import os
import re
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk

PATH = os.path.expanduser("~/todo.md")
LINE = re.compile(r"^- \[( |x)\] (.*)$")

CSS = b"""
.task-row { padding: 10px 14px; }
.task-row check { min-width: 20px; min-height: 20px; }
.task-row.done .task-text { text-decoration: line-through; opacity: 0.5; }
.add-bar { padding: 12px; }
.badge { border-radius: 999px; padding: 2px 10px; min-height: 0; font-size: 0.8em; font-weight: bold; margin-right: 10px; }
.badge.urgent { background: #e01b24; color: white; }
.badge.not-urgent { background: alpha(currentColor, 0.1); opacity: 0.6; }
.delete { margin-right: 8px; opacity: 0.5; }
.delete:hover { opacity: 1; color: #e01b24; }
"""
URGENT = " #urgent"


def read_lines():
    try:
        with open(PATH, encoding="utf-8") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []


def write_lines(lines):
    with open(PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))


class TodoWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, default_width=420, default_height=560)
        self.set_icon_name("local.TodoWidget")

        self.title = Adw.WindowTitle(title="Todo", subtitle="")
        header = Adw.HeaderBar(title_widget=self.title)

        self.listbox = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE, margin_start=12, margin_end=12, margin_top=12)
        self.listbox.add_css_class("boxed-list")
        list_scroll = Gtk.ScrolledWindow(vexpand=True, hscrollbar_policy=Gtk.PolicyType.NEVER)
        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.START)
        list_box.append(self.listbox)
        list_scroll.set_child(list_box)

        empty = Adw.StatusPage(icon_name="emblem-ok-symbolic", title="Rien à faire", description="Ajoute une tâche ci-dessous")
        self.stack = Gtk.Stack()
        self.stack.add_named(list_scroll, "list")
        self.stack.add_named(empty, "empty")

        self.entry = Gtk.Entry(placeholder_text="Nouvelle tâche…", hexpand=True)
        self.entry.connect("activate", self.on_add)
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.add_css_class("suggested-action")
        add_btn.connect("clicked", lambda *_: self.on_add(self.entry))
        bar = Gtk.Box(spacing=8)
        bar.add_css_class("add-bar")
        bar.append(self.entry)
        bar.append(add_btn)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        body.append(self.stack)
        body.append(bar)
        view = Adw.ToolbarView(content=body)
        view.add_top_bar(header)
        self.set_content(view)

        self.monitor = Gio.File.new_for_path(PATH).monitor_file(Gio.FileMonitorFlags.NONE, None)
        self.monitor.connect("changed", lambda *_: GLib.idle_add(self.refresh))
        self.refresh()

    def refresh(self):
        while (row := self.listbox.get_first_child()) is not None:
            self.listbox.remove(row)
        pending = 0
        tasks = [(i, m) for i, line in enumerate(read_lines()) if (m := LINE.match(line))]
        tasks.sort(key=lambda t: not t[1].group(2).endswith(URGENT))
        for i, m in tasks:
            done = m.group(1) == "x"
            pending += not done
            text = m.group(2)
            urgent = text.endswith(URGENT)
            if urgent:
                text = text[: -len(URGENT)]
            check = Gtk.CheckButton(active=done, valign=Gtk.Align.CENTER)
            check.connect("toggled", self.on_toggle, i)
            label = Gtk.Label(label=text, wrap=True, xalign=0, hexpand=True)
            label.add_css_class("task-text")
            entry = Gtk.Entry(text=text, hexpand=True, valign=Gtk.Align.CENTER)
            edit = Gtk.Stack(hexpand=True)
            edit.add_child(label)
            edit.add_child(entry)
            click = Gtk.GestureClick()
            click.connect("released", self.on_start_edit, edit, entry)
            label.add_controller(click)
            entry.connect("activate", self.on_edit, edit, i)
            focus = Gtk.EventControllerFocus()
            focus.connect("leave", lambda _c, e=entry, s=edit, idx=i: self.on_edit(e, s, idx))
            entry.add_controller(focus)
            badge = Gtk.Button(label="Urgent" if urgent else "Pas urgent", valign=Gtk.Align.CENTER)
            badge.add_css_class("badge")
            badge.add_css_class("urgent" if urgent else "not-urgent")
            badge.connect("clicked", self.on_urgent, i)
            delete = Gtk.Button(icon_name="window-close-symbolic", valign=Gtk.Align.CENTER, tooltip_text="Supprimer")
            delete.add_css_class("flat")
            delete.add_css_class("circular")
            delete.add_css_class("delete")
            delete.connect("clicked", self.on_delete, i)
            row = Gtk.Box(spacing=12)
            row.add_css_class("task-row")
            if done:
                row.add_css_class("done")
            row.append(check)
            row.append(edit)
            row.append(badge)
            row.append(delete)
            self.listbox.append(row)
        total = sum(1 for l in read_lines() if LINE.match(l))
        self.stack.set_visible_child_name("list" if total else "empty")
        self.title.set_subtitle(f"{pending} à faire" if pending else "Tout est fait")
        return False

    def on_toggle(self, check, index):
        lines = read_lines()
        if index >= len(lines):
            return
        m = LINE.match(lines[index])
        if m:
            lines[index] = f"- [{'x' if check.get_active() else ' '}] {m.group(2)}"
            write_lines(lines)

    def on_urgent(self, _button, index):
        lines = read_lines()
        if index >= len(lines) or not LINE.match(lines[index]):
            return
        line = lines[index]
        lines[index] = line[: -len(URGENT)] if line.endswith(URGENT) else line + URGENT
        write_lines(lines)

    def on_start_edit(self, _gesture, _n, _x, _y, edit, entry):
        edit.set_visible_child(entry)
        entry.grab_focus()

    def on_edit(self, entry, edit, index):
        if edit.get_visible_child() is not entry:
            return
        edit.set_visible_child(edit.get_first_child())
        text = entry.get_text().strip()
        lines = read_lines()
        if not text or index >= len(lines) or not (m := LINE.match(lines[index])):
            return
        suffix = URGENT if m.group(2).endswith(URGENT) else ""
        new = f"- [{m.group(1)}] {text}{suffix}"
        if new != lines[index]:
            lines[index] = new
            write_lines(lines)

    def on_delete(self, _button, index):
        lines = read_lines()
        if index >= len(lines) or not LINE.match(lines[index]):
            return
        del lines[index]
        write_lines(lines)

    def on_add(self, entry):
        text = entry.get_text().strip()
        if not text:
            return
        lines = read_lines()
        lines.append(f"- [ ] {text}")
        write_lines(lines)
        entry.set_text("")


class TodoApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="local.TodoWidget")

    def do_startup(self):
        Adw.Application.do_startup(self)
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def do_activate(self):
        win = self.props.active_window or TodoWindow(self)
        win.present()


if __name__ == "__main__":
    sys.exit(TodoApp().run(sys.argv))
