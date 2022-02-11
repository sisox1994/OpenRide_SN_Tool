import asyncio
from faulthandler import disable
import threading
import time
import tkinter as tk
from tkinter import messagebox
import ble_scanner
from ble_writer import ble_write
import os


#Open Ride 寫入序號的 Characteristic
OPEN_RIDE_CUSTOM_CHAR_UUID = "8EC92001-F315-4F60-9FB8-838830DAEA50"


#System
global Background_Exit
Background_Exit = False

#global btn flag
global Scan_Click
Scan_Click = False   

#global Task flag
global Background_Write_SN_flag
Background_Write_SN_flag = False

#oooooooooooooooooooo UI  Biding Functions ooooooooooooooooooooooooooo
def scan_btn_press():
    global Scan_Click 
    Scan_Click = True
    global scan_libox
    scan_libox.delete(0,tk.END)
    return 0

def clr_btn_press():
    clear_Scan_ListBox()
    return 0

#Double Click Scan Device list
def connect_dbc_press(content):
    print('db click')
    return 0    

#清除 Scan ListBox 內容
def clear_Scan_ListBox():
    global scan_libox
    scan_libox.delete(0,tk.END)

#清除 SN Entry  內容
def clear_sn_Entry():
    global SN_Entry
    SN_Entry.delete(0,tk.END)
    
def disable_UI():
    global SN_Entry
    global scan_libox
    global Write_Button
    global scan_btn
    global clr_btn

    SN_Entry.config(state=tk.DISABLED)
    scan_libox.config(state=tk.DISABLED)
    Write_Button.config(state=tk.DISABLED)
    scan_btn.config(state=tk.DISABLED)
    clr_btn.config(state=tk.DISABLED)

def Enable_UI():
    global SN_Entry
    global scan_libox
    global Write_Button
    global scan_btn
    global clr_btn

    SN_Entry.config(state=tk.NORMAL)
    scan_libox.config(state=tk.NORMAL)
    Write_Button.config(state=tk.NORMAL)
    scan_btn.config(state=tk.NORMAL)
    clr_btn.config(state=tk.NORMAL)

#"寫入SN序號"
def sn_write_press():
    
    #==========  取得 Scan List 選擇的裝置  & (Get BLE Connect Address)=================
    global scan_libox
    global focus_device
       
    focus_device = None #清除殘留

    cuselect = scan_libox.curselection()
    for index in cuselect:          
        focus_device = devices[index]
        print(focus_device.name," " ,focus_device.address)           


    #============= 取得 UI SN 輸入內容 並編成RawData準備發送給BLE =================
    global SN_Entry
    text = SN_Entry.get()

    global sn_raw_data
    sn_raw_data = b'' #清除殘留

    try:
        serial_number = int(text)
        
        if( serial_number > 0 and serial_number <=9999 ):
            print(serial_number)
            #OPEN RIDE 寫序號編碼  
            OPcode = 0xeb            
            head = OPcode.to_bytes(1,'little')
            tail = serial_number.to_bytes(2,'big')
            sn_raw_data = head + tail

        else:
            print('Out of range!!')
            messagebox.showwarning("Out of Range","Please input Number (1~9999)")
            SN_Entry.delete(0,tk.END)

    except:
        messagebox.showerror("Type error","Please input Number (1~9999)")
        SN_Entry.delete(0,tk.END)
    
    
    #準備進行SN寫入
    if focus_device == None:
        messagebox.showerror("No device error","No device selected")
    else:
        #立起Flag 讓背景去執行
        global Background_Write_SN_flag
        Background_Write_SN_flag = True

    return 0

#oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo


#uuuuuuuuuuuuuuuuuuuuuuuuuuu  UI 建構  uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu
def create_OpenRide_SN_Input_UI():
    global win
    global SN_Entry
    global Write_Button

    inputFrame = tk.Frame(win)
    SN_Label = tk.Label(inputFrame,text="SN:").pack(padx=5,side=tk.LEFT,fill=tk.BOTH,expand=1)
    SN_Entry = tk.Entry(inputFrame,width=4,font=('consolas', 20))
    SN_Entry.pack(padx=5,side=tk.LEFT,fill=tk.BOTH)
    Write_Button = tk.Button(inputFrame,text="Write",command=sn_write_press)
    Write_Button.pack(padx=5,side=tk.LEFT,fill=tk.BOTH,expand=1)
    inputFrame.pack(side=tk.TOP,fill=tk.X,ipady=5,pady=10,expand=1)
    

def create_BLE_Scan_UI():
    global win
    global scan_btn
    global clr_btn

    btn_frame = tk.Frame(win)
    scan_btn = tk.Button( btn_frame ,text='Scan',command=scan_btn_press)
    scan_btn.pack(side=tk.LEFT,ipadx=5,ipady=5,fill=tk.BOTH,expand=1)
    clr_btn = tk.Button( btn_frame ,text='Clear',command=clr_btn_press)
    clr_btn.pack(side=tk.LEFT,ipadx=5,ipady=5,fill=tk.BOTH,expand=1)
    btn_frame.pack(side=tk.TOP,fill=tk.X,ipady=20)
    li_frame = tk.Frame(win)
    global scan_libox
    #創造一個 Scrollbar 放在 Frame的右邊 y軸填滿
    scrollbar = tk.Scrollbar(li_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    #創造一個listbox 放在Frame裡面 x軸填滿
    scan_libox = tk.Listbox(li_frame,height=7,font=('consolas', 9))
    scan_libox.bind('<Double-Button>', connect_dbc_press)
    scan_libox.pack(fill=tk.X)
    #將scrollbar和Listbox綁再一起
    scan_libox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=scan_libox.yview)
    li_frame.pack(side=tk.TOP,fill=tk.X)
    return 0

def window_on_closing():
    global Background_Exit
    print("windows close")
    Background_Exit = True 

def creat_window():
    print('Windows Task thread id:', threading.get_ident())
    
    
    global win
    win = tk.Tk()
    win.title('Open Ride SNTool')
    win.geometry("300x270")
    create_BLE_Scan_UI()
    create_OpenRide_SN_Input_UI()

    win.protocol("WM_DELETE_WINDOW", window_on_closing)
    win.mainloop()

#uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu



#xxxxxxxxxxxxx  背景 "異步程式" 處理區塊  xxxxxxxxxxxxxxxxxxxxxxxxxxx

async def scan():
    global devices
    try:
        devices.clear()
        print("devices list clear ok")
    except:
        print("can not clear")
    devices = await ble_scanner.ble_scan(-60)    

    for dev in devices:
        tab_space = " " * (20 - len(dev.name))
        scan_libox.insert(tk.END,f"{dev.name}{tab_space}[{dev.address}]")     

    print("Scan end")

async def ble_write_sn_to_device():    

    global sn_raw_data    
    print(sn_raw_data)
    print(type(sn_raw_data))
    

    disable_UI()
    result = await (ble_write( focus_device.address, OPEN_RIDE_CUSTOM_CHAR_UUID , sn_raw_data ))
    if(result == 1):
        print("write ok")        
        messagebox.showinfo("SN Write","Successfull!")

        Enable_UI()
        clear_Scan_ListBox()
        clear_sn_Entry()
    elif (result == 2):
        Enable_UI()
        messagebox.showerror("SN Write","Fail! Time out")
    elif (result == 3):
        Enable_UI()
        messagebox.showerror("SN Write","Fail! Cant not find device")
    elif (result == 4):
        Enable_UI()
        messagebox.showerror("SN Write","Fail! Bluetooth not Ready!!")

    


def do_Somethong_Background():
    global Scan_Click     
    global Background_Write_SN_flag

    #--------------------------
    if (Scan_Click == True):
        Scan_Click = False
        asyncio.run(scan())  
    #--------------------------
            
    #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    if (Background_Write_SN_flag == True):
        Background_Write_SN_flag = False
        asyncio.run(ble_write_sn_to_device())  
    #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    return 0

#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx




# bbbbbbbbbbbbbbbbbbb 背景執行區塊 bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb


#設定讓Background Task結束
def set_Background_Exit():
    global Background_Exit
    Background_Exit = True


#確認主程式離開
def Is_Background_Exit():
    global Background_Exit
    if (Background_Exit == True):
        return True

def Background_Task():
    
    print('Background Task thread id:', threading.get_ident())
    bg_cnt = 0

    while True:

        #Call 背景處理
        do_Somethong_Background()

        #-----確認Background Task還活著用-----
        time.sleep(0.1)
        if(bg_cnt % 20 == 0):
           print("Background:", bg_cnt/20 )
        bg_cnt += 1     
        #--------------------------------------                    
                
        if (Is_Background_Exit() == True):
            break

# bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb




#將任務分配到新的Thread
async def do_async_job(func):
    ret = await asyncio.to_thread(func)
    print('job done!')
    set_Background_Exit()
    return ret

async def main():

    task1 = asyncio.create_task(do_async_job(Background_Task)) 
    #task2 = asyncio.create_task(do_async_job(creat_window))  

    t = threading.Thread(target=creat_window)
    t.setDaemon(True)
    t.start()

    ret_Values = await asyncio.gather(task1)

    for ret in ret_Values:
        print("result=",ret)


if __name__ ==  "__main__":
    asyncio.run(main())
