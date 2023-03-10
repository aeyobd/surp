from .coord import Length

class FigBase():
    children = [[]]
    floats = []
    h_pad = (Length(0),Length(0))
    v_pad = (Length(0),Length(0))

    @property
    def n_rows(self):
        if len(self.children[0]) == 0:
            return 0
        else:
            return len(self.children)

    @property
    def n_cols(self):
        return len(self.children[0])

    @property
    def n_children(self):
        return self.n_rows * self.n_cols

    @property
    def width(self):
        self.expand()
        return self._width

    @property
    def height(self):
        self.expand()
        return self._height

    def expand(self):
        self._width = Length(0)
        self._height = Length(0)

        for row in self.children:
            for child in row:
                self._width += child.width
                self._width += child.h_pad[0]
                self._width += child.h_pad[1]
                self._height += child.height
                self._height += child.v_pad[0]
                self._height += child.v_pad[1]

    def remove(self):
        pass

    def locate(self, a, b):
        pass
