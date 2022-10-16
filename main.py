#!/usr/bin/env python
import sys
from tkinter import *

import networkx as nx
import threading

# modules/libs needed : networkx

SCALING_FACTOR = 50
OFFSET_FACTOR = 0.5
# Actual value 
BOARD_SIZE = None
## Dictionary to store the widget information
widgetInfoDict = {}
# widgetInfoDict {  "root" : <root widget object (main window")>,
#                   "pw"    : <reference to paned window inside the top (horizontal)>,
#                   "lf1"   : <reference to label_frame1 inside the horizontal paned window>
#                   "lf2"   : <reference to label_frame2 inside the horizontal paned window>
#                   "text"  : <reference to text widget inside the label_frame1>,
#                   "canvas"  : <reference to canvas widget inside the label_frame1>,
#               }

## Dictionary to store coin info
coinInfoDict = {}
# coinInfoDict {  "<coin_1>" : [<x_cord> , <y_cord>],
#                   "<coin_2>" : [<x_cord> , <y_cord>] 
#               }

coinsPresenceInfo = []

shapesInfoDict = {}

#thread variables
masterThread = None
threads = []
THREADS = 5
## Graph to create the hierarchy of shape create sequence and to store the shape properties
#   Shapes are the nodes in the graph, reference shape defines the directed edge/arc between those shapes
placeInfoGraph = nx.DiGraph()
placeInfoGraphLock = threading.Lock() 


## Function to create the toplevel window, text and canvas widget
#
def createEditor(fileContent):
    # main tkinter window
    widgetInfoDict["root"] = Tk()
    widgetInfoDict["root"].geometry(str(widgetInfoDict["root"].winfo_screenwidth()) + 'x' + str(
        int(widgetInfoDict["root"].winfo_screenheight() * 0.9)))

    # panedwindow object

    widgetInfoDict["pw"] = PanedWindow(widgetInfoDict["root"], orient='horizontal')

    widgetInfoDict["lf1"] = LabelFrame(widgetInfoDict["root"], text='Editor', width=500)
    widgetInfoDict["lf1"].pack(expand='yes', fill=BOTH)

    widgetInfoDict["lf2"] = LabelFrame(widgetInfoDict["root"], text='Canvas', width=500)
    widgetInfoDict["lf2"].pack(expand='yes', fill=BOTH)

    widgetInfoDict["text"] = Text(widgetInfoDict["lf1"])
    widgetInfoDict["text"].pack(fill=BOTH, expand=True)

    widgetInfoDict["canvas"] = Canvas(widgetInfoDict["lf2"])
    widgetInfoDict["canvas"].pack(fill=BOTH, expand=True)

    widgetInfoDict["canvas"].pack()

    widgetInfoDict["pw"].add(widgetInfoDict["lf1"])
    widgetInfoDict["pw"].add(widgetInfoDict["lf2"])
    widgetInfoDict["pw"].pack(fill=BOTH, expand=True)
    widgetInfoDict["pw"].configure(sashrelief=RAISED)

    renderBoard(BOARD_SIZE)

    btn = Button(widgetInfoDict["lf1"], text='Evaluate', bd='5', command=placeSequence)
    btn.pack(side='bottom')
    widgetInfoDict["text"].insert(END, fileContent)
    widgetInfoDict["root"].mainloop()


## Function to read the data from sequence cmds (placeSequence.txt) file and write to the text editor
#
#   @param placementSwqCmdsFile : Reference to the area.txt file path
#
def fillEditor(placmntSeqCmdsFile):
    with open(placmntSeqCmdsFile, 'r') as cmdFileObj:
        fileContent = cmdFileObj.read()
        # widgetInfoDict["text"].insert(END, fileContent)
        return fileContent


## Function to draw the board on the canvas
#
#   @param boardSize : integer number.
#
def renderBoard(boardSize):
    renderRectangle([0, 0, boardSize, boardSize], "board")
    for n in range(boardSize):
        renderLine([n, 0, n, boardSize])
        renderLine([0, n, boardSize, n])
    return


## Function to draw the rectangle on the canvas using the coordinates
#
#   @param coord : tuple with lower left and upper right coordinates
#   @param name : Reference to the shape name
#
# Info : In tkinter, rectangle/square can be drawn by passing the lower left and upper right coordinates, ex: to draw a
# 5(l), 7(b) rectangle from origin, coordinates are (0,0) and (5,7)
#
def renderRectangle(coords, name=None):
    coords = [coord * SCALING_FACTOR for coord in coords]
    coordref = widgetInfoDict["canvas"].create_rectangle(coords[0], coords[1], coords[2], coords[3])
    # ref 'coordref' can be used to print the coordinates of the rendered name, i.e.
    print(widgetInfoDict["canvas"].coords(coordref))
    # Add the shape name to the rendered name
    if name:
        widgetInfoDict["canvas"].create_text((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2, text=name)


## Function to draw a line on the canvas using the coordinates
#
#   @param coord : [x1, y1, x2, y2]
#   @param color : Color of the line
#   @param name :  Reference to the line name
#
def renderLine(coords, color="black", name=None):
    coords = [coord * SCALING_FACTOR for coord in coords]
    coordref = widgetInfoDict["canvas"].create_line(coords[0], coords[1], coords[2], coords[3], fill=color)
    # ref 'coordref' can be used to print the coordinates of the rendered name, i.e.
    print(widgetInfoDict["canvas"].coords(coordref))
    # Add the shape name to the rendered name
    if name:
        widgetInfoDict["canvas"].create_text((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2, text=name)


## Function to read the coordinate information from the file
#
#   @param coinInfoFile : Reference to the shapeDimensionFile path
#
def readCoinInfoFromFile(coinInfoFile):
    with open(coinInfoFile, 'r') as coinFileObj:
        for line in coinFileObj:
            dataLst = line.split()
            if len(dataLst) != 3:
                print("Couldn't process the line " + line + " in " + str(
                    coinInfoFile) + "due to missing of information. Format is '<coin_name> <x_cord> <y_cord>', "
                                     "hence skipping this line")
                continue
            coinInfoDict[dataLst[0]] = [int(dataLst[1]), int(dataLst[2])]
            coinsPresenceInfo[int(dataLst[1]) * BOARD_SIZE + int(dataLst[2])] = 1


def renderSnake(coords, name):
    if coinsPresenceInfo[coords[0] * BOARD_SIZE + coords[1]]:
        coinsPresenceInfo[coords[0] * BOARD_SIZE + coords[1]] = 0
        coinsPresenceInfo[coords[2] * BOARD_SIZE + coords[3]] = 1
    coords = [(coord + OFFSET_FACTOR) * SCALING_FACTOR for coord in coords]
    coordref = widgetInfoDict["canvas"].create_line(coords[0], coords[1], coords[2], coords[3], fill='red', arrow=LAST)
    # ref 'coordref' can be used to print the coordinates of the rendered name, i.e.
    print(widgetInfoDict["canvas"].coords(coordref))
    # Add the shape name to the rendered name
    if name:
        widgetInfoDict["canvas"].create_text((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2, text=name)


def renderLadder(coords, name):
    if coinsPresenceInfo[coords[0] * BOARD_SIZE + coords[1]]:
        coinsPresenceInfo[coords[0] * BOARD_SIZE + coords[1]] = 0
        coinsPresenceInfo[coords[2] * BOARD_SIZE + coords[3]] = 1
    coords = [(coord + OFFSET_FACTOR) * SCALING_FACTOR for coord in coords]
    coordref = widgetInfoDict["canvas"].create_line(coords[0], coords[1], coords[2], coords[3], fill='green',
                                                    arrow=LAST)
    # ref 'coord-ref' can be used to print the coordinates of the rendered name, i.e.
    print(widgetInfoDict["canvas"].coords(coordref))
    # Add the shape name to the rendered name
    if name:
        widgetInfoDict["canvas"].create_text((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2, text=name)


## Function to draw the shape on the canvas using the coordinates
#
#   @param coord : tuple with lower left and upper right coordinates
#   @param shape : Reference to the shape name
#
# Info : In tkinter, rectangle/square can be drawn by passing the lower left and upper right coordinates, ex: to draw a
# 5(l), 7(b) rectangle from origin, coordinates are (0,0) and (5,7)
#
def renderToCanvas(coords, shape):
    if shape.startswith('Snake'):
        renderSnake(coords, shape)
    elif shape.startswith('Ladder'):
        renderLadder(coords, shape)


def renderCoins():
    for idx, val in enumerate(coinsPresenceInfo):
        x, y = (idx // BOARD_SIZE) + 0.25, (idx % BOARD_SIZE) + 0.25
        # x, y = int(coords[0]) + 0.25, int(coords[1]) + 0.25
        if val:
            widgetInfoDict["canvas"].create_oval(x * SCALING_FACTOR, y * SCALING_FACTOR, (x + 0.5) * SCALING_FACTOR,
                                                 (y + 0.5) * SCALING_FACTOR, fill="cyan")


## Function to read the information from the file
#
#   @param shapeDimensionFile : Reference to the shapeDimensionFile path
#
def readDimensionFromFile(shapeDimensionFile):
    with open(shapeDimensionFile, 'r') as dimFileObj:
        for line in dimFileObj:
            dataLst = line.split(" ")
            if len(dataLst) < 2:
                print(
                    "couldn't process the line " + line + "due to missing of information, format is '<shape_name> "
                                                          "<area>', hence skipping this line")
                continue
            shapesInfoDict[dataLst[0]] = int(dataLst[1])


## Function to calculate the absolute coordinate of the shape by considering the ref-shape and offset and render the
# shape to the canvas
def calculateShapeDependency():
    # DS to store the visited nodes (indicates the shapes already rendered on canvas)
    visitedNodeSet = set()
    placeInfoGraph.nodes["Origin"]["ori-coord"] = [0, 0, 0, 0]
    # Act as a queue for the BFS traversal
    shapesToBeProcessed = ["Origin"]
    # import pdb; pdb.set_trace()
    while len(shapesToBeProcessed):
        # pop the front shape in the queue, append all the out nodes to the queue, render the shape in the canvas
        front = shapesToBeProcessed.pop(0)
        startX, startY, endX, endY = placeInfoGraph.nodes[front]["ori-coord"]
        for outNode in placeInfoGraph.successors(front):
            if outNode in visitedNodeSet:
                continue
            visitedNodeSet.add(outNode)
            shapesToBeProcessed.append(outNode)
            offsetStartX, offsetStartY, offsetEndX, offsetEndY = placeInfoGraph.get_edge_data(front, outNode)["offset"]
            # offset subtracted on the y-coordinate since the upper left is considered as the origin in tkinter
            outNodeStartCoordX = startX + offsetStartX
            outNodeStartCoordY = startY + offsetStartY
            outNodeEndCoordX = outNodeStartCoordX + offsetEndX
            outNodeEndCoordY = outNodeStartCoordY + offsetEndY
            outNodeDim = [outNodeStartCoordX, outNodeStartCoordY, outNodeEndCoordX, outNodeEndCoordY]
            placeInfoGraph.nodes[outNode]["ori-coord"] = [outNodeStartCoordX, outNodeStartCoordY, outNodeEndCoordX,
                                                          outNodeEndCoordY]
            renderToCanvas(outNodeDim, outNode)
    renderCoins()


## Function to update the graph with shape as nodes and ref between shapes as arcs, properties of the shapes (
# offset) as edge attribute
#
#   @param placeStmt : Reference to the string which has placement command
#
def addShapeDependency(placeStmt):
    shape, refShape, startX, startY, endX, endY = placeStmt.split()

    # # Add shape and ref_shape if not present in the graph, define the arc between ref_shape and shape,
    # add the offset as an attribute
    if shape not in placeInfoGraph:
        placeInfoGraph.add_node(shape)
    if refShape not in placeInfoGraph:
        placeInfoGraph.add_node(refShape)
    if placeInfoGraph.has_edge(refShape, shape):
        print("WARNING: Duplicated placement sequence found: >" + placeStmt + "+<.Please debug !")
        return
    placeInfoGraph.add_edge(refShape, shape, offset=[int(startX), int(startY), int(endX), int(endY)])


## Function which will be executed after the 'Evaluate' button click, clears the data (graph) and start rendering the
# canvas by calling the required apis to figure out the new coordinates
#
def placeSequence():
    # clear the graph data
    placeInfoGraph.clear()
    # get the text editor data
    editorText = widgetInfoDict["text"].get(1.0, END)
    # clear the canvas
    widgetInfoDict["canvas"].delete("all")
    # Re-render the board
    renderBoard(BOARD_SIZE)

    # split the place cmds (editor data) and calculate the absolute coordinate based on offset
    editorTextLst = editorText.split("\n")
    n = len(editorTextLst)

    global threads
    global masterThread
    if(len(threads) != 0):
        masterThread.join()
    threads = []
    parts = []
    for i in range(THREADS):
        k, m = divmod(len(editorTextLst), THREADS)
        parts = list(editorTextLst[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(THREADS))
    for i in range(THREADS):
        threads.append(threading.Thread(target=placeMulti, args=[parts[i]]))
        threads[i].start()
    masterThread = threading.Thread(target=masterFunc, args=[threads])
    masterThread.start()

#this function will be run on a seperate thread when the placeSequence is called
#
def placeMulti(objectList):
    for line in objectList:
        if line.strip() == "" or "#" in line:
            continue
        #placeInfoGraphLock.acquire() 
        addShapeDependency(line)
       # placeInfoGraphLock.release() 
    #move to master thread

#this function will wait for all rendering threads to complete and will then render the result
def masterFunc(threads):
    print("INFO::Waiting for threads to finish rendering")
    for thread in threads:
        thread.join()
    print("INFO::All threads joined")

    placeInfoGraphLock.acquire(timeout=5) 
    calculateShapeDependency()
    placeInfoGraphLock.release() 




if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Please pass the <Board coin info file path>, <snake and ladder info file path> and <board size> as "
            "arguments in the command line")
        sys.exit()

    BOARD_SIZE = int(sys.argv[3])
    coinsPresenceInfo = [0] * (BOARD_SIZE ** 2)
    readCoinInfoFromFile(sys.argv[1])
    data = fillEditor(sys.argv[2])
    createEditor(data)
