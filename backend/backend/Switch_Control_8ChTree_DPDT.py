""" 
Python GUI to control the Switches using the Numato Relays
Author: Alex Walter
Modified: Jason Allmaras
************** MODIFICATIONS IN PROGRESS ************************
Updated form old code by Simone Frasca
"""

import sys
import numpy as np
from functools import partial
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *

#sys.path.append('/Users/srpatel/Downloads/')
from numatoRelay import Relay


class switchTreeGUI(QtWidgets.QMainWindow):

    def __init__(self, port, relayDPDTPolarity, relayDPDTMapping, treeChannelMapping, initialState, title=''):
        super(switchTreeGUI, self).__init__()
        self.relayDPDTPolarity = relayDPDTPolarity
        self.relayDPDTMapping = relayDPDTMapping
        self.treeChannelMapping = treeChannelMapping
        self.switch = Relay(port)
        self.currentState = initialState
        self.currentOutputState = 0
        self.currentPolarityState = 0

        self.create_main_frame()
        self.setWindowTitle(title)


    def isAmpOff(self):
        s = "WARNING: Before (de)activating switches you should unpower any attached cryoamps. You can check the power supply by navigating to http://10.7.0.160. Use the password 'Keysight'\n\nAre the Cryoamps OFF?"
        ret = QtWidgets.QMessageBox.question(self, 'WARNING: Cryoamp', s, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)

        if ret == QtWidgets.QMessageBox.Yes:
            return True
        return False
    
    def activateChannel(self, relayCh):
        if self.isAmpOff():
            self.switch.send_pulse(relayCh, 15)
            print("Sent pulse to relay "+str(relayCh))

    def resetSwitch(self, switchNum, relayCh):
        if self.isAmpOff():
            self.switch.send_pulse(relayCh, 15)
            print("Sent pulse to relay "+str(relayCh))
            for b in self.buttons[switchNum]:
                b.setPalette(self.redButtonPalette)

    def activateChannelNoSafetyCheck(self, relayCh):
        self.switch.send_pulse(relayCh, 15)
        print("Sent pulse to relay "+str(relayCh))

    def setPulsePolarity(self, polarity, safetyCheck):
        if safetyCheck:
            if self.isAmpOff():
                if polarity == 0:
                    self.switch.turn_on(self.relayDPDTPolarity[0][0])
                    print("Set relay " + str(self.relayDPDTPolarity[0][0]) + " to low.")
                    self.polarityButton.setPalette(self.greenButtonPalette)
                    self.polarityButton2.setPalette(self.redButtonPalette)
                    self.currentPolarityState = 0
                else:
                    self.switch.turn_off(self.relayDPDTPolarity[0][0])
                    print("Set relay "+str(self.relayDPDTPolarity[0][0])+" to high.")
                    self.polarityButton.setPalette(self.redButtonPalette)
                    self.polarityButton2.setPalette(self.greenButtonPalette)
                    self.currentPolarityState = 1
        else:
            if polarity == 0:
                self.switch.turn_on(self.relayDPDTPolarity[0][0])
                print("Set relay " + str(self.relayDPDTPolarity[0][0]) + " to low.")
                self.currentPolarityState = 0
            else:
                self.switch.turn_off(self.relayDPDTPolarity[0][0])
                print("Set relay " + str(self.relayDPDTPolarity[0][0]) + " to high.")
                self.currentPolarityState = 1

    def resetTree(self, relayChannels):
        if self.isAmpOff():
            # Set the polarity to negative
            self.setPulsePolarity(0, 0)
            self.polarityButton.setPalette(self.greenButtonPalette)
            self.polarityButton2.setPalette(self.redButtonPalette)
            for relayCh in relayChannels:
                self.switch.send_pulse(relayCh[1], 15)
                currentSwitchChannelInd = relayCh[0]-1
                self.currentState[currentSwitchChannelInd] = 0  # set the state of the switch
                self.switchButtons[currentSwitchChannelInd].setPalette(self.greenButtonPalette)
                self.switchButtons2[currentSwitchChannelInd].setPalette(self.redButtonPalette)
                print("Sent pulse to relay " + str(relayCh[1]) + " for switch " + str(relayCh[0]))
            # Need to reset the color of the output channel based on the new state
            self.updateGuiOutputChannel()


    def updateGuiOutputChannel(self):
        for outputChannel in range(self.numberOutputChannels):
            targetState = self.treeChannelMapping[outputChannel]
            branch1 = targetState[1]
            tier1Switch = branch1[0]
            if self.currentState[tier1Switch - 1] == branch1[1]:
                branch2 = targetState[2]
                tier2Switch = branch2[0]
                if self.currentState[tier2Switch - 1] == branch2[1]:
                    branch3 = targetState[3]
                    tier3Switch = branch3[0]
                    if self.currentState[tier3Switch - 1] == branch3[1]:
                        branch4 = targetState[4]
                        tier4Switch = branch4[0]
                        if self.currentState[tier4Switch - 1] == branch4[1]:
                            self.currentOutputState = outputChannel
                            self.outputChannelButtons[outputChannel].setPalette(self.blueButtonPalette)
                        else:
                            self.outputChannelButtons[outputChannel].setPalette(self.redButtonPalette)
                    else:
                        self.outputChannelButtons[outputChannel].setPalette(self.redButtonPalette)
                else:
                    self.outputChannelButtons[outputChannel].setPalette(self.redButtonPalette)
            else:
                self.outputChannelButtons[outputChannel].setPalette(self.redButtonPalette)
    
    def activateOutputChannel(self, outputChannelNum):
        if self.isAmpOff():
            # print("called activate output channel")
            # Based on outputChannelNum(zero indexed), should be updated, but this works for now
            # determine the switches that need to be configured
            for treeLevel in range(self.numberTreeColumns):
                desiredState = treeChannelMapping[outputChannelNum][treeLevel+1]
                #print("Desired State" + str(desiredState))
                #print(self.currentState)
                for switchNum in range(self.numberSwitches):  #  temporary
                    if desiredState[0] == (switchNum+1):  # temporary
                        if desiredState[1] == self.currentState[switchNum]:
                            print("CH "+str(switchNum+1)+" in correct state")
                        else:
                            print("CH " + str(switchNum+1) + " in wrong state")
                            self.activateSwitch((switchNum), desiredState[1])
            # Determine the switches that actually need to be switched
            self.updateGuiOutputChannel()

    def activateSwitch(self, switchCh, polarity, safetyCheck=0):
        proceedWithSwitch = 1
        if safetyCheck:
            proceedWithSwitch = 0
            if self.isAmpOff():
                proceedWithSwitch = 1

        if proceedWithSwitch:
            # Check switch state
            print(switchCh)
            print(self.relayDPDTMapping)
            for k in range(self.numberSwitches):
                print(str(self.relayDPDTMapping[k][1]))
                print(str(switchCh))
                if self.relayDPDTMapping[k][0] == switchCh+1:
                    print(str(self.relayDPDTMapping[k][1]))
                    relayCh = self.relayDPDTMapping[k][1]
            print(relayCh)
            if self.currentState[switchCh] == polarity:
                print("Already in correct state")
            else:
                if self.currentPolarityState == polarity:
                    self.activateChannelNoSafetyCheck(relayCh)
                    self.currentState[switchCh] = polarity
                    if polarity == 0:
                        self.switchButtons[switchCh].setPalette(self.greenButtonPalette)
                        self.switchButtons2[switchCh].setPalette(self.redButtonPalette)
                    else:
                        self.switchButtons2[switchCh].setPalette(self.greenButtonPalette)
                        self.switchButtons[switchCh].setPalette(self.redButtonPalette)
                else:
                    self.setPulsePolarity(polarity, 0)
                    self.activateChannelNoSafetyCheck(relayCh)
                    self.currentState[switchCh] = polarity
                    if polarity == 0:
                        self.switchButtons[switchCh].setPalette(self.greenButtonPalette)
                        self.switchButtons2[switchCh].setPalette(self.redButtonPalette)
                    else:
                        self.switchButtons2[switchCh].setPalette(self.greenButtonPalette)
                        self.switchButtons[switchCh].setPalette(self.redButtonPalette)
                print(self.currentState)
                self.updateGuiOutputChannel()

    def create_main_frame(self):
        self.main_frame = QtWidgets.QWidget()

        #button colors
        self.greenButtonPalette = QtGui.QPalette()
        self.greenButtonPalette.setColor(QtGui.QPalette.Button, QtCore.Qt.green)
        self.redButtonPalette = QtGui.QPalette()
        self.redButtonPalette.setColor(QtGui.QPalette.Button, QtCore.Qt.darkRed)
        self.blueButtonPalette = QtGui.QPalette()
        self.blueButtonPalette.setColor(QtGui.QPalette.Button, QtCore.Qt.blue)

        self.numberTreeColumns = len(treeChannelMapping[0]) - 1
        self.numberOutputChannels = len(treeChannelMapping)
        # self.currentState = {}
        # for switchNum in range(15):
        #     self.currentState[switchNum] = 0

        buttonBoxes = {}        # save the button layouts in here so we can order them later
        self.buttons = {}       # save only the activate buttons here so that we can change their color when we reset

        self.buttonStates = {}

        self.numberSwitches = 15

        col1 = 0
        col2 = 2
        col3 = 4
        col4 = 6
        self.colCh = 8
        self.GUIChannelMapping = [[0, col4],
                                  [2, col4],
                                  [4, col4],
                                  [6, col4],
                                  [8, col4],
                                  [10, col4],
                                  [1, col3],
                                  [14, col4],
                                  [12, col4],
                                  [13, col3],
                                  [5, col3],
                                  [9, col3],
                                  [7, col1],
                                  [3, col2],
                                  [11, col2]]

        self.grid = QGridLayout()

        self.switchButtons = []
        self.switchButtons2 = []
        for arr in range(self.numberSwitches):
            switchCh = arr
            button = QtWidgets.QPushButton("Neg")
            button.setPalette(self.redButtonPalette)
            button.setBackgroundRole(QtGui.QPalette.Button)
            button.setEnabled(True)
            button.setMaximumWidth(80)
            button.clicked.connect(partial(self.activateSwitch, switchCh, 0, safetyCheck=1))
            self.grid.addWidget(button, self.GUIChannelMapping[arr][0], self.GUIChannelMapping[arr][1])
            self.switchButtons.append(button)

            button2 = QtWidgets.QPushButton("Pos")
            button2.setPalette(self.redButtonPalette)
            button2.setBackgroundRole(QtGui.QPalette.Button)
            button2.setEnabled(True)
            button2.setMaximumWidth(80)
            button2.clicked.connect(partial(self.activateSwitch, switchCh, 1, safetyCheck=1))
            self.grid.addWidget(button2, (self.GUIChannelMapping[arr][0]+1), (self.GUIChannelMapping[arr][1]))
            self.switchButtons2.append(button2)

        self.outputChannelButtons = []
        for arr in range(self.numberOutputChannels):
            outputChannel = arr
            button = QtWidgets.QPushButton("CH: "+str(outputChannel + 1))
            button.setPalette(self.redButtonPalette)
            button.setBackgroundRole(QtGui.QPalette.Button)
            button.setEnabled(True)
            button.setMaximumWidth(80)
            button.clicked.connect(partial(self.activateOutputChannel, outputChannel))
            self.grid.addWidget(button, outputChannel, self.colCh)
            self.outputChannelButtons.append(button)

        resetButton = QtWidgets.QPushButton("Reset All")
        resetButton.setPalette(self.redButtonPalette)
        resetButton.setBackgroundRole(QtGui.QPalette.Button)
        resetButton.setEnabled(True)
        resetButton.setMaximumWidth(80)
        resetButton.clicked.connect(partial(self.resetTree, self.relayDPDTMapping))
        self.grid.addWidget(resetButton, (self.numberOutputChannels-1), 0)
        self.resetButton = resetButton

        polarityButtonLabel = QtWidgets.QLabel("Set Polarity:")
        self.grid.addWidget(polarityButtonLabel, 0, 0)

        polarityButton = QtWidgets.QPushButton("Negative")
        polarityButton.setPalette(self.redButtonPalette)
        polarityButton.setBackgroundRole(QtGui.QPalette.Button)
        polarityButton.setEnabled(True)
        polarityButton.setMaximumWidth(80)
        polarityButton.setAccessibleName("TestButton")
        polarityButton.setObjectName("TestButton")
        polarityButton.clicked.connect(partial(self.setPulsePolarity, 0, 1))
        self.grid.addWidget(polarityButton, 1, 0)
        self.polarityButton = polarityButton

        polarityButton2 = QtWidgets.QPushButton("Positive")
        polarityButton2.setPalette(self.redButtonPalette)
        polarityButton2.setBackgroundRole(QtGui.QPalette.Button)
        polarityButton2.setEnabled(True)
        polarityButton2.setMaximumWidth(80)
        polarityButton2.clicked.connect(partial(self.setPulsePolarity, 1, 1))
        self.grid.addWidget(polarityButton2, 2, 0)
        self.polarityButton2 = polarityButton2

        # Arrange buttons on window
        # hbox_S = QtWidgets.QHBoxLayout(spacing=50)
        # switchNums = list(buttonBoxes.keys())
        # switchNums.sort()
        # for sn in switchNums:
        #     vbox = QtWidgets.QVBoxLayout(spacing=0)
        #     label=QtWidgets.QLabel("Switch "+str(sn))
        #     hbox_label=QtWidgets.QHBoxLayout()
        #     hbox_label.addStretch()
        #     hbox_label.addWidget(label)
        #     hbox_label.addStretch()
        #     vbox.addLayout(hbox_label)
        #     buttonBoxes[sn].sort(key=lambda x: x._order)
        #     if buttonBoxes[sn][0]._order==-1:
        #         buttonBoxes[sn] = buttonBoxes[sn][1:] +[buttonBoxes[sn][0]]
        #     for bb in buttonBoxes[sn]:
        #         vbox.addLayout(bb)
        #     vbox.addStretch()
        #     hbox_S.addLayout(vbox)

        self.main_frame.setLayout(self.grid)
        # self.main_frame.setLayout(hbox_S)
        self.setCentralWidget(self.main_frame)


    def closeEvent(self, even):
        self.switch.close()
        QtCore.QCoreApplication.instance().quit


def main(port, relay2Switch, relayDPDTMapping, treeChannelMapping, initialState, title="16 CHANNEL SWITCH TREE GUI"):
    #print(QtWidgets.QStyleFactory.keys())
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    app = QtWidgets.QApplication(sys.argv)
    form = switchTreeGUI(port, relay2Switch, relayDPDTMapping, treeChannelMapping, initialState, title)
    form.show()
    app.exec_()


if __name__=='__main__':
    port = '/dev/tty.usbmodem21301'

    # Switch 3 and 4 are both controlled with the same relay peripheral
    # Control this with a nest tuple. ie
    # [ (relayCH, (Switch#, SwitchCH)) ]
    # switchCH == -1 means reset

    relayDPDTPolarity = [(0, (0,-1))]
    relayDPDTChannels = list(zip([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], zip([1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4], [-1, -1, -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1])))
    relay2Switch4_reset = [(19, (4, 1))]

    relayDPDT = relayDPDTPolarity
    relayDPDT = np.append(relayDPDTPolarity, relayDPDTChannels, axis=0)
    # Mapping for ARC6 -3 Style Cables
    # treeChannelMapping = list(
    #     zip([ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16],
    #     zip([13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13],
    #         [ 0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,  1,  1,  1,  1]),
    #     zip([14, 14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 15, 15],
    #         [ 0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,  1,  1,  1,  1]),
    #     zip([ 7,  7,  7,  7, 11, 11, 11, 11, 12, 12, 12, 12, 10, 10, 10, 10],
    #         [ 0,  0,  1,  1,  0,  0,  1,  1,  0,  0,  1,  1,  0,  0,  1,  1]),
    #     zip([ 1,  1,  2,  2,  3,  3,  4,  4,  5,  5,  6,  6,  9,  9,  8,  8],
    #         [ 0,  1,  0,  1,  0,  1,  0,  1,  0,  1,  0,  1,  0,  1,  0,  1])
    #         ))

    relayDPDTMapping = list(zip([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]))

    # Mapping for ARC6 -3 Style Cables
    treeChannelMapping = (
        [1, (13, 0), (14, 0), (7, 0), (1, 0)],
        [2, (13, 0), (14, 0), (7, 0), (1, 1)],
        [3, (13, 0), (14, 0), (7, 1), (2, 0)],
        [4, (13, 0), (14, 0), (7, 1), (2, 1)],
        [5, (13, 0), (14, 1), (11, 0), (3, 0)],
        [6, (13, 0), (14, 1), (11, 0), (3, 1)],
        [7, (13, 0), (14, 1), (11, 1), (4, 0)],
        [8, (13, 0), (14, 1), (11, 1), (4, 1)],
        [9, (13, 1), (15, 0), (12, 0), (5, 0)],
        [10, (13, 1), (15, 0), (12, 0), (5, 1)],
        [11,  (13, 1), (15, 0), (12, 1), (6, 0)],
        [12,  (13, 1), (15, 0), (12, 1), (6, 1)],
        [13,  (13, 1), (15, 1), (10, 0), (9, 0)],
        [14,  (13, 1), (15, 1), (10, 0), (9, 1)],
        [15,  (13, 1), (15, 1), (10, 1), (8, 0)],
        [16,  (13, 1), (15, 1), (10, 1), (8, 1)],
    )


    initialState = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # print(relayDPDT)
    # print(treeChannelMapping)
    #
    # print(len(treeChannelMapping))
    # print((treeChannelMapping[1]))
    # print((treeChannelMapping[1][1]))
    # print((treeChannelMapping[1][1][0]))
    # print((treeChannelMapping[1][1][1]))
    # print(initialState)
    #
    # print(relayDPDTPolarity[0][0])
    # print(relayDPDTMapping)
    main(port, relayDPDTPolarity, relayDPDTMapping, treeChannelMapping, initialState)

