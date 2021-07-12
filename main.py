from random import random
from random import randrange
import math
from bresenham import bresenham
import pyxel
from webbrowser import open as openw
from urllib.parse import quote_plus
SCENE_TITLE = 0
SCENE_TITLE_TO_GAME = 1
SCENE_GAME = 2
SCENE_GAME_TO_GAMEOVER = 3
BACK_DOT_COUNT = 300
enemys_list = []
bullets_list = []
bloods_list=  []
drops_list = []
class Background:
    def __init__(self,parent):
        self.parent = parent
        self.dot_list = []
        self.bg_color = 9
        self.dot_color = 4
        for i in range(BACK_DOT_COUNT):
            self.dot_list.append(
                (random() * pyxel.width, random() * pyxel.height,1)
            )

    def draw(self):
        pyxel.cls(self.bg_color)
        for (x, y, speed) in self.dot_list:
            pyxel.pset(x, (y+self.parent.scroll_y)% pyxel.height, self.dot_color)
        for i in range(32):
            l = self.parent.scroll_y % 128 * 2 * (((64-i)/64))+i*1.5
            c = [i,64+i,1,64-i]
            cc = l
            while cc>0:
                cc -= 128-i*2
            while cc-i*2 <= pyxel.height:

                pyxel.blt(c[0],cc,0,c[0],c[1],c[2],c[3],8)
                pyxel.blt(c[0],cc+64-i,0,c[0],c[1],c[2],c[3]*-1,8)
                pyxel.blt(pyxel.width-c[0],cc,0,c[0],c[1],c[2],c[3],8)
                pyxel.blt(pyxel.width-c[0], cc+64-i, 0,
                          c[0], c[1], c[2], c[3]*-1, 8)
                cc+=128-i*2-2



class Drop:
    def __init__(self,p):
        self.p = p
        self.parent = p.parent
        self.alive = True
        self.posx = p.posx
        self.posy = p.posy
    def update(self):
        if self.posy > pyxel.height+self.parent.scroll_y+11:
            self.alive = False
        elif self.posx-10 < self.parent.player.posx < self.posx+10 and self.posy-10 < self.parent.player.posy < self.posy+10:
            self.alive = False
            pyxel.play(3,6)
            self.parent.kushis += 1
            self.parent.kushis = min(99,self.parent.kushis)
    def draw(self):
        pyxel.blt(self.posx-5,self.posy+self.parent.scroll_y-5,0,0,128,10,10,6)
class Blood:
    def __init__(self,p):
        self.p = p
        self.parent = p.parent
        self.alive = True
        self.posx = p.posx+randrange(-5, 5)
        self.posy = p.posy+randrange(-5, 5)
    def update(self):
        if self.posy > pyxel.height+self.parent.scroll_y+11:
            self.alive = False
    def draw(self):
        pyxel.pset(self.posx,self.posy+self.parent.scroll_y,8)
class Enemy:
    def __init__(self,parent):
        self.parent = parent
        self.anime_count = 0
        self.posx = random()*(pyxel.width-64-10)+32+5
        self.posy = -self.parent.scroll_y+0
        self.alive = True
    def update(self):
        self.anime_count += 1
        self.anime_count %= 12
        self.posy += 1
        if self.posy > pyxel.height+self.parent.scroll_y+11:
            self.alive = False
        elif self.posx-10 < self.parent.player.posx < self.posx+10 and self.posy-2 < self.parent.player.posy < self.posy+8:
            pyxel.play(1, 5)
            self.parent.gameover()
    def draw(self):
        tilex = 0
        if self.anime_count in [0,1,2,3,7,8]:
            tilex = 0
        elif self.anime_count in [4,6,9,11]:
            tilex = 16
        else:
            tilex = 32
        pyxel.blt(self.posx-5,self.posy-11+self.parent.scroll_y,0,tilex,0,16,11,14)
    def killed(self):
        self.parent.killcount += 1
        if random()>0.7:
            drops_list.append(Drop(self))
        self.alive = False
        for i in range(20):
            bloods_list.append(Blood(self))


class Bullet:
    def __init__(self,parent):
        self.parent = parent
        self.alive = True
        self.posx = self.parent.player.posx
        self.posy = self.parent.player.posy+self.parent.scroll_y-8
        xx = pyxel.mouse_x-self.posx
        yy = pyxel.mouse_y-self.posy
        self.at = math.atan2(yy, xx)
    def update(self):
        poses = []
        for i in range(1,8):
            poses.append((math.cos(self.at)*i+self.posx,math.sin(self.at)*i+self.posy))
        for a in enemys_list:
            for b in poses:
                if a.posx-5 < b[0] < a.posx+5 and a.posy-11 < b[1]-self.parent.scroll_y < a.posy:
                    pyxel.play(1,5)
                    a.killed()
                    break
            else:
                continue
            break
        self.posx = poses[6][0]
        self.posy = poses[6][1]

        if not (0 < poses[-1][1] < pyxel.height):
            self.alive = False
        elif not (32 < poses[-1][0] < pyxel.width-32):
            self.alive = False
            pyxel.play(2,4)
    def draw(self):
        pyxel.line(self.posx, self.posy,
                   self.posx+math.cos(self.at)*5, self.posy+math.sin(self.at)*5,0)

class Player:
    def __init__(self,parent):
        self.parent = parent
        self.posy = self.parent.scroll_y+pyxel.height-32
        self.posx = pyxel.width/2
        self.bloodflag = 0
    def update(self):
        self.posy -= self.parent.dif
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.posx += 2*pyxel.width/100
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.posx -= 2*pyxel.width/100
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
            self.posy -= 2*pyxel.height/100
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
            self.posy += 2*pyxel.height/100
        if self.posy > pyxel.height-self.parent.scroll_y:
            self.posy = pyxel.height-self.parent.scroll_y
        if self.posy< 0-self.parent.scroll_y+16:
            self.posy = 0-self.parent.scroll_y+16
        if self.posx > pyxel.width-32-5:
            self.posx = pyxel.width-32-5
        if self.posx < 32+5:
            self.posx = 32+5
        for i in bloods_list:
            if math.floor(i.posx) == math.floor(self.posx):
                if math.floor(i.posy) == math.floor(self.posy):
                    if i.p != self:
                        self.bloodflag = 10
        if pyxel.frame_count%5==0 and self.bloodflag > 0:
            self.bloodflag-=1
            bloods_list.append(Blood(self))
            bloods_list[-1].posx = self.posx
            bloods_list[-1].posy = self.posy
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            if self.parent.kushis > 0:
                pyxel.play(0, 0)
                self.parent.kushis -= 1
                bullets_list.append(Bullet(self.parent))
        if pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):
            if self.parent.clickcount > 30:
                pyxel.play(0, 0)
                for i in range(min(5, self.parent.kushis)):
                    self.parent.kushis -= 1
                    bullets_list.append(Bullet(self.parent))
                    bullets_list[-1].at = math.radians(math.degrees(bullets_list[-1].at)+(i-2)*20)




    def draw(self):
        pyxel.blt(self.posx-5,self.posy-11+self.parent.scroll_y,0,0,48,16,11,14)


class App:
    def __init__(self):
        pyxel.init(184, 192)
        self.killcount = 0
        self.scroll_y = 0
        self.scene = SCENE_TITLE
        self.background = Background(self)
        self.counts = {}
        self.dif = 1
        self.kushis = 99
        self.clickcount = 0
        pyxel.load("assets/main.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.scene == SCENE_TITLE:
            self.scroll_y += 1
            if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON):
                pyxel.play(0,3)
                self.scene = SCENE_TITLE_TO_GAME
                self.counts["ttg_count_1"] = 0
                self.counts["ttg_count_2"] = 0
                self.counts["ttg_count_3"] = 0
                self.counts["ttg_count_4"] = 0
                self.start_count = pyxel.frame_count+0
        elif self.scene == SCENE_TITLE_TO_GAME:
            self.scroll_y += 1
            if self.counts["ttg_count_1"]**1.8 > 16:
                self.counts["ttg_count_2"] += 1
            if self.counts["ttg_count_1"]**1.8 > 32:
                self.counts["ttg_count_3"] += 1
            if self.counts["ttg_count_1"]**1.8 > 48:
                self.counts["ttg_count_4"] += 1
                if pyxel.height <= self.counts["ttg_count_4"]**2-7-32:
                    self.scene = SCENE_GAME
                    self.killcount = 0
                    self.dif = 1
                    self.player = Player(self)
            self.counts["ttg_count_1"] += 1
        elif self.scene == SCENE_GAME:
            if pyxel.btn(pyxel.MOUSE_LEFT_BUTTON):
                self.clickcount += 1
            if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                self.clickcount = 0
            
            self.scroll_y += self.dif
            if pyxel.frame_count%(math.floor(20/self.dif)) == 0:
                enemys_list.append(Enemy(self))
            for i in enemys_list:
                if i.alive:
                    i.update()
                else:
                    enemys_list.remove(i)
            for i in bullets_list:
                if i.alive:
                    i.update()
                else:
                    bullets_list.remove(i)
            for i in bloods_list:
                if i.alive:
                    i.update()
                else:
                    bloods_list.remove(i)
            for i in drops_list:
                if i.alive:
                    i.update()
                else:
                    drops_list.remove(i)
            self.dif += 0.001
            self.player.update()
    
    def draw(self):
        self.background.draw()
        if self.scene == SCENE_TITLE:
            pyxel.blt(pyxel.width/2-32,pyxel.height/2-8-32,0,0,32,64,16,7)
            pyxel.blt(pyxel.width/2-32+8,pyxel.height/2-8-32,0,0,16,16,16,0)
            pyxel.blt(pyxel.width/2-32+8+16,pyxel.height/2-8-32,0,16,16,16,16,0)
            pyxel.blt(pyxel.width/2-32+8+32,pyxel.height/2-8-32,0,32,16,16,16,0)
            pyxel.text(pyxel.width/2-len("- CLICK START -")*2, pyxel.height/2-2,"- CLICK START -",7)
        elif self.scene == SCENE_TITLE_TO_GAME:
            pyxel.blt(self.counts["ttg_count_1"]**1.8+pyxel.width/2-32,pyxel.height/2-8-32,0,0,32,64,16,7)
            pyxel.blt(pyxel.width/2-32+8,self.counts["ttg_count_2"]**2+pyxel.height/2-8-32,0,0,16,16,16,0)
            pyxel.blt(pyxel.width/2-32+8+16,self.counts["ttg_count_3"]**2+pyxel.height/2-8-32,0,16,16,16,16,0)
            pyxel.blt(pyxel.width/2-32+8+32,self.counts["ttg_count_4"]**2+pyxel.height/2-8-32,0,32,16,16,16,0)
        elif self.scene == SCENE_GAME:
            for i in list(bresenham(pyxel.mouse_x, pyxel.mouse_y, math.floor(self.player.posx), math.floor(self.player.posy+self.scroll_y-11)))[::3]:
                pyxel.pset(i[0], i[1], 7)
            self.player.draw()
            crosser = []
            for i in range(5):
                crosser.append((pyxel.mouse_x+2-i, pyxel.mouse_y+0))
            for i in range(5):
                crosser.append((pyxel.mouse_x+0, pyxel.mouse_y+2-i))
            for i in range(16):
                pyxel.pal(i,(i+7)%16)
            for i in crosser:
                pyxel.pset(i[0],i[1],pyxel.pget(i[0],i[1]))
            pyxel.pal()
            pyxel.text(5, 5, str(self.kushis), 7)
            for i in bloods_list:
                i.draw()
            for i in enemys_list:
                i.draw()
            for i in drops_list:
                i.draw()
            for i in bullets_list:
                i.draw()
        elif self.scene == SCENE_GAME_TO_GAMEOVER:
            pyxel.rect(16, 0, 123, self.counts["gtg_count"]*4, 7)
            pyxel.rect(16, 0, 20, self.counts["gtg_count"]*4, 4)
            pyxel.rect(139, 0, 20, self.counts["gtg_count"]*4, 4)
            pyxel.line(16, 0, 16, self.counts["gtg_count"]*4, 0)
            pyxel.line(159, 0, 159, self.counts["gtg_count"]*4, 0)
            if self.counts["gtg_count"] < pyxel.height/4:
                pyxel.blt(0,self.counts["gtg_count"]*4-32,1,0,0,186,32,12)
            else:
                pyxel.blt(0,pyxel.height-32,1,0,0,186,32,12)
                if self.counts["gtg_count"] > pyxel.height/4+20:
                    pyxel.text(37,33,"SCORE ".upper()+str(self.stop_count - self.start_count),0)
                    if self.counts["gtg_count"] > pyxel.height/4+40:
                        pyxel.text(37,40,"KILL  ".upper()+str(self.killcount),0)
                    if self.counts["gtg_count"] > pyxel.height/4+60:
                        if 37 <= pyxel.mouse_x <= 37+64 and 47 <= pyxel.mouse_y <= 47+64:
                            pyxel.pal(12, 8)
                            pyxel.pal(7,12)
                            if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                                openw(
                                    "https://twitter.com/intent/tweet?text=" + quote_plus("SCORE:".upper()+str(self.stop_count - self.start_count)+"\nKILL:".upper()+str(self.killcount)+"\n#Bakumatu_Harisenbon\nhttps://github.com/AlageZ/Harisenbon/releases/"))
                        pyxel.blt(37,47,0,32,64,64,64,0)
                        pyxel.pal()
                        pyxel.mouse(True)
            self.counts["gtg_count"] += 1
    def gameover(self):
        self.stop_count = pyxel.frame_count+0
        self.counts["gtg_count"] = 0
        self.scene = SCENE_GAME_TO_GAMEOVER
app = App()
