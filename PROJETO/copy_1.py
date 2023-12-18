import asyncio
import getpass
import json
import os
import websockets
import heapq

key_send_lock = asyncio.Lock()

async def update(x,y,enemy_x,enemy_y, state):
    x, y = state.get("digdug")
    enemy_x, enemy_y = state.get("enemies")[0].get("pos"), state.get("enemies")[1].get("pos")

async def sendkey(websocket, key):
    async with key_send_lock:
        await websocket.send(json.dumps({"cmd": "key", "key": key}))

    

    
async def agent_loop(server_address="localhost:8000", agent_name="student"):
    
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        x, y, rockx, rocky, enemy_x, enemy_y, enemy_dir, fire, traverse, enemy_name, enemy_id, camp= 1, 2, 20, 20, 20, 20, 0, None, None, None, 1, False
        digdug_dir = 1  # Initialize digdug direction as right (1)
        
        while True:
            try:
                state = json.loads(await websocket.recv())  # receive game update

                if "map" in state:
                    mapa = state.get("map")
                
                if "digdug" in state:
                    x, y = state.get("digdug")  # get the x and y of digdug
                
                if "enemies" in state and state.get("enemies"):
                    closest_enemy = min(state.get("enemies"), key=lambda e: abs(e.get("pos")[0] - x) + abs(e.get("pos")[1] - y))
                    enemy_x, enemy_y, enemy_dir, fire, traverse, enemy_name, enemy_id = closest_enemy.get("pos")[0], closest_enemy.get("pos")[1], closest_enemy.get("dir"), closest_enemy.get("fire"), closest_enemy.get("traverse"), closest_enemy.get("name"), closest_enemy.get("id")
                    

                if "rocks" in state and state.get("rocks"):
                    rockx, rocky = state.get("rocks")[0].get("pos")  # get the x and y of the rock
                dpedrax, dpedray = rockx - x, rocky - y
                dx, dy = enemy_x - x, enemy_y - y
                #if (abs(enemy_x - x) <= 3 and abs(enemy_y - y) == 0) or (abs(enemy_y - y) <= 3 and abs(enemy_x - x) == 0):
            

                if fire is not None and abs(fire[0][0] - x) <= 4 and fire[0][1] == y:
                    if enemy_dir == 3 and enemy_x >x:
                        await sendkey(websocket, "w" if enemy_dir == 0 else "s")
                        y += -1 ;x += 1 if enemy_dir == 0 else 1
                        digdug_dir = 1 if enemy_dir == 0 else 3
                        
                    elif enemy_dir == 1 and enemy_x < x:
                        await sendkey(websocket, "w" if enemy_dir == 0 else "s")
                        y += -1 ;x += 1 if enemy_dir == 0 else -1  
                        digdug_dir = 1 if enemy_dir == 0 else 3 

                
                
                if abs(enemy_x - x) > 1 or abs(enemy_y - y) > 1 and camp==False:

                    if traverse is not None:
                        if enemy_dir == 0 and enemy_y > y:
                            for _ in range(5):
                                await sendkey(websocket, "s")
                                y -= 1
                        elif enemy_dir == 1 and enemy_x > x:
                            for _ in range(5):
                                await sendkey(websocket, "a")
                                x -= 1
                        elif enemy_dir == 2 and enemy_y < y:
                            for _ in range(5):
                                await sendkey(websocket, "w")
                                y += 1
                        elif enemy_dir == 3 and enemy_x < x:
                            for _ in range(5):
                                await sendkey(websocket, "d")
                                x += 1
                    
                    if abs(dpedrax) <= 2 and abs(dpedray) <= 2:
                        if abs(dpedrax) < abs(dpedray):
                            await sendkey(websocket, "s" if dpedray < 0 else "w")
                            y += 1 if dpedrax < 0 else -1
                            digdug_dir = 2 if dpedray < 0 else 0  # Set direction to down or up
                        else:
                            await sendkey(websocket, "d" if dpedray < 0 else "a")
                            x += 1 if dpedray < 0 else -1
                            digdug_dir = 1 if dpedray < 0 else 3  # Set direction to right or left
                        

                    if abs(dx) > abs(dy):
                        await sendkey(websocket, "d" if dx > 0 else "a")
                        x += 1 if dx > 0 else -1
                        digdug_dir = 1 if dx > 0 else 3  # Set direction to right or left
                    else:
                        await sendkey(websocket, "s" if dy > 0 else "w")    
                        y += 1 if dy > 0 else -1
                        digdug_dir = 2 if dy > 0 else 0  # Set direction to down or up
                #if abs(enemy_x - x) <= 1  and abs(enemy_y - y) <= 1:
                else:
                   
                        
                    if dx == 1 and abs(dy) == 1 and enemy_dir in [0,2]:

                        print("1")
                        await sendkey(websocket, "a")
                        x-=1
                        await asyncio.sleep(0.1)

                        await sendkey(websocket, "d")
                        x+=1
                        await asyncio.sleep(0.1)
                        
                        while(dy != 0):
                            update(x,y,enemy_x,enemy_y, state)
                            print(dy)
                            dx, dy = enemy_x - x, enemy_y - y
                            
                        for _ in range(3): await sendkey(websocket, "A")
                        
                        
                    elif dx == -1 and abs(dy)== 1 and enemy_dir in [0,2]:

                        print("2")
                        await sendkey(websocket, "a")
                        x-=1
                        await asyncio.sleep(0.1)

                        await sendkey(websocket, "d")
                        x+=1
                        await asyncio.sleep(0.1)
                        
                        while(dy != 0):
                            update(x,y,enemy_x,enemy_y, state)
                            print(dy)
                            dx, dy = enemy_x - x, enemy_y - y
                            
                        
                        for _ in range(3): await sendkey(websocket, "A")
                    
                    elif abs(dx) == 1 and (dy) == 1 and enemy_dir in [1,3]:

                        print("3")
                        await sendkey(websocket, "w")
                        x-=1
                        await asyncio.sleep(0.1)

                        await sendkey(websocket, "s")
                        x+=1
                        await asyncio.sleep(0.1)
                        
                        while(dx != 0):
                            update(x,y,enemy_x,enemy_y, state)
                            print(dx)
                            dx, dy = enemy_x - x, enemy_y - y
                        
                        
                        for _ in range(3): await sendkey(websocket, "A")

                    elif abs(dx) == 1 and (dy) == -1 and enemy_dir in [1,3]:

                        print("4")
                        await sendkey(websocket, "s")
                        x-=1
                        await asyncio.sleep(0.1)

                        await sendkey(websocket, "w")
                        x+=1
                        await asyncio.sleep(0.1)
                        
                        while(dx != 0):
                            update(x,y,enemy_x,enemy_y, state)
                            print(dx)
                            dx, dy = enemy_x - x, enemy_y - y
                    
                        
                        for _ in range(3): await sendkey(websocket, "A")

                state["digdug_dir"] = digdug_dir

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", "Fygar")
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
