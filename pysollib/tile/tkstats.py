## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##

__all__ = ['SingleGame_StatsDialog',
           'AllGames_StatsDialog',
           'FullLog_StatsDialog',
           'SessionLog_StatsDialog',
           'Status_StatsDialog',
           'Top_StatsDialog']

# imports
import os, string, sys, types
import time
import Tile as Tkinter
import tkFont

# PySol imports
from pysollib.mfxutil import destruct, Struct, kwdefault, KwStruct
from pysollib.mfxutil import format_time
##from pysollib.util import *
from pysollib.stats import PysolStatsFormatter
from pysollib.settings import TOP_TITLE

# Toolkit imports
from tkutil import bind, unbind_destroy, loadImage
from tkwidget import MfxDialog, MfxMessageDialog
from tkwidget import MfxScrolledCanvas

gettext = _


# FIXME - this file a quick hack and needs a rewrite

# /***********************************************************************
# //
# ************************************************************************/

class SingleGame_StatsDialog(MfxDialog):
    def __init__(self, parent, title, app, player, gameid, **kw):
        self.app = app
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.top_frame = top_frame
        self.createBitmaps(top_frame, kw)
        #
        self.player = player or _("Demo games")
        self.top.wm_minsize(200, 200)
        self.button = kw.default
        #
        ##createChart = self.create3DBarChart
        createChart = self.createPieChart
        ##createChart = self.createSimpleChart
##         if parent.winfo_screenwidth() < 800 or parent.winfo_screenheight() < 600:
##             createChart = self.createPieChart
##             createChart = self.createSimpleChart
        #
        self.font = self.app.getFont("default")
        self.tk_font = tkFont.Font(self.top, self.font)
        self.font_metrics = self.tk_font.metrics()
        self._calc_tabs()
        #
        won, lost = app.stats.getStats(player, gameid)
        createChart(app, won, lost, _("Total"))
        won, lost = app.stats.getSessionStats(player, gameid)
        createChart(app, won, lost, _("Current session"))
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    #
    # helpers
    #

    def _calc_tabs(self):
        #
        font = self.tk_font
        t0 = 160
        t = ''
        for i in (_("Won:"),
                  _("Lost:"),
                  _("Total:")):
            if len(i) > len(t):
                t = i
        t1 = font.measure(t)
##         t1 = max(font.measure(_("Won:")),
##                  font.measure(_("Lost:")),
##                  font.measure(_("Total:")))
        t1 += 10
        ##t2 = font.measure('99999')+10
        t2 = 45
        ##t3 = font.measure('100%')+10
        t3 = 45
        tx = (t0, t0+t1+t2, t0+t1+t2+t3)
        #
        ls = self.font_metrics['linespace']
        ls += 5
        ls = max(ls, 20)
        ty = (ls, 2*ls, 3*ls+15, 3*ls+25)
        #
        self.tab_x, self.tab_y = tx, ty

    def _getPwon(self, won, lost):
        pwon, plost = 0.0, 0.0
        if won + lost > 0:
            pwon = float(won) / (won + lost)
            pwon = min(max(pwon, 0.00001), 0.99999)
            plost = 1.0 - pwon
        return pwon, plost

    def _createChartInit(self, text):
        w, h = self.tab_x[-1]+20, self.tab_y[-1]+20
        c = Tkinter.Canvas(self.top_frame, width=w, height=h)
        c.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=0, padx=20, pady=10)
        self.canvas = c
        ##self.fg = c.cget("insertbackground")
        self.fg = c.option_get('foreground', '') or c.cget("insertbackground")
        #
        c.create_rectangle(2, 7, w, h, fill="", outline="#7f7f7f")
        l = Tkinter.Label(c, text=text, font=self.font, bd=0, padx=3, pady=1)
        dy = int(self.font_metrics['ascent']) - 10
        dy = dy/2
        c.create_window(20, -dy, window=l, anchor="nw")

    def _createChartTexts(self, tx, ty, won, lost):
        c, tfont, fg = self.canvas, self.font, self.fg
        pwon, plost = self._getPwon(won, lost)
        #
        x = tx[0]
        dy = int(self.font_metrics['ascent']) - 10
        dy = dy/2
        c.create_text(x, ty[0]-dy, text=_("Won:"), anchor="nw", font=tfont, fill=fg)
        c.create_text(x, ty[1]-dy, text=_("Lost:"), anchor="nw", font=tfont, fill=fg)
        c.create_text(x, ty[2]-dy, text=_("Total:"), anchor="nw", font=tfont, fill=fg)
        x = tx[1] - 16
        c.create_text(x, ty[0]-dy, text="%d" % won, anchor="ne", font=tfont, fill=fg)
        c.create_text(x, ty[1]-dy, text="%d" % lost, anchor="ne", font=tfont, fill=fg)
        c.create_text(x, ty[2]-dy, text="%d" % (won + lost), anchor="ne", font=tfont, fill=fg)
        y = ty[2] - 11
        c.create_line(tx[0], y, x, y, fill=fg)
        if won + lost > 0:
            x = tx[2]
            pw = int(round(100.0 * pwon))
            c.create_text(x, ty[0]-dy, text="%d%%" % pw, anchor="ne", font=tfont, fill=fg)
            c.create_text(x, ty[1]-dy, text="%d%%" % (100-pw), anchor="ne", font=tfont, fill=fg)


##     def _createChart3DBar(self, canvas, perc, x, y, p, col):
##         if perc < 0.005:
##             return
##         # translate and scale
##         p = list(p[:])
##         for i in (0, 1, 2, 3):
##             p[i] = (x + p[i][0], y + p[i][1])
##             j = i + 4
##             dx = int(round(p[j][0] * perc))
##             dy = int(round(p[j][1] * perc))
##             p[j] = (p[i][0] + dx, p[i][1] + dy)
##         # draw rects
##         def draw_rect(a, b, c, d, col, canvas=canvas, p=p):
##             points = (p[a][0], p[a][1], p[b][0], p[b][1],
##                       p[c][0], p[c][1], p[d][0], p[d][1])
##             canvas.create_polygon(points, fill=col)
##         draw_rect(0, 1, 5, 4, col[0])
##         draw_rect(1, 2, 6, 5, col[1])
##         draw_rect(4, 5, 6, 7, col[2])
##         # draw lines
##         def draw_line(a, b, canvas=canvas, p=p):
##             ##print a, b, p[a], p[b]
##             canvas.create_line(p[a][0], p[a][1], p[b][0], p[b][1])
##         draw_line(0, 1)
##         draw_line(1, 2)
##         draw_line(0, 4)
##         draw_line(1, 5)
##         draw_line(2, 6)
##         ###draw_line(3, 7)     ## test
##         draw_line(4, 5)
##         draw_line(5, 6)
##         draw_line(6, 7)
##         draw_line(7, 4)


    #
    # charts
    #

##     def createSimpleChart(self, app, won, lost, text):
##         #c, tfont, fg = self._createChartInit(frame, 300, 100, text)
##         self._createChartInit(300, 100, text)
##         c, tfont, fg = self.canvas, self.font, self.fg
##         #
##         tx = (90, 180, 210)
##         ty = (21, 41, 75)
##         self._createChartTexts(tx, ty, won, lost)

##     def create3DBarChart(self, app, won, lost, text):
##         image = app.gimages.stats[0]
##         iw, ih = image.width(), image.height()
##         #c, tfont, fg = self._createChartInit(frame, iw+160, ih, text)
##         self._createChartInit(iw+160, ih, text)
##         c, tfont, fg = self.canvas, self.font, self.fg
##         pwon, plost = self._getPwon(won, lost)
##         #
##         tx = (iw+20, iw+110, iw+140)
##         yy = ih/2 ## + 7
##         ty = (yy+21-46, yy+41-46, yy+75-46)
##         #
##         c.create_image(0, 7, image=image, anchor="nw")
##         #
##         p = ((0, 0), (44, 6), (62, -9), (20, -14),
##              (-3, -118), (-1, -120), (-1, -114), (-4, -112))
##         col = ("#00ff00", "#008200", "#00c300")
##         self._createChart3DBar(c, pwon,  102, 145+7, p, col)
##         p = ((0, 0), (49, 6), (61, -10), (15, -15),
##              (1, -123), (3, -126), (4, -120), (1, -118))
##         col = ("#ff0000", "#860400", "#c70400")
##         self._createChart3DBar(c, plost, 216, 159+7, p, col)
##         #
##         self._createChartTexts(tx, ty, won, lost)
##         c.create_text(tx[0], ty[0]-48, text=self.player, anchor="nw", font=tfont, fill=fg)

    def createPieChart(self, app, won, lost, text):
        #c, tfont, fg = self._createChartInit(frame, 300, 100, text)
        #
        self._createChartInit(text)
        c, tfont, fg = self.canvas, self.font, self.fg
        pwon, plost = self._getPwon(won, lost)
        #
        #tx = (160, 250, 280)
        #ty = (21, 41, 75)
        #
        tx, ty = self.tab_x, self.tab_y
        if won + lost > 0:
            ##s, ewon, elost = 90.0, -360.0 * pwon, -360.0 * plost
            s, ewon, elost = 0.0, 360.0 * pwon, 360.0 * plost
            c.create_arc(20, 25+9, 110, 75+9,  fill="#007f00", start=s, extent=ewon)
            c.create_arc(20, 25+9, 110, 75+9,  fill="#7f0000", start=s+ewon, extent=elost)
            c.create_arc(20, 25,   110, 75,    fill="#00ff00", start=s, extent=ewon)
            c.create_arc(20, 25,   110, 75,    fill="#ff0000", start=s+ewon, extent=elost)
            x, y = tx[0] - 25, ty[0]
            c.create_rectangle(x, y, x+10, y+10, fill="#00ff00")
            y = ty[1]
            c.create_rectangle(x, y, x+10, y+10, fill="#ff0000")
        else:
            c.create_oval(20, 25+10, 110, 75+10, fill="#7f7f7f")
            c.create_oval(20, 25,    110, 75,    fill="#f0f0f0")
            c.create_text(65, 50, text=_("No games"), anchor="center", font=tfont, fill="#bfbfbf")
        #
        self._createChartTexts(tx, ty, won, lost)

    #
    #
    #

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"),
                               (_("&All games..."), 102),
                               (TOP_TITLE+"...", 105),
                               (_("&Reset..."), 302)), default=0,
                      image=self.app.gimages.logos[5],
                      padx=10, pady=10,
        )
        return MfxDialog.initKw(self, kw)


# /***********************************************************************
# //
# ************************************************************************/

class CanvasWriter(PysolStatsFormatter.StringWriter):
    def __init__(self, canvas, parent_window, font, w, h):
        self.canvas = canvas
        self.parent_window = parent_window
        ##self.fg = canvas.cget("insertbackground")
        self.fg = canvas.option_get('foreground', '') or canvas.cget("insertbackground")
        self.font = font
        self.w = w
        self.h = h
        self.x = self.y = 0
        self.gameid = None
        self.gamenumber = None
        self.canvas.config(yscrollincrement=h)
        self._tabs = None

    def _addItem(self, id):
        self.canvas.dialog.nodes[id] = (self.gameid, self.gamenumber)

    def p(self, s):
        if self.y > 16000:
            return
        h1, h2 = 0, 0
        while s and s[0] == "\n":
            s = s[1:]
            h1 = h1 + self.h
        while s and s[-1] == "\n":
            s = s[:-1]
            h2 = h2 + self.h
        self.y = self.y + h1
        if s:
            id = self.canvas.create_text(self.x, self.y, text=s, anchor="nw",
                                         font=self.font, fill=self.fg)
            self._addItem(id)
        self.y = self.y + h2

    def pheader(self, s):
        pass

    def _calc_tabs(self, arg):
        tw = 15*self.w
        ##tw = 160
        self._tabs = [tw]
        font = tkFont.Font(self.canvas, self.font)
        for t in arg[1:]:
            tw = font.measure(t)+20
            self._tabs.append(tw)
        self._tabs.append(10)

    def pstats(self, *args, **kwargs):
        gameid=kwargs.get('gameid', None)
        header = False
        if self._tabs is None:
            # header
            header = True
            self._calc_tabs(args)
            self.gameid = 'header'
            self.gamenumber = None
##             if False:
##                 sort_by = ( 'name', 'played', 'won', 'lost',
##                             'time', 'moves', 'percent', )
##                 frame = Tkinter.Frame(self.canvas)
##                 i = 0
##                 for t in args:
##                     w = self._tabs[i]
##                     if i == 0:
##                         w += 10
##                     b = Tkinter.Button(frame, text=t)
##                     b.grid(row=0, column=i, sticky='ew')
##                     b.bind('<1>', lambda e, f=self.parent_window.rearrange, s=sort_by[i]: f(s))
##                     frame.columnconfigure(i, minsize=w)
##                     i += 1
##                 self.canvas.create_window(0, 0, window=frame, anchor='nw')
##                 self.y += 20
##                 return
##             if False:
##                 i = 0
##                 x = 0
##                 for t in args:
##                     w = self._tabs[i]
##                     h = 18
##                     anchor = 'ne'
##                     y = 0
##                     self.canvas.create_rectangle(x+2, y, x+w, y+h, width=1,
##                                      fill="#00ff00", outline="#000000")
##                     x += w
##                     self.canvas.create_text(x-3, y+3, text=t, anchor=anchor)
##                     i += 1
##                 self.y += 20
##                 return

        else:
            self.gameid = gameid
            self.gamenumber = None
        if self.y > 16000:
            return
        x, y = 1, self.y
        p = self._pstats_text
        t1, t2, t3, t4, t5, t6, t7 = args
        h = 0
        if not header: t1=gettext(t1)                        # game name

        for var, text, anchor, tab in (
            ('name',    t1, 'nw', self._tabs[0]+self._tabs[1]),
            ('played',  t2, 'ne', self._tabs[2]),
            ('won',     t3, 'ne', self._tabs[3]),
            ('lost',    t4, 'ne', self._tabs[4]),
            ('time',    t5, 'ne', self._tabs[5]),
            ('moves',   t6, 'ne', self._tabs[6]),
            ('percent', t7, 'ne', self._tabs[7]), ):
            if header: self.gamenumber=var
            h = max(h, p(x, y, anchor=anchor, text=text))
            x += tab

        self.pstats_perc(x, y, t7)
        self.y += h
        self.gameid = None
        return

##         h = max(h, p(x, y, anchor="nw", text=t1))
##         if header: self.gamenumber='played'
##         x += self._tabs[0]+self._tabs[1]
##         h = max(h, p(x, y, anchor="ne", text=t2))
##         if header: self.gamenumber='won'
##         x += self._tabs[2]
##         h = max(h, p(x, y, anchor="ne", text=t3))
##         if header: self.gamenumber='lost'
##         x += self._tabs[3]
##         h = max(h, p(x, y, anchor="ne", text=t4))
##         if header: self.gamenumber='time'
##         x += self._tabs[4]
##         h = max(h, p(x, y, anchor="ne", text=t5))
##         if header: self.gamenumber='moves'
##         x += self._tabs[5]
##         h = max(h, p(x, y, anchor="ne", text=t6))
##         if header: self.gamenumber='percent'
##         x += self._tabs[6]
##         h = max(h, p(x, y, anchor="ne", text=t7))
##         x += self._tabs[7]
##         self.pstats_perc(x, y, t7)
##         self.y += h
##         self.gameid = None

    def _pstats_text(self, x, y, **kw):
        kwdefault(kw, font=self.font, fill=self.fg)
        id = apply(self.canvas.create_text, (x, y), kw)
        self._addItem(id)
        return self.h
        ##bbox = self.canvas.bbox(id)
        ##return bbox[3] - bbox[1]

    def pstats_perc(self, x, y, t):
        if not (t and "0" <= t[0] <= "9"):
            return
        perc = int(round(float(str(t))))
        if perc < 1:
            return
        rx, ry, rw, rh = x, y+1, 2 + 8*10, self.h-5
        if 1:
            w = int(round(rw*perc/100.0))
            if 1 and w < 1:
                return
            if w > 0:
                w = max(3, w)
                w = min(rw - 2, w)
                id = self.canvas.create_rectangle(rx, ry, rx+w, ry+rh, width=1,
                                                  fill="#00ff00", outline="#000000")
            if w < rw:
                id = self.canvas.create_rectangle(rx+w, ry, rx+rw, ry+rh, width=1,
                                                  fill="#ff0000", outline="#000000")
            return
        ##fill = "#ffffff"
        ##fill = self.canvas["bg"]
        fill = None
        id = self.canvas.create_rectangle(rx, ry, rx+rw, ry+rh, width=1,
                                          fill=fill, outline="#808080")
        if 1:
            rx, rw = rx + 1, rw - 1
            ry, rh = ry + 1, rh - 1
            w = int(round(rw*perc/100.0))
            if w > 0:
                id = self.canvas.create_rectangle(rx, ry, rx+w, ry+rh, width=0,
                                                  fill="#00ff00", outline="")
            if w < rw:
                id = self.canvas.create_rectangle(rx+w, ry, rx+rw, ry+rh, width=0,
                                                  fill="#ff0000", outline="")
            return
        p = 1.0
        ix = rx + 2
        for i in (1, 11, 21, 31, 41, 51, 61, 71, 81, 91):
            if perc < i:
                break
            ##c = "#ff8040"
            r, g, b = 255, 128*p, 64*p
            c = "#%02x%02x%02x" % (int(r), int(g), int(b))
            id = self.canvas.create_rectangle(ix, ry+2, ix+6, ry+rh-2, width=0,
                                              fill=c, outline=c)
            ix = ix + 8
            p = max(0.0, p - 0.1)

    def plog(self, gamename, gamenumber, date, status, gameid=-1, won=-1):
        if gameid > 0 and "0" <= gamenumber[0:1] <= "9":
            self.gameid = gameid
            self.gamenumber = gamenumber
        self.p("%-25s %-20s  %17s  %s\n" % (gamename, gamenumber, date, status))
        self.gameid = None
        self.gamenumber = None


# /***********************************************************************
# //
# ************************************************************************/

class AllGames_StatsDialogScrolledCanvas(MfxScrolledCanvas):
    pass


class AllGames_StatsDialog(MfxDialog):
    # for font "canvas_fixed"
    #CHAR_W, CHAR_H = 7, 16
    #if os.name == "mac": CHAR_W = 6
    #
    YVIEW = 0
    FONT_TYPE = "default"

    def __init__(self, parent, title, app, player, **kw):
        lines = 25
        #if parent and parent.winfo_screenheight() < 600:
        #    lines = 20
        #
        self.font = app.getFont(self.FONT_TYPE)
        font = tkFont.Font(parent, self.font)
        self.font_metrics = font.metrics()
        self.CHAR_H = self.font_metrics['linespace']
        self.CHAR_W = font.measure('M')
        self.app = app
        #
        self.player = player
        self.title = title
        self.sort_by = 'name'
        #
        kwdefault(kw, width=self.CHAR_W*64, height=lines*self.CHAR_H)
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.top.wm_minsize(200, 200)
        self.button = kw.default
        #
        self.sc = AllGames_StatsDialogScrolledCanvas(top_frame,
                                       width=kw.width, height=kw.height)
        self.sc.pack(fill=Tkinter.BOTH, expand=1, padx=kw.padx, pady=kw.pady)
        #
        self.nodes = {}
        self.canvas = self.sc.canvas
        self.canvas.dialog = self
        bind(self.canvas, "<1>", self.singleClick)
        self.fillCanvas(player, title)
        bbox = self.canvas.bbox("all")
        ##print bbox
        ##self.canvas.config(scrollregion=bbox)
        dx, dy = 4, 0
        self.canvas.config(scrollregion=(-dx,-dy,bbox[2]+dx,bbox[3]+dy))
        self.canvas.xview_moveto(-dx)
        self.canvas.yview_moveto(self.YVIEW)
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"),
                               (_("&Save to file"), 202),
                               (_("&Reset all..."), 301),),
                      default=0,
                      resizable=1,
                      padx=10, pady=10,
                      #width=900,
        )
        return MfxDialog.initKw(self, kw)

    def destroy(self):
        self.app = None
        self.canvas.dialog = None
        self.nodes = {}
        self.sc.destroy()
        MfxDialog.destroy(self)

    def rearrange(self, sort_by):
        if self.sort_by == sort_by: return
        self.sort_by = sort_by
        self.fillCanvas(self.player, self.title)

    def singleClick(self, event=None):
        id = self.canvas.find_withtag(Tkinter.CURRENT)
        if not id:
            return
        ##print id, self.nodes.get(id[0])
        gameid, gamenumber = self.nodes.get(id[0], (None, None))
        if gameid == 'header':
            if self.sort_by == gamenumber: return
            self.sort_by = gamenumber
            self.fillCanvas(self.player, self.title)
            return
        ## FIXME / TODO
        return
        if gameid and gamenumber:
            print gameid, gamenumber
        elif gameid:
            print gameid

    #
    #
    #

    def fillCanvas(self, player, header):
        self.canvas.delete('all')
        self.nodes = {}
        a = PysolStatsFormatter(self.app)
        #print 'CHAR_W:', self.CHAR_W
        writer = CanvasWriter(self.canvas, self,
                              self.font, self.CHAR_W, self.CHAR_H)
        if not a.writeStats(writer, player, header, sort_by=self.sort_by):
            writer.p(_("No entries for player ") + player + "\n")
        destruct(writer)
        destruct(a)


# /***********************************************************************
# //
# ************************************************************************/

class FullLog_StatsDialog(AllGames_StatsDialog):
    YVIEW = 1
    FONT_TYPE = "fixed"

    def fillCanvas(self, player, header):
        a = PysolStatsFormatter(self.app)
        writer = CanvasWriter(self.canvas, self, self.font, self.CHAR_W, self.CHAR_H)
        if not a.writeFullLog(writer, player, header):
            writer.p(_("No log entries for %s\n") % player)
        destruct(a)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), (_("Session &log..."), 104), (_("&Save to file"), 203)), default=0,
                      width=76*self.CHAR_W,
                      )
        return AllGames_StatsDialog.initKw(self, kw)


class SessionLog_StatsDialog(FullLog_StatsDialog):
    def fillCanvas(self, player, header):
        a = PysolStatsFormatter(self.app)
        writer = CanvasWriter(self.canvas, self, self.font, self.CHAR_W, self.CHAR_H)
        if not a.writeSessionLog(writer, player, header):
            writer.p(_("No current session log entries for %s\n") % player)
        destruct(a)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), (_("&Full log..."), 103), (_("&Save to file"), 204)), default=0,
                      )
        return FullLog_StatsDialog.initKw(self, kw)

# /***********************************************************************
# //
# ************************************************************************/

class Status_StatsDialog(MfxMessageDialog):
    def __init__(self, parent, game):
        stats, gstats = game.stats, game.gstats
        w1 = w2 = ""
        n = 0
        for s in game.s.foundations:
            n = n + len(s.cards)
        w1 = (_("Highlight piles: ") + str(stats.highlight_piles) + "\n" +
              _("Highlight cards: ") + str(stats.highlight_cards) + "\n" +
              _("Highlight same rank: ") + str(stats.highlight_samerank) + "\n")
        if game.s.talon:
            if game.gameinfo.redeals != 0:
                w2 = w2 + _("\nRedeals: ") + str(game.s.talon.round - 1)
            w2 = w2 + _("\nCards in Talon: ") + str(len(game.s.talon.cards))
        if game.s.waste and game.s.waste not in game.s.foundations:
            w2 = w2 + _("\nCards in Waste: ") + str(len(game.s.waste.cards))
        if game.s.foundations:
            w2 = w2 + _("\nCards in Foundations: ") + str(n)
        #
        date = time.strftime("%Y-%m-%d %H:%M", time.localtime(game.gstats.start_time))
        MfxMessageDialog.__init__(self, parent, title=_("Game status"),
                                  text=game.getTitleName() + "\n" +
                                  game.getGameNumber(format=1) + "\n" +
                                  _("Playing time: ") + game.getTime() + "\n" +
                                  _("Started at: ") + date + "\n\n"+
                                  _("Moves: ") + str(game.moves.index) + "\n" +
                                  _("Undo moves: ") + str(stats.undo_moves) + "\n" +
                                  _("Bookmark moves: ") + str(gstats.goto_bookmark_moves) + "\n" +
                                  _("Demo moves: ") + str(stats.demo_moves) + "\n" +
                                  _("Total player moves: ") + str(stats.player_moves) + "\n" +
                                  _("Total moves in this game: ") + str(stats.total_moves) + "\n" +
                                  _("Hints: ") + str(stats.hints) + "\n" +
                                  "\n" +
                                  w1 + w2,
                                  strings=(_("&OK"),
                                           (_("&Statistics..."), 101),
                                           (TOP_TITLE+"...", 105), ),
                                  image=game.app.gimages.logos[3],
                                  image_side="left", image_padx=20,
                                  padx=20,
                                  )

# /***********************************************************************
# //
# ************************************************************************/

class _TopDialog(MfxDialog):
    def __init__(self, parent, title, top, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        cnf = {'master': top_frame,
               'highlightthickness': 1,
               'highlightbackground': 'black',
               }
        frame = apply(Tkinter.Frame, (), cnf)
        frame.pack(expand=Tkinter.YES, fill=Tkinter.BOTH, padx=10, pady=10)
        frame.columnconfigure(0, weight=1)
        cnf['master'] = frame
        cnf['text'] = _('N')
        l = apply(Tkinter.Label, (), cnf)
        l.grid(row=0, column=0, sticky='ew')
        cnf['text'] = _('Game number')
        l = apply(Tkinter.Label, (), cnf)
        l.grid(row=0, column=1, sticky='ew')
        cnf['text'] = _('Started at')
        l = apply(Tkinter.Label, (), cnf)
        l.grid(row=0, column=2, sticky='ew')
        cnf['text'] = _('Result')
        l = apply(Tkinter.Label, (), cnf)
        l.grid(row=0, column=3, sticky='ew')

        row = 1
        for i in top:
            # N
            cnf['text'] = str(row)
            l = apply(Tkinter.Label, (), cnf)
            l.grid(row=row, column=0, sticky='ew')
            # Game number
            cnf['text'] = '#'+str(i.game_number)
            l = apply(Tkinter.Label, (), cnf)
            l.grid(row=row, column=1, sticky='ew')
            # Start time
            t = time.strftime('%Y-%m-%d %H:%M', time.localtime(i.game_start_time))
            cnf['text'] = t
            l = apply(Tkinter.Label, (), cnf)
            l.grid(row=row, column=2, sticky='ew')
            # Result
            if isinstance(i.value, float):
                # time
                s = format_time(i.value)
            else:
                # moves
                s = str(i.value)
            cnf['text'] = s
            l = apply(Tkinter.Label, (), cnf)
            l.grid(row=row, column=3, sticky='ew')
            row += 1

        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)


    def initKw(self, kw):
        kw = KwStruct(kw, strings=(_('&OK'),), default=0, separatorwidth=2)
        return MfxDialog.initKw(self, kw)


class Top_StatsDialog(MfxDialog):
    def __init__(self, parent, title, app, player, gameid, **kw):
        self.app = app
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        frame = Tkinter.Frame(top_frame)
        frame.pack(expand=Tkinter.YES, fill=Tkinter.BOTH, padx=5, pady=10)
        frame.columnconfigure(0, weight=1)

        if (app.stats.games_stats.has_key(player) and
            app.stats.games_stats[player].has_key(gameid) and
            app.stats.games_stats[player][gameid].time_result.top):

            Tkinter.Label(frame, text=_('Minimum')).grid(row=0, column=1)
            Tkinter.Label(frame, text=_('Maximum')).grid(row=0, column=2)
            Tkinter.Label(frame, text=_('Average')).grid(row=0, column=3)
            ##Tkinter.Label(frame, text=_('Total')).grid(row=0, column=4)

            s = app.stats.games_stats[player][gameid]
            row = 1
            ll = [
                (_('Playing time:'),
                 format_time(s.time_result.min),
                 format_time(s.time_result.max),
                 format_time(s.time_result.average),
                 format_time(s.time_result.total),
                 s.time_result.top,
                 ),
                (_('Moves:'),
                 s.moves_result.min,
                 s.moves_result.max,
                 round(s.moves_result.average, 2),
                 s.moves_result.total,
                 s.moves_result.top,
                 ),
                (_('Total moves:'),
                 s.total_moves_result.min,
                 s.total_moves_result.max,
                 round(s.total_moves_result.average, 2),
                 s.total_moves_result.total,
                 s.total_moves_result.top,
                 ),
                ]
##             if s.score_result.min:
##                 ll.append(('Score:',
##                            s.score_result.min,
##                            s.score_result.max,
##                            round(s.score_result.average, 2),
##                            s.score_result.top,
##                            ))
##             if s.score_casino_result.min:
##                 ll.append(('Casino Score:',
##                            s.score_casino_result.min,
##                            s.score_casino_result.max,
##                            round(s.score_casino_result.average, 2), ))
            for l, min, max, avr, tot, top in ll:
                Tkinter.Label(frame, text=l).grid(row=row, column=0)
                Tkinter.Label(frame, text=str(min)).grid(row=row, column=1)
                Tkinter.Label(frame, text=str(max)).grid(row=row, column=2)
                Tkinter.Label(frame, text=str(avr)).grid(row=row, column=3)
                ##Tkinter.Label(frame, text=str(tot)).grid(row=row, column=4)
                b = Tkinter.Button(frame, text=TOP_TITLE+' ...', width=10,
                                   command=lambda top=top: self.showTop(top))
                b.grid(row=row, column=5)
                row += 1
        else:
            Tkinter.Label(frame, text=_('No TOP for this game')).pack()

        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    def showTop(self, top):
        #print top
        d = _TopDialog(self.top, TOP_TITLE, top)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_('&OK'),),
                      default=0,
                      image=self.app.gimages.logos[4],
                      separatorwidth=2,
                      )
        return MfxDialog.initKw(self, kw)