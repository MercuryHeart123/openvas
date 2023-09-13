import nmap
# import socket   
# hostname=socket.gethostname()   
# IPAddr=socket.gethostbyname(hostname)   
# print("Your Computer Name is:"+hostname)   
# print("Your Computer IP Address is:"+IPAddr) 
# take the range of ports to 
# be scanned


import netifaces as ni
allInterface = ni.interfaces()
networkInterface = []
for interface in allInterface:
    addresses = ni.ifaddresses(interface)
    if ni.AF_INET in addresses:
        ip = addresses[ni.AF_INET][0]['addr']
        netmask = addresses[ni.AF_INET][0]['netmask']
        cidr = sum(bin(int(x)).count('1') for x in netmask.split('.'))
        networkInterface.append({"interface":interface, "ip":ip, "cidr":cidr})
        print(f"{interface} {ip}/{cidr}")
  
file_path = 'output.txt'
file = open(file_path, 'w')
selectedInterface = input("Select interface: ")
interface = networkInterface[int(selectedInterface)]
cidr = interface["cidr"]
ip = interface["ip"]
nm = nmap.PortScanner()
print("starting scan...")
nm.scan(hosts=f"{ip}/{cidr}", arguments="-sP")
hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]
for host, status in hosts_list:
    print(host, file=file)
file.close()
print("scan finished")
