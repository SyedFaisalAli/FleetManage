from fastapi import APIRouter
import netifaces

api = APIRouter(
    tags=["api"],
)

@api.get("/hello")
def hello():
    return {"message": "Hello, World!"}


@api.get("/network-status")
def network_status():
    interfaces = netifaces.interfaces()
    result = []

    for interface in interfaces:
        iface_info = {}
        iface_info['interfaceName'] = interface

        addrs = netifaces.ifaddresses(interface)

        if netifaces.AF_INET in addrs:
            addr_info = addrs[netifaces.AF_INET][0]
            iface_info['ipAddress'] = addr_info.get('addr', 'N/A')
            gateway = netifaces.default_gateway()
            default_gateway = gateway.get(netifaces.AF_INET, ("N/A",))[0]
            iface_info['gateway'] = default_gateway
            iface_info['readyStatus'] = 'up'
        else:
            iface_info['ipAddress'] = 'N/A'
            iface_info['gateway'] = 'N/A'
            iface_info['readyStatus'] = 'down'

        result.append(iface_info)

    return result