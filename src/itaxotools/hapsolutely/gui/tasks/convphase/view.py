from itaxotools.convphase_gui.task.view import View as _View


class View(_View):
    def draw(self):
        super().draw()
        self.cards.title.setVisible(False)
