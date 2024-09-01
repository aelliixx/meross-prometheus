import asyncio
import os
import time

from dotenv import load_dotenv
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from prometheus_client import Gauge
from prometheus_client import start_http_server
from prometheus_client import disable_created_metrics
disable_created_metrics()

load_dotenv()

EMAIL = os.environ.get('MEROSS_EMAIL')
PASSWORD = os.environ.get('MEROSS_PASSWORD')

serverPlugPower = Gauge('server_plug_power', 'Power used by server plug')
serverPlugAmps = Gauge('server_plug_amps', 'Server plug current')
serverPlugVolts = Gauge('server_plug_volts', 'Server plug voltage')
officePlugPower = Gauge('office_plug_power', 'Power used by office plug')
officePlugAmps = Gauge('office_plug_amps', 'Office plug current')
officePlugVolts = Gauge('office_plug_volts', 'Office plug voltage')

async def main():
    http_api_client = await MerossHttpClient.async_from_user_password(api_base_url='https://iotx-eu.meross.com',
                                                                      email=EMAIL,
                                                                      password=PASSWORD)

    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    await manager.async_device_discovery()
    plugs = manager.find_devices(device_type="mss315")
    if len(plugs) < 1:
        print("No MSS315 plugs found...")
    else:
        start_http_server(8000)
        while True:
            for plug in plugs:
                dev = plug

                await dev.async_update()

                instant_consumption = await dev.async_get_instant_metrics()
                print(f"{dev.name} {instant_consumption}")
                if dev.name == "Office":
                    officePlugPower.set(instant_consumption.power)
                    officePlugAmps.set(instant_consumption.current)
                    officePlugVolts.set(instant_consumption.voltage)
                elif dev.name == "Server":
                    serverPlugPower.set(instant_consumption.power)
                    serverPlugAmps.set(instant_consumption.current)
                    serverPlugVolts.set(instant_consumption.voltage)

            time.sleep(5)

    manager.close()
    await http_api_client.async_logout()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.stop()
