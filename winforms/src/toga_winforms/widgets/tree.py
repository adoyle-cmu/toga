import System.Windows.Forms as WinForms

from toga.handlers import WeakrefCallable

from .base import Widget


class Tree(Widget):
    def create(self):
        self.native = WinForms.TreeView()
        self.native.AfterSelect += WeakrefCallable(self.winforms_after_select)
        self.native.NodeMouseDoubleClick += WeakrefCallable(
            self.winforms_node_mouse_double_click
        )
        self.native.ImageList = WinForms.ImageList()

    def change_source(self, source):
        self.native.Nodes.Clear()
        self.native.ImageList.Images.Clear()
        if source:
            for i, item in enumerate(source):
                self.insert(None, i, item)

    def insert(self, parent, index, item):
        node = self._create_node_recurse(item)

        if parent is None:
            self.native.Nodes.Insert(index, node)
        else:
            parent._impl.Nodes.Insert(index, node)

    def _create_node_recurse(self, item):
        text = self._item_text(item)
        node = WinForms.TreeNode(text)
        node.Tag = item
        item._impl = node

        icon = self._item_icon(item)
        if icon is not None:
            image_index = self._image_index(icon)
            node.ImageIndex = image_index
            node.SelectedImageIndex = image_index
        else:
            node.ImageIndex = -1
            node.SelectedImageIndex = -1

        for child in item:
            child_node = self._create_node_recurse(child)
            node.Nodes.Add(child_node)

        return node

    def _item_text(self, item):
        if not self.interface.accessors:
            return ""
        accessor = self.interface.accessors[0]
        val = getattr(item, accessor, None)
        if isinstance(val, tuple):
            val = val[1]
        if val is None:
            val = self.interface.missing_value
        return str(val)

    def _item_icon(self, item):
        if not self.interface.accessors:
            return None
        accessor = self.interface.accessors[0]
        val = getattr(item, accessor, None)
        icon = None
        if isinstance(val, tuple):
            if val[0] is not None:
                icon = val[0]
        else:
            try:
                icon = val.icon
            except AttributeError:
                pass
        return None if icon is None else icon._impl

    def _image_index(self, icon):
        images = self.native.ImageList.Images
        key = str(icon.path)
        index = images.IndexOfKey(key)
        if index == -1:
            index = images.Count
            images.Add(key, icon.bitmap)
        return index

    def change(self, item):
        node = item._impl
        node.Text = self._item_text(item)

        icon = self._item_icon(item)
        if icon is not None:
            image_index = self._image_index(icon)
            node.ImageIndex = image_index
            node.SelectedImageIndex = image_index
        else:
            node.ImageIndex = -1
            node.SelectedImageIndex = -1

    def remove(self, parent, index, item):
        node = item._impl
        if parent:
            parent._impl.Nodes.Remove(node)
        else:
            self.native.Nodes.Remove(node)
        item._impl = None

    def clear(self):
        self.native.Nodes.Clear()
        self.native.ImageList.Images.Clear()

    def get_selection(self):
        # TreeView supports only single selection
        node = self.native.SelectedNode
        if node:
            return node.Tag
        return None

    def winforms_after_select(self, sender, e):
        self.interface.on_select()

    def winforms_node_mouse_double_click(self, sender, e):
        self.interface.on_activate(node=e.Node.Tag)

    def expand_node(self, node):
        node._impl.Expand()

    def expand_all(self):
        self.native.ExpandAll()

    def collapse_node(self, node):
        node._impl.Collapse()

    def collapse_all(self):
        self.native.CollapseAll()

    def insert_column(self, index, heading, accessor):
        if index == 0:
            self.change_source(self.interface.data)

    def remove_column(self, index):
        if index == 0:
            self.change_source(self.interface.data)