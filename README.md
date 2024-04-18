# VPN
Python VPN project for CS364 Network Security. All tutorials on this page are made for MacOS users, functions within the VirtualBox application may be in different locations for Windows or Linux users.

## VM Setup
In this project, we will use [VirtualBox](https://www.virtualbox.org/wiki/Downloads) to emulate different Ubuntu systems, and we will use the Ubuntu image configured by SEED Labs available [here](https://seed.nyc3.cdn.digitaloceanspaces.com/SEED-Ubuntu20.04.zip). To create the VM, SEED Labs has made a tutorial [here](https://github.com/seed-labs/seed-labs/blob/master/manuals/vm/seedvm-manual.md#step-1-create-a-new-vm-in-virtualbox).

## Network Setup (VirtualBox)
Our network will consist of a VPN client (Host U), a VPN server (the gateway), and a host in the private network (Host V).\
<img width="700" alt="Screenshot 2024-04-17 at 1 18 17 PM" src="https://github.com/wetzelTanner/VPN/assets/140431902/1e9bf796-345b-45d2-af95-a6e1b8180e6b">

### Cloning VMs
Our network will consist of three VMs, each a copy of the one made in the "VM Setup" step. To do this, we will right click on the VM we wish to clone and select "clone" from the drop-down menu.\
<img width="700" alt="1" src="https://github.com/wetzelTanner/VPN/assets/140431902/248a0d2e-7442-4c2b-8200-5d8e0e98bf0f">\
Another window will open and we will be able to rename our VM copy, in the example below we are creating the VPN server. Do not change any of the other fields, and select next.\
<img width="700" alt="Screenshot 2024-04-17 at 1 01 11 PM" src="https://github.com/wetzelTanner/VPN/assets/140431902/b5737db3-ec0e-4ba5-9dfe-f353ef05b4c6">\
Select finish in the next window, and wait for the machine to be cloned. Do this three times, One for the VPN server, one for the VPN client, and one for the private network host (Host V).

### NAT Network
Next we will set up the NAT network that the VPN server and Host U are connected on. Navigate to the "Tools" menu and select "Network".\
<img width="700" alt="Screenshot 2024-04-17 at 1 38 09 PM" src="https://github.com/wetzelTanner/VPN/assets/140431902/811b4a7b-eab9-4e37-a321-107621a01d94">\
Navigate to the "NAT Networks" menu and create a NAT network of 10.0.2.0/24, name the network, and disable DHCP. For reference, our network should look like the picture below.\
<img width="700" alt="Screenshot 2024-04-17 at 1 44 00 PM" src="https://github.com/wetzelTanner/VPN/assets/140431902/2522ce81-c4da-4ab0-b2e4-78e1acea9242">

#### VPN Server
After creating the network, we will navigate to the network settings of the VPN server and attach adapter 1 to the NAT network we just created, and we will also allow promiscuous mode for VMs, and we must change the MAC address by clicking the blue refresh symbol. This setup is shown in the picture below.\
<img width="650" alt="Screenshot 2024-04-17 at 2 28 26 PM" src="https://github.com/wetzelTanner/VPN/assets/140431902/1546fd5b-e4d5-495c-9555-b42118c5a3ac">

#### Host U
To set up Host U's network, we will take the exact same steps as with the VPN server, but make sure the MAC address is refreshed so that the server and client have different MAC addresses.

### Internal Network
Now we will set up the internal network that connects Host V to the VPN server. We will navigate once again to the network settings of the VPN server and enable adapter 2, attaching it to an "Internal Network". We can name the network anything we want, here I used "VPNINTERNAL", and once again make sure the MAC address is refreshed and promiscuous mode is turned on for VMs. An example of the VPN server setup is in the picture below.\
<img width="650" alt="Screenshot 2024-04-17 at 2 22 51 PM" src="https://github.com/wetzelTanner/VPN/assets/140431902/a9c6074a-67e8-4409-8c94-09627a1a1674">\
Set up Host V the same way, but use adapter 1.

## Network Setup (VM)
After the virtual ethernet adapters have been configured, start the virtual machines.

### VPN Server
When the VPN server is running, navigate to the network settings, and select the IPv4 tab of the NAT network adapter(this should be enp0s3). Select manual, enter the fields in the image below, and click "Apply", do not forget the DNS addresses.\
<img width="550" alt="Screenshot 2024-04-17 at 1 56 52 PM" src="https://github.com/wetzelTanner/VPN/assets/140431902/52ddbb4e-c285-48b3-9b38-176a15829fad">

There should be a second interface in the network settings as well(enp0s8), and this will be for the internal network. Navigate to the same page as the first interface, select manual, enter the fields in the image below, and click "Apply".\
<img width="550" alt="Screenshot 2024-04-17 at 1 57 15 PM" src="https://github.com/wetzelTanner/VPN/assets/140431902/d8d431ee-fa98-420e-98e3-31c7aa6d2f0b">

### Host U
In the Host U machine, there should only be one network adapter. Navigate to the network settings for that adapter and select the IPv4 tab, as we did on the VPN server. Select manual, enter the fields in the image below, and click "Apply", do not forget the DNS addresses.\
<img width="550" alt="Screenshot 2024-04-17 at 2 21 16 PM" src="https://github.com/wetzelTanner/VPN/assets/140431902/f2dff620-bcc1-401a-a1ce-860e5d0b078c">

### Host V
In the Host V machine, there also should only be one network adapter. Navigate to the network settings for that adapter and select the IPv4 tab, as we did on Host U. Select manual, enter the fields in the image below, and click "Apply".\
<img width="550" alt="Screenshot 2024-04-17 at 2 17 22 PM" src="https://github.com/wetzelTanner/VPN/assets/140431902/eed4c189-338d-4268-8c45-64e761a56c67">

### Testing
The network should now be set up correctly! To test this, on the VPN server, ping both Host V and Host U. The VPN server should be able to reach both. Then open the web browser and make sure the VPN server can connect to the internet. Now, on Host U, ping both Host V and the VPN server. Host U should not be able to reach Host V, but should be able to reach the VPN server. Host U should also be able to reach the internet through the web browser. Next, on Host V, ping Host U and the VPN server. Host V should not be able to reach Host U, but should be able to reach the VPN server. Host V should not have internet access. If these tests are successful, the network is setup correctly!
