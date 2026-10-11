import time
import glfw
import OpenGL.GL as GL
import OpenGL.GLU as GLU
from PIL import Image
class SysEngine:  #Системная библеотека

    def __init__(self):# Создание переиенных
        self.objects = {}
        self.id = {}
        self.globalDat = {0: 0.016}
        self.timer = {}
        self.pbut = {}
        self.rendDat = {"sprites_id": {}}
        self.frame_time = None
        self.cache = {"collide":None}

    def print_DB(self): # вывод базы данных
        print(self.objects, self.id, self.globalDat, self.timer, self.frame_time)
        return self.objects, self.id, self.globalDat, self.timer, self.frame_time

    def start_timer(self):  # начать таймер
        self.timer[0] = time.perf_counter()

    def stop_timer(self):  # остановить таймер
        end = time.perf_counter()

        eltime = end - self.timer[0]

        return eltime

    def start_frame(self):  # начало кадра
        self.timer[1] = time.perf_counter()

    def end_frame(self):  #конец кадра
        end = time.perf_counter()

        eltime = end - self.timer[1]

        if eltime <= 0:
            eltime = 0.0001

        self.globalDat[0] = eltime 

    def adToDB(self,DBName,args):
        DBName = getattr(DB,DBName)
        for id, argso in args.items():
            DBName[id] = argso

    def window_closed(self):
        closed = glfw.window_should_close(DB.rendDat["window"])
        if closed:
            glfw.terminate()
            print(1)
        return closed
DB = SysEngine()  #Делаем переменные глобальными

class file_lib:  # Библеотека для работы с переменными

    def __init__(self):
        pass

    def map(self, name, size):  #Создание карты (локации)
        map = {
            "type": "map",
            "name":name, 
            "sizeX":size[0], 
            "sizeY":size[1]
            }
        free_id = next(i for i in range(len(DB.objects) + 1) if i not in DB.objects)
        DB.objects[free_id] = map
        return map 

    def object(
        self, name, size, interactable=0, resistance=1, sprite=None
    ):  # Создание объекта
        if sprite != None:
            grafic.load_sprite(way=sprite,name=name)
            sprite_name = name
        else:
            sprite_name = None
        obj = {
            "type": "object",
            "name": name,
            "sizeX": size[0],
            "sizeY": size[1],
            "interact": interactable,
            "sprite": sprite_name,
            "resistance": resistance,
        }
        free_id = next(i for i in range(len(DB.objects) + 1) if i not in DB.objects)
        DB.objects[free_id] = obj
        return obj

    def trigger(self, name, size, function, args):  # Создание триггера
        trigger = {
            "type": "trigger",
            "name":name,
            "sizeX":size[0],
            "sizeY":size[1],
            "function":function,
            "args":args
            }
        free_id = next(i for i in range(len(DB.objects) + 1) if i not in DB.objects)
        DB.objects[free_id] = trigger
        return trigger

    def searchName(self, name):  #Поиск объекта по имени
        for count in DB.objects:
            if DB.objects[count]["name"] == name:
                return count
        return None

    def delete(self, obj):  # Удаление объекта из общей переменной
        obj_id = next(i for i, v in DB.objects.items() if v == obj)
        del DB.objects[obj_id]

    def read(self, objname):  # Вывод данных из объекта (отладка)

        obj = DB.objects[self.searchName(objname)]

        if obj["type"] == "map":
            print(
                f"type = {obj["type"]}\n name = {obj["name"]}\n size X = {obj["sizeX"]}\n size Y = {obj["sizeY"]}"
            )
        elif obj["type"] == "object":
            print( 
                f"type = {obj["type"]}\n name = {obj["name"]}\n size X = {obj["sizeX"]}\n size Y = {obj["sizeY"]}\n scale = {obj["scale"]}\n interactable = {obj["interact"]}\n resistance = {obj["resistance"]}\n way to sprite = {obj["sprite"]}"
            )
        elif obj["type"] == "trigger":
            print(
                f"type = {obj["type"]}\n name = {obj["name"]}\n size X = {obj["sizeX"]}\n size Y = {obj["sizeY"]}\n activateble function = {obj["function"]}"
            )

    def nearObj(self, id, R):  # Поиск близжайших объектов по  id
        obj = DB.id[id]
        objDat = DB.objects[self.searchName(obj[2])]

        nearObj = {}

        for oid, odat in DB.id.items():
            if oid == id:
                continue
            objdat = DB.objects[self.searchName(odat[2])]

            diX = max(0, max(obj[3][0], odat[3][0]) - min(obj[3][0] + objDat["sizeX"] * obj[7], odat[3][0] + objdat["sizeX"] * odat[7]))
            diY = max(0, max(obj[3][1], odat[3][1]) - min(obj[3][1] + objDat["sizeY"] * obj[7], odat[3][1] + objdat["sizeY"] * odat[7]))

            if diX <= R and diY <= R:
                free_id = next(i for i in range(len(nearObj) + 1) if i not in nearObj)
                nearObj[free_id] = (oid, odat)

        return nearObj

    def posOnObject(self,pos):

        for oid, odat in DB.id.items():
            objdat = DB.objects[self.searchName(odat[2])]
            if pos[0] >= odat[3][0] and pos[0] <= odat[3][0] + objdat["sizeX"] and pos[1] >= odat[3][1] and pos[1] <= odat[3][1] + objdat["sizeY"]:
                return(odat,True)
        return(None,False)


file = file_lib()

class physick_lib:  # Библеотека для работы с физикой

    def __init__(self):
        pass

    def check_triggers(self,id):
        id_dat = DB.id[id]
        coll = self.collide(id)
        for i in coll:            
            obj = DB.objects[file.searchName(coll[i][0][2])]
            if obj["type"] == "trigger":
                obj["function"](*obj["args"])

    def place(self, map, obj_name, pos, scale = 1):  # Размещение объекта и присваевание id
        obj = DB.objects[file.searchName(obj_name)]
        free_id = next(i for i in range(len(DB.id) + 1) if i not in DB.id)
        DB.id[free_id] = [free_id, map, obj["name"], pos, 0, 0, [0,0,0], scale]
        return free_id

    def collide(self, id_num, id1 = None):  #  проверка косаний по радиусу 3 или между id

        tochobj = {}

        id = DB.id[id_num]

        if id1 == None:
            id1 = file.nearObj(id_num, 3)

        playerdat = DB.objects[file.searchName(id[2])]

        px = id[3][0] + (playerdat["sizeX"] * id[7])
        py = id[3][1] + (playerdat["sizeY"] * id[7])

        for obj_id,obj in id1.items():# проверка на столкновение

            obj_id,obj = obj

            objdat = DB.objects[file.searchName(obj[2])]

            ox = obj[3][0] + (objdat["sizeX"] * obj[7])
            oy = obj[3][1] + (objdat["sizeY"] * obj[7])

            inobj = (id[3][0] < ox and
                        px > obj[3][0] and
                        id[3][1] < oy and
                        py > obj[3][1])
            toching = (
                id[3][0] - 1 < ox
                and px + 1 > obj[3][0]
                and id[3][1] - 1 < oy
                and py + 1 > obj[3][1]
            )
            nextframe = (
                id[3][0] + DB.id[id_num][4] < ox + DB.id[obj_id][4]
                and px + DB.id[id_num][4] > obj[3][0] + DB.id[obj_id][4]
                and id[3][1] + DB.id[id_num][5] < oy + DB.id[obj_id][5]
                and py + DB.id[id_num][5] > obj[3][1] + DB.id[obj_id][5]
            )
            if inobj or toching or nextframe: # проверка с какой стороны

                if inobj:
                    side_lef = px - obj[3][0]
                    side_rig = ox - id[3][0]
                    side_top = py - obj[3][1]
                    side_bot = oy - id[3][1]
                elif toching:
                    side_lef = px + 1 - obj[3][0]
                    side_rig = ox - id[3][0] - 1
                    side_top = py + 1 - obj[3][1]
                    side_bot = oy - id[3][1] - 1
                elif nextframe:
                    side_lef = px + DB.id[id_num][4] * DB.globalDat[0] - (obj[3][0] + DB.id[obj_id][4] * DB.globalDat[0])
                    side_rig = ox + DB.id[obj_id][4] * DB.globalDat[0] - (id[3][0] + DB.id[id_num][4] * DB.globalDat[0])
                    side_top = py + DB.id[id_num][5] * DB.globalDat[0] - (obj[3][1] + DB.id[obj_id][5] * DB.globalDat[0])
                    side_bot = oy + DB.id[obj_id][5] * DB.globalDat[0] - (id[3][1] + DB.id[id_num][5] * DB.globalDat[0])
                minX = min(side_lef, side_rig)
                minY = min(side_top, side_bot)

                if minX < minY:
                    if side_lef < side_rig:
                        side = "right"
                    else:
                        side = "left"
                else:
                    if side_top < side_bot:
                        side = "bottom"
                    else:
                        side = "top"

                free_id = next(i for i in range(len(tochobj) + 1) if i not in tochobj)
                if inobj:
                    tochobj[free_id] = (obj, inobj, side,"inobj")
                elif toching:
                    tochobj[free_id] = (obj, toching, side, "toching")
                elif nextframe:
                    tochobj[free_id] = (obj, toching, side, "Nframe")
        return tochobj           

    def physick(self, id, phis = (1,1)): # физика, проверка колизий, изменение позиций

        DB.cache["onground"] = False
        sides = {}

        if phis[1] == 1:
            coll = self.collide(id)
            main_obj = DB.objects[file.searchName(DB.id[id][2])]
            for i in coll:
                free_id = next(i for i in range(len(sides) + 1) if i not in sides)
                sides[free_id] = coll[i][2] 
            for i in coll:
                obj = DB.objects[file.searchName(coll[i][0][2])]
                if obj["type"] == "map" or obj["type"] == "trigger":
                    continue
                if coll[i][1]: # остановка при столкновении
                    if coll[i][2] == "right":
                        if coll[i][3] in ["inobj","Nframe"]:
                            DB.id[id][3][0] = coll[i][0][3][0] - main_obj["sizeX"] * DB.id[id][7]
                        if DB.id[id][4] >= 0:
                            DB.id[id][4] = 0 
                    elif coll[i][2] == "left":
                        if coll[i][3] in ["inobj", "Nframe"]:
                            DB.id[id][3][0] = coll[i][0][3][0] + main_obj["sizeX"] * DB.id[id][7]
                        if DB.id[id][4] < 0:
                            DB.id[id][4] = 0  

                    if coll[i][2] == "top":
                        if DB.id[id][5] < 0:
                            DB.id[id][5] = 0
                        if "bottom" in sides:
                            continue
                        if coll[i][3] in ["inobj", "Nframe"]:
                            DB.id[id][3][1] = coll[i][0][3][1] + main_obj["sizeY"] * DB.id[id][7]
                    elif coll[i][2] == "bottom":
                        if DB.id[id][5] > 0:
                            DB.id[id][5] = 0
                        if "top" in sides:
                            continue
                        DB.cache["onground"] = True
                        if coll[i][3] in ["inobj", "Nframe"]:
                            DB.id[id][3][1] = coll[i][0][3][1] - main_obj["sizeY"] * DB.id[id][7]

                    if DB.id[id][4] < coll[i][0][4] or DB.id[id][4] > coll[i][0][4]:
                        if "right" in sides.values() and "left" in sides.values():
                            continue
                        if coll[i][2] == "right" and coll[i][0][4] < 0:
                            DB.id[id][4] = coll[i][0][4]
                        if coll[i][2] == "left" and coll[i][0][4] > 0:
                            DB.id[id][4] = coll[i][0][4]
                    if DB.id[id][5] < coll[i][0][5] or DB.id[id][5] > coll[i][0][5]:
                        if "bottom" in sides.values() and "top" in sides.values():
                            continue
                        if coll[i][2] == "top" and coll[i][0][5] > 0:
                            DB.id[id][5] = coll[i][0][5]
                        if coll[i][2] == "bottom" and coll[i][0][5] < 0:
                            DB.id[id][5] = coll[i][0][5]
        if phis[0] != 0 and not DB.cache["onground"]:
            DB.id[id][5] = DB.id[id][5] + phis[0]
        if DB.id[id][4] != 0:  # изменение позиций

            DB.id[id][3][0] += DB.id[id][4] * DB.globalDat[0]

        if DB.id[id][5] != 0:

            DB.id[id][3][1] += DB.id[id][5] * DB.globalDat[0]
        obj = DB.objects[file.searchName(DB.id[id][2])]
        if obj["resistance"] > 0:
            self.resistance(id)

    def setVector(self, id, vector, value):# Устанавливает направление
        if vector.lower() == "x":

            vector = 4

        elif vector.lower() == "y":

            vector = 5

        if value != DB.id[id][vector]:
            DB.id[id][vector] = value

    def setPos(self,id,posx,posy):

        DB.id[id][3][0],DB.id[id][3][1] = posx,posy

    def resistance(self, id): #сопротевление

        collision = self.collide(id)

        for obj_id,coll in collision.items():
            obj = DB.objects[file.searchName(coll[0][2])]
            if obj["type"] == "map" or obj["type"] == "trigger":
                continue
            if not coll[1]:
                continue
            side = coll[2]
            reactable = obj["resistance"]

            if side == "left" or side == "right": #проверка какой вектор уменьшать

                if DB.id[id][5] > 0:  # проверка куда уменьшать
                    if DB.id[id][5] > reactable:
                        DB.id[id][5] = DB.id[id][5] - reactable
                    elif DB.id[id][5] <= reactable:
                        DB.id[id][5] = 0

                elif DB.id[id][5] < 0:
                    if DB.id[id][5] < reactable:
                        DB.id[id][5] = DB.id[id][5] + reactable
                    elif DB.id[id][5] >= reactable:
                        DB.id[id][5] = 0
            if side == "bottom" or side == "top":
                if DB.id[id][4] > 0:  # проверка куда уменьшать
                    if DB.id[id][4] > reactable:
                        DB.id[id][4] = DB.id[id][4] - reactable
                    elif DB.id[id][4] <= reactable:
                        DB.id[id][4] = 0

                elif DB.id[id][4] < 0:
                    if DB.id[id][4] < reactable:
                        DB.id[id][4] = DB.id[id][4] + reactable
                    elif DB.id[id][4] >= reactable:
                        DB.id[id][4] = 0
physick = physick_lib()
class grafic_lib:  # Библеотека для работы с графикой

    def __init__(self):
        pass

    def set_colour(self, id, red,green,blue):  # Присваивание цвета (временно)
        DB.id[id][6] = [red,green,blue]

    def load_sprite(self, way, name, preset=(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)):
        img = Image.open(way)
        img_dat = img.convert("RGBA").tobytes()
        w,h = img.size
        sprite_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, sprite_id)
        GL.glTexParameteri(*preset)
        GL.glTexParameteri(*preset)
        GL.glTexImage2D(
        GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, 
        w, h, 0, 
        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, img_dat
        )
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        DB.rendDat["sprites_id"][name] = [sprite_id, way]

grafic = grafic_lib()
class input_lib: # Библиотека для работы с вводом

    def __init__(self):
        self.pressed_keys = {}

    def bind_button(self, button, function, args, pressType): #бинд кнопки, pressType = "short"\"long"\"un_short"\"un_long"

        free_id = next(i for i in range(len(DB.pbut) + 1) if i not in DB.pbut)

        DB.pbut[free_id] = [button, function, args, pressType]
        self.pressed_keys[button] = None

    def get_mouse_pos(self):

        win = DB.rendDat["window"]
        if not win:
            print("Нет окна")
            return None

        mouseX,mouseY = glfw.get_cursor_pos(win)
        return mouseX,mouseY

    def mouseOn(self):

        mouse_pos = self.get_mouse_pos()

        obj = file.posOnObject(mouse_pos)
        if obj[1]:
            otn_pos = (mouse_pos[0]- obj[0][3][0],mouse_pos[1] - obj[0][3][1])
            return(obj[0],otn_pos,True)
        return(None,None,False)

    def check_buttons(self):  # проверка всех клавиш
        glfw.poll_events()

        win = DB.rendDat["window"]
        if not win:
            print("Нет окна")
            return None

        for id,butt in DB.pbut.items():

            if butt[0].startswith("mouse_"):
                if butt[0] == "mouse_left":
                    key_code = glfw.MOUSE_BUTTON_LEFT  # ЛКМ
                elif butt[0] == "mouse_right":
                    key_code = glfw.MOUSE_BUTTON_RIGHT  # ПКМ
                elif butt[0] == "mouse_middle":
                    key_code = glfw.MOUSE_BUTTON_MIDDLE  # Колесико
                else:
                    continue
                key_state = glfw.get_mouse_button(win, key_code)
            else:
                key_code = getattr(glfw, f"KEY_{butt[0].upper()}", None)
                if key_code is None:
                    continue
                key_state = glfw.get_key(win, key_code)

            if key_state == glfw.PRESS:
                if butt[3] == "long" and self.pressed_keys[butt[0]] == True:
                    butt[1](*butt[2])
                elif butt[3] == "short" and self.pressed_keys[butt[0]] == False:
                    butt[1](*butt[2])
                self.pressed_keys[butt[0]] = True

            if key_state == glfw.RELEASE:
                if butt[3] == "un_long" and self.pressed_keys[butt[0]] == False:
                    butt[1](*butt[2])
                    self.pressed_keys[butt[0]] = False
                elif butt[3] == "un_short" and self.pressed_keys[butt[0]] == True:
                    butt[1](*butt[2])
                    self.pressed_keys[butt[0]] = False

                if butt[3] == "short" or butt[3] == "long":
                    self.pressed_keys[butt[0]] = False
input = input_lib()

class render_lib: # библеотека для работы с выводом изображения

    def __init__(self):
        pass

    def window(self, width = 800, hight = 600, name = "Standart window", standartBgColour = (0.15, 0.15, 0.15, 1.0)):

        DB.rendDat["windowdat"] = [width,hight,name]

        if not glfw.init():
            print("нет glfw")
            return None

        DB.rendDat["window"] = glfw.create_window(DB.rendDat["windowdat"][0],DB.rendDat["windowdat"][1],DB.rendDat["windowdat"][2],None,None)
        if not DB.rendDat["window"]:
            print("нет окна")
            glfw.terminate()
            return None

        glfw.make_context_current(DB.rendDat["window"])
        glfw.swap_interval(1)

        glfw.swap_interval(1)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, DB.rendDat["windowdat"][0], DB.rendDat["windowdat"][1],0,-1,1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glClearColor(*standartBgColour)
        print("окно создано")
        return True

    def render_frame(self, curent_map):

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        for oid, odat in DB.id.items():
            if odat[1] != curent_map or DB.objects[file.searchName(odat[2])]["type"] == "trigger":
                continue

            obj_id = file.searchName(odat[2])

            if obj_id == None:
                print(f"объект {odat[2]} не найден")
                continue

            objdat = DB.objects[obj_id]
            if objdat["sprite"] == None:
                GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
                GL.glColor3ub(odat[6][0],odat[6][1],odat[6][2])
            else:
                GL.glColor3f(1.0, 1.0, 1.0)
                GL.glBindTexture(GL.GL_TEXTURE_2D, DB.rendDat["sprites_id"][objdat["name"]][0])

            GL.glBegin(GL.GL_QUADS)
            GL.glTexCoord2f(0.0, 0.0)
            GL.glVertex2f(odat[3][0], odat[3][1])
            GL.glTexCoord2f(1.0, 0.0)
            GL.glVertex2f(odat[3][0] + objdat["sizeX"] * odat[7], odat[3][1])
            GL.glTexCoord2f(1.0, 1.0)
            GL.glVertex2f(odat[3][0] + objdat["sizeX"] * odat[7], odat[3][1] + objdat["sizeY"] * odat[7])
            GL.glTexCoord2f(0.0, 1.0)
            GL.glVertex2f(odat[3][0], odat[3][1] + objdat["sizeY"] * odat[7])
            GL.glEnd()

        glfw.swap_buffers(DB.rendDat["window"])
        glfw.poll_events()
render = render_lib()
