import asyncio
from http import client
from time import sleep
from bleak import BleakClient
import bleak

#OpenRide_addr = "C2:D6:96:28:DA:CA"
OpenRide_addr = "D1:8C:EC:F5:F6:84"
OPEN_RIDE_Write_UUID = "8EC92001-F315-4F60-9FB8-838830DAEA50"

async def Notify_callback(sender: int, data: bytearray):
      print(f"{sender}: {data}")

# async def ble_write(address,char_uuid,data):
#     print('start connect...'," ",address)

#     while True:
#         try:
#             async with BleakClient(address) as client:  
#                 print(f"Connected: {client.is_connected}")

#                 unpaired = await client.unpair()
#                 print(f"unpaired: {unpaired}") 

#                 connect = await client.connect()
#                 print(f"connect: {connect}") 

#                 paired  = await client.pair(protection_level=2) #先配對
#                 print(f"Paired: {paired}") 

#                 while client.is_connected:
#                     discconect = await client.disconnect()
#                     print(f"discconect: {discconect}") 
#                     connect = await client.connect()
#                     print(f"connect: {connect}") 
            
#                     while paired == True:
#                         await client.start_notify(char_uuid, Notify_callback)
#                         try:
#                             await client.write_gatt_char(char_uuid , data , True)
#                         except:
#                             print('ok')
#                             return 1    
#         except asyncio.exceptions.TimeoutError:
#             print("Time out !!")
#             return 2                             
#         except bleak.exc.BleakError:
#             print("Cant not find device") 
#             return 3        
#         except OSError:
#             print("Bluetooth not Ready!!")  
#             return 4  
                


async def ble_write(address,char_uuid,data):
    

    while True:
        try:
                client = BleakClient(address)
                if(client.is_connected == True):
                    print(f"Aleady Connected")
                    unpaired = await client.unpair()
                    print(f"unpaired: {unpaired}")
                    # discconect = await client.disconnect()
                    # print(f"discconect: {discconect}") 

                print('start connect...'," ",address)
                connect = await client.connect(timeout=5.0)
                print(f"connect: {connect}") 
                 # connect = await client.connect()
                # print(f"connect: {connect}") 
                
                while client.is_connected:
                    # connect = await client.connect()
                    # print(f"connect: {connect}") 
                    paired  = await client.pair(protection_level=2) #先配對
                    print(f"Paired: {paired}") 

                    while paired == True:                    

                        await client.start_notify(char_uuid, Notify_callback)
                        print("notify ok") 
                        try:
                            await client.write_gatt_char(char_uuid , data , True)
                            return 1  
                        except:
                            print('ok')
                            return 1    
                    print("out paired")
                print("out connected")
        except asyncio.exceptions.TimeoutError:
            print("Time out !!")
            return 2                             
        except bleak.exc.BleakError:
            unpaired = await client.unpair()
            print(f"unpaired: {unpaired}")
            print("Cant not find device") 
            return 3        
        except OSError:
            unpaired = await client.unpair()
            print(f"unpaired: {unpaired}")
            
            print("Bluetooth not Ready!!")  
            return 4  
                


    
async def main():

    #OPEN RIDE 寫序號編碼  
    opcode = 0xeb
    serial_number = 12
    head = opcode.to_bytes(1,'little')
    tail = serial_number.to_bytes(2,'big')
    raw_data = head + tail

    #raw_data = b'hello 87'
    print(raw_data)
    print(type(raw_data))

    result = await (ble_write( OpenRide_addr, OPEN_RIDE_Write_UUID , raw_data ))
    if(result == True):
        print("write ok")


if __name__ == '__main__':   
    asyncio.run(main())
