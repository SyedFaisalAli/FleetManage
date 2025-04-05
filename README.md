# Fleet Management AI Agent

## Goal

Traditional device management platforms involve a set of actions that are sent down to an agent 
on a device (e.g. microcontrollers, sensors, servers) to trigger a function, as well as regularly 
receive data from the device about its health, sensors, and any application-related data. From 
there, information from these devices are aggregated onto a frontend to allow better view of the 
device fleet state.

When it comes to supporting these devices, sometimes it still takes multiple actions and queries 
to troubleshoot issues such as network and hardware failures that aren’t immediately obvious. 
To aid in this, a proposed LLM agent can provide solutions with the context of a device’s state to 
better troubleshoot issues in the field.
