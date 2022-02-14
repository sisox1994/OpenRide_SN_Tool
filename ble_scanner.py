import asyncio
from bleak import BleakScanner
import threading

scan_devices = []
global filter_rssi
filter_rssi = 0

def scan_callback(device, advertisement_data):
    global dev_cnt
    global filter_rssi
    #print('callback thread id:', threading.get_ident())
    #print(f"[{device.name}]",device.address, "RSSI:", device.rssi ) #advertisement_data
    #print(f"[{device.name}]",device.address, "RSSI:", device.rssi ) #advertisement_data

    if(device.rssi > filter_rssi):
        #過濾重複的adress 
        if(dev_cnt == 0):
            scan_devices.append(device)
            dev_cnt = 1
        else:
            idx = 1 
            for dev in scan_devices:
                if dev.address == device.address:
                    if(len(dev.name) == 0):
                        dev.name = device.name #掃到Name就補進去陣列
                    break
                if dev_cnt == idx:
                    scan_devices.append(device)
                    dev_cnt += 1
                idx+=1
       

async def ble_scan(rssi_in): 
    #print('ble_scan thread id:', threading.get_ident())

    scanner = BleakScanner()
    
    global dev_cnt
    dev_cnt = 0

    global filter_rssi
    filter_rssi = rssi_in

    scanner.register_detection_callback(scan_callback)
    await scanner.start()
    await asyncio.sleep(4.0)
    await scanner.stop()

    #for dev in scanner.discovered_devices:
        #print(dev)    

    #掃完還是沒有Name的填"Unknow"
    for dev in scan_devices:
        if (len(dev.name) == 0):
            dev.name = "Unknow"

    #print('--------------------------------------')
    #for dev in scan_devices:
        #print(dev.address ," [" ,dev.name,"]")
    #print('--------------------------------------')

    return scan_devices

    #fut.set_result(scanner.discovered_devices)
    #for dev in scanner.discovered_devices:
        #print(dev)
    


if __name__ == "__main__":
    asyncio.run(ble_scan(-60))      
    print('--------------------------------------')
    for dev in scan_devices:
        print(dev.address ," [" ,dev.name,"]")
    print('--------------------------------------') 