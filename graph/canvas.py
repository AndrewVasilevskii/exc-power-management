import matplotlib

matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
import numpy as np
import math

class Canvas(FigureCanvas):
    def __init__(self, panel, par, figure, zoom=-1):
        # ensure the parent's __init__ is called
        super(Canvas, self).__init__(panel, par, figure)
        self.enableLegend = True
        self.figure = figure
        self.zoom = zoom
        self.axis = figure.add_subplot(111)
        self.axis2 = self.axis.twinx()
        self.numberOfPlots = 0
    # self.dataprovider = DataProvider()
    # self.datagenerator = DataGenerator(self.dataprovider)

    def drawLinePlot(self, graphs):
        lines1 = []
        lines2 = []
        nums = np.arange(0, 10)
        startStep = 0
        self.numberOfPlots= 0
        for gr in graphs:
            if len(gr.sumInt) == 0:
                continue
            data = np.arange(0, len(gr.sumInt))
            nums = np.arange(0, len(gr.sumInt))

            if not gr.isLine:
                data = np.array(gr.sumInt)
                size = data.size
                nums = np.arange(0, size)
                if self.zoom != -1:
                    arr = gr.sumInt
                    size = len(arr)
                    nums = np.arange(0, len(arr))
                    if len(arr) > self.zoom:
                        newLen = self.zoom * -1
                        arr = arr[newLen:]
                        startStep = size - self.zoom
                        nums = np.arange(size - self.zoom, size)
                        data = np.array(arr)
                posStr = " (Left)"
                if gr.position == 1:
                    posStr = " (Right)"
                if gr.position == 0:
                    self.axis.plot(nums, data, gr.color, label=str(gr.mass) + posStr)
                    self.numberOfPlots += 1
                else:
                    self.axis2.plot(nums, data, gr.color, label=str(gr.mass) + posStr)
                    self.numberOfPlots += 1
        self.figure.legends.clear()
        self.figure.legend(ncol=math.ceil(self.numberOfPlots/2), borderaxespad=0.2)
    #           if self.zoom != -1:
    #               self.figure.legend()

    #             maxValue = np.amax(data)

    #             #data = np.vstack((nums, data)).reshape((-1,),order='F')
    #             data.shape = (size, 2)
    #             line = PolyLine(data, legend='mass ' + str(gr.mass), colour=gr.color, width=2)
    #             lines.append(line)

    #             maxData = np.empty(size)
    #             maxData.fill(maxValue)
    #             maxData = np.vstack((nums, maxData)).reshape((-1,),order='F')
    #             maxData.shape = (size, 2)
    #             line = PolyLine(maxData, legend='max mass ' +  str(gr.mass), colour=gr.color, width=1)
    #             lines.append(line)
    #   lines1.append(object)

    #         if self.dataprovider.mzs.size > 0:
    #             mz = self.dataprovider.mzs[0]
    #             spec1 = self.dataprovider.rawData[0]
    #             size = spec1.size
    #             nums = np.arange(0, size)
    #             mz = np.vstack((nums, spec1)).reshape((-1,),order='F')
    #             mz.shape = (spec1.size, 2)
    #             line = PolyLine(mz, legend='mz/spec1', colour="black", width=1)
    #             lines.append(line)
    #
    #
    #         data1 = np.arange(0, 1)
    #         data2 = np.arange(0, 1)
    #         data1 = np.vstack((data1, data2))
    #         data1.shape = (1, 2)
    #
    #         line1 = PolyLine(data1, legend='', colour='white', width=1)
    #         lines.append(line1)
    #
    #         return PlotGraphics(lines, "", "", "")

    def redraw(self, graphs):
        self.axis.clear()
        self.axis2.clear()
        self.drawLinePlot(graphs)
        self.draw()
        # self.Draw(self.drawLinePlot())
        return self.axis.get_xlim()[1]

