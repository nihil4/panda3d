# Last updated: 8/9/2013

import direct.directbase.DirectStart
from panda3d.core import WindowProperties
from panda3d.core import Filename,AmbientLight,DirectionalLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from pandac.PandaModules import CardMaker
from panda3d.core import Point3, Vec3,Vec4,BitMask32
from panda3d.core import LightRampAttrib
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.task.Task import Task
from direct.showbase.DirectObject import DirectObject
import random, sys, os, math

def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale=.04)
                        
class World(DirectObject):
    
    def __init__(self):
        
        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0}
        self.angles = {"left":-90, "right":90, "forward":0, "backward":180}
        self.title = addTitle("Moving like nowaday's action game")
        
        # load the scene
        base.setBackgroundColor(0,0,0.2,1)
        floorTex = loader.loadTexture("maps/envir-ground.jpg")
        cm = CardMaker("")
        cm.setFrame(-2,2,-2,2)
        floor = render.attachNewNode(PandaNode("floor"))
        for y in range(12):
            for x in range(12):
                nn = floor.attachNewNode(cm.generate())
                nn.setP(-90)
                nn.setPos((x-6)*4, (y-6)*4, 0)
        floor.setTexture(floorTex)
        floor.flattenStrong()
        
        # create main character        
        self.eve = Actor("models/eve", 
                           {"run":"models/eve_run",
                            "walk":"models/eve_walk"})
        self.eve.reparentTo(render)
        self.eve.setScale(.4)
        self.eve.setPos(0, 0, 0)
        
        # accept the control keys for movement and rotation        
        self.accept("escape", sys.exit)
        self.accept("a", self.setKey, ["left",1])
        self.accept("d", self.setKey, ["right",1])
        self.accept("w", self.setKey, ["forward",1])
        self.accept("s", self.setKey, ["backward",1])
        self.accept("a-up", self.setKey, ["left",0])
        self.accept("d-up", self.setKey, ["right",0])
        self.accept("w-up", self.setKey, ["forward",0])
        self.accept("s-up", self.setKey, ["backward",0])
        
        self.pre_move = "forward"
        taskMgr.add(self.move, "moveTask")
        
        # game start variable
        self.isMoving = False
        
        # set up the camera        
        base.camera.reparentTo(self.eve)
        #look over eve
        self.cameraTargetHeight = 6.0
        self.cameraDistance = 30
        self.cameraPitch = 10
        # disable the default camera control by mouse
        base.disableMouse()
        # hide mouse
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        
        # create some lighting
        render.setShaderAuto()
        render.setAttrib(LightRampAttrib.makeHdr1())
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.4, .4, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(0, 8, -2.5))
        directionalLight.setColor(Vec4(2.0, 2.0, 2.0, 1))
        directionalLight.setSpecularColor(Vec4(2.0, 2.0, 2.0, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))

    # record the state of the move keys
    def setKey(self, key, value):
        self.keyMap[key] = value
        
    # accepts move keys to move the character
    def move(self, task):               
        # Use mouse input to turn both the character and camera       
        if base.mouseWatcherNode.hasMouse():
            # get change in mouse position
            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            deltaX = md.getX() - 200
            deltaY = md.getY() - 200
            # reset cursor position
            base.win.movePointer(0, 200, 200)
            
            self.eve.setH(self.eve.getH() - 0.3 * deltaX)
                
            self.cameraPitch = self.cameraPitch + 0.1 * deltaY
            for key in self.keyMap.keys():
                if (self.keyMap[key] != 0):
                    if not self.pre_move is key: 
                        self.eve.setH(self.eve.getH() + (self.angles[self.pre_move] - self.angles[key]))
                        self.pre_move = key
                    self.eve.setY(self.eve, -25 * globalClock.getDt())
                    base.camera.setHpr(self.eve, self.angles[key], self.cameraPitch, 0)
                    break
            else:
                base.camera.setHpr(self.angles[self.pre_move], self.cameraPitch, 0)
            base.camera.setPos(0, 0, self.cameraTargetHeight/2)
            base.camera.setY(base.camera, self.cameraDistance)
            
        # point the camera at the view target
        viewTarget = Point3(0, 0, self.cameraTargetHeight)
        base.camera.lookAt(viewTarget)
        
        # if eve is moving, loop the run animation   
        if (self.keyMap.values().count(1) != 0):
            if self.isMoving is False:
                self.eve.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.eve.stop()
                self.eve.pose("walk", 5)
                self.isMoving = False
        
        return task.cont
        
w = World()
run()