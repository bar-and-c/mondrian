import logging
import wx
from wx.lib.pubsub import pub as Publisher

MONITOR_RELATIVE_SIZE = 0.2
MONITOR_EDGE_MARGIN = 20

STATUS_GOOD = 0
STATUS_ALMOST_GOOD = 1
STATUS_ALMOST_BAD = 2
STATUS_BAD = 3

COLOUR_STATUS_GOOD = 'white'
COLOUR_STATUS_ALMOST_GOOD = 'blue'
COLOUR_STATUS_ALMOST_BAD = 'yellow'
COLOUR_STATUS_BAD = 'red'
LINE_COLOUR = 'black'

status_colour = {STATUS_GOOD : COLOUR_STATUS_GOOD,
                 STATUS_ALMOST_GOOD : COLOUR_STATUS_ALMOST_GOOD,
                 STATUS_ALMOST_BAD : COLOUR_STATUS_ALMOST_BAD,
                 STATUS_BAD : COLOUR_STATUS_BAD}

LINE_WIDTH_PART = 0.01

SHUTDOWN_PUBSUB = "shutdown"
RESIZE_PUBSUB = "resize"
UPDATE_BUILD_PUBSUB = "update_build"
UPDATE_CI_TEST_PUBSUB = "update_ci_test"
UPDATE_OTHER_TESTS_PUBSUB = "update_other_test"
UPDATE_GERRIT_FOR_REVIEW_PUBSUB = "update_ready_for_review"
UPDATE_GERRIT_REVIEWED_PUBSUB = "update_reviewed"


# This defines how much space each "column/row" should take, the proportions.
FIRST_COLUMN_WEIGHT = 2
SECOND_COLUMN_WEIGHT = 16
THIRD_COLUMN_WEIGHT = 7
FIRST_ROW_WEIGHT = 2
SECOND_ROW_WEIGHT = 18
THIRD_ROW_WEIGHT = 3

# Special panels, breaking the grid
JENKINS_CI_TEST_WEIGHT = 3
JENKINS_OTHER_TESTS_WEIGHT = 2
GERRIT_FOR_REVIEW_WEIGHT = 9
GERRIT_REVIEWED_WEIGHT = 7

class MonitorPanel(wx.Panel):
    """A panel wwhich draws a black border around its edges.
       The line width is updated when the main window resizes."""
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.line_width = 5  # Initial width, updated through resize pubsub
        self.SetBackgroundColour(COLOUR_STATUS_GOOD)
        Publisher.subscribe(self.update_line_width, RESIZE_PUBSUB)

    def on_paint(self, event):
        (width, height) = self.GetSize()
        dc = wx.PaintDC(self)
        pen = wx.Pen(LINE_COLOUR, width=self.line_width)
        dc.SetPen(pen)
        dc.SetBrush(wx.Brush('white', style=wx.TRANSPARENT))
        dc.DrawRectangle(0, 0, width, height)

    def update_line_width(self, line_width):
        self.line_width = line_width


class MainPanel(wx.Panel):

    def __init__(self, parent):
        """The main panel. It contains a number ow panels arranged in a Mondrian like fashion.
           Some are all white, some are possible to update their colour."""
        wx.Panel.__init__(self, parent)

        self.jenkins_build_panel = MonitorPanel(self)
        self.jenkins_ci_test_panel = MonitorPanel(self)
        self.jenkins_other_test_panel = MonitorPanel(self)
        self.gerrit_for_review_panel = MonitorPanel(self)
        self.gerrit_reviewed_panel = MonitorPanel(self)

        first_row = wx.BoxSizer(wx.HORIZONTAL)
        second_row = wx.BoxSizer(wx.HORIZONTAL)
        third_row = wx.BoxSizer(wx.HORIZONTAL)

        first_row.Add(MonitorPanel(self), FIRST_COLUMN_WEIGHT, wx.EXPAND)
        first_row.Add(MonitorPanel(self), SECOND_COLUMN_WEIGHT, wx.EXPAND)
        first_row.Add(MonitorPanel(self), THIRD_COLUMN_WEIGHT, wx.EXPAND)

        jenkins_test_sizer = wx.BoxSizer(wx.VERTICAL)
        jenkins_test_sizer.Add(self.jenkins_ci_test_panel, JENKINS_CI_TEST_WEIGHT, wx.EXPAND)
        jenkins_test_sizer.Add(self.jenkins_other_test_panel, JENKINS_OTHER_TESTS_WEIGHT, wx.EXPAND)

        second_row.Add(MonitorPanel(self), FIRST_COLUMN_WEIGHT, wx.EXPAND)
        second_row.Add(self.jenkins_build_panel, SECOND_COLUMN_WEIGHT, wx.EXPAND)
        second_row.Add(jenkins_test_sizer, THIRD_COLUMN_WEIGHT, wx.EXPAND)

        gerrit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        gerrit_sizer.Add(self.gerrit_for_review_panel, GERRIT_FOR_REVIEW_WEIGHT, wx.EXPAND)
        gerrit_sizer.Add(self.gerrit_reviewed_panel, GERRIT_REVIEWED_WEIGHT, wx.EXPAND)
        third_row.Add(MonitorPanel(self), FIRST_COLUMN_WEIGHT, wx.EXPAND)
        third_row.Add(gerrit_sizer, SECOND_COLUMN_WEIGHT, wx.EXPAND)
        third_row.Add(MonitorPanel(self), THIRD_COLUMN_WEIGHT, wx.EXPAND)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(first_row, FIRST_ROW_WEIGHT, wx.EXPAND)
        box.Add(second_row, SECOND_ROW_WEIGHT, wx.EXPAND)
        box.Add(third_row, THIRD_ROW_WEIGHT, wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

        Publisher.subscribe(self.update_build_display, UPDATE_BUILD_PUBSUB)
        Publisher.subscribe(self.update_ci_test_display, UPDATE_CI_TEST_PUBSUB)
        Publisher.subscribe(self.update_other_test_display, UPDATE_OTHER_TESTS_PUBSUB)
        Publisher.subscribe(self.update_ready_for_review_display, UPDATE_GERRIT_FOR_REVIEW_PUBSUB)
        Publisher.subscribe(self.update_reviewed_display, UPDATE_GERRIT_REVIEWED_PUBSUB)

    def update_panel(self, panel, colour):
        panel.SetBackgroundColour(colour)
        panel.Refresh()

    def update_build_display(self, status):
        logging.debug('build status: %d', status)
        wx.CallAfter(self.update_panel, self.jenkins_build_panel, status_colour[status])

    def update_ci_test_display(self, status):
        logging.debug('ci test status: %d', status)
        wx.CallAfter(self.update_panel, self.jenkins_ci_test_panel, status_colour[status])

    def update_other_test_display(self, status):
        logging.debug('other test status: %d', status)
        wx.CallAfter(self.update_panel, self.jenkins_other_test_panel, status_colour[status])

    def update_ready_for_review_display(self, status):
        logging.debug('ready for review status: %d', status)
        wx.CallAfter(self.update_panel, self.gerrit_for_review_panel, status_colour[status])

    def update_reviewed_display(self, status):
        logging.debug('reviewed status: %d', status)
        wx.CallAfter(self.update_panel, self.gerrit_reviewed_panel, status_colour[status])


class MyForm(wx.Frame):
    """The main form. Possible to run full screen. Posts updates of new 'Mondrian line
       width' when resizing."""
    def __init__(self, full_screen=True, top_window=False):

        if top_window:
            win_style = wx.CLIP_CHILDREN | wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR | \
                      wx.NO_BORDER | wx.FRAME_SHAPED | wx.DEFAULT_FRAME_STYLE
        else:
            win_style = wx.DEFAULT_FRAME_STYLE

        (win_pos, win_size) = self.top_right()

        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY, title="Mondrian",
                          style=win_style, pos=win_pos, size=win_size)

        # EVT_KEY_DOWN doesn't seem to work on OS X
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        self.Bind(wx.EVT_SIZE, self.on_size)

        Publisher.subscribe(self.shutdown, SHUTDOWN_PUBSUB)

        MainPanel(self)
        self.Show()

        if full_screen:
            self.ShowFullScreen(True)

    def top_right(self):
        (display_width, display_height) = wx.DisplaySize()
        width = display_width * MONITOR_RELATIVE_SIZE
        height = display_height * MONITOR_RELATIVE_SIZE
        x = display_width - width - MONITOR_EDGE_MARGIN
        y = MONITOR_EDGE_MARGIN  # Just some "normal" position near the top
        return (wx.Point(x, y), wx.Size(width, height))

    def shutdown(self):
        self.Close()

    def on_key(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self.Close()
        else:
            event.Skip()

    def on_size(self, event):
        self.update_line_width()
        event.Skip()

    def update_line_width(self):
        new_line_width = self.GetSize()[0] * LINE_WIDTH_PART
        Publisher.sendMessage(RESIZE_PUBSUB, line_width=new_line_width)


def run(full_screen=True, top_window=False):
    app = wx.App()
    MyForm(full_screen, top_window)
    app.MainLoop()


if __name__ == "__main__":
    # Just for test...
    run(full_screen=False, top_window=True)
