import threading

lock = threading.Lock()
credentials = {}
         
def update_credentials(inventory):
    inventory_dict = {switch['ip']: {"username": switch['username'], "password": switch['password']} for switch in inventory}
    global credentials
    with lock:
        credentials = inventory_dict

def get_credentials(device_ip):
    with lock:
        return credentials.get(device_ip)
    