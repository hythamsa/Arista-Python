import argparse, sys, cvp, cvpServices, getpass, csv, time

class color:
	HEADER = '\033[95m'
	PURPLE = '\033[95m'
	CYAN = '\033[96m'
	DARKCYAN = '\033[36m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	END = '\033[0m'


def readme():
	print(color.HEADER + color.BOLD + 'Python 2.7.x\n' + color.END)
	print(color.RED + color.BOLD + color.UNDERLINE + 'Required:' + color.END)
	print('Python 2')
	print('cvp')
	print('argparase')
	print('cvpServices')
	print('getpass\n')
	print('This script has been tested against 2019.1.0 BETA release of CVP, and not yet tested against the current production release of CVP 2018.2.4. Further tests are required')
	print('to determine performance.\n')
	print('The purpose of the script is to create the container topology, and then import switches into their respective containers. You have the option of only creating the containers')
	print('without inventory import, or importing inventory into existing containers without the need to create new ones, and as already stated... both.\n')
	print('A future revision (sometime today, or tomorrow) will allow for compliance checking to occur after switches have been uploaded if one so chooses.\n')
	print(color.RED + color.BOLD + color.UNDERLINE + 'Note:' + color.END)
	print('The intent of the command flag "--execute" is to give control to the user in deciding whether or not to execute tasks upon completion of inventory import into its container')
	print('The default is set to "True", requiring "False" to be set explicitly. As one can see in the usage exmaples, "--execute" has not been set, but defaults to "True" based on argparse config.\n')
	print(color.RED + color.BOLD + color.UNDERLINE + 'Usage to create container topology:' + color.END)
	print('python provision-container.py --user cvpadmin --password cvpadmin --cvpserver <IP of CVP server> --container containers.csv\n')
	print(color.RED + color.BOLD + color.UNDERLINE + 'Usage to import switch inventory into container topology:' + color.END)
	print('python provision-container.py --user cvpadmin --password arista123 --cvpserver 10.92.59.17 --inventory switch-to-container-provisioning.csv\n')
	print(color.RED + color.BOLD + color.UNDERLINE + 'Usage to import inventory and place into container topology:' + color.END)
	print('python provision-container.py --user cvpadmin --password arista123 --cvpserver 10.92.59.17 --container containers.csv --inventory switch-to-container-provisioning.csv\n')


def Arguments():
	parser = argparse.ArgumentParser(description='Import Switches into existing, or newly created, Containers')
	parser.add_argument('--user', dest='user', nargs='?', help='CVP username')
	parser.add_argument('--password', dest='passwd', help='CVP administrative password')
	parser.add_argument('--inventory', dest='inventory', help='CSV file with the names/IPs of switches with their associated container')
	parser.add_argument('--execute', dest='execute', default='False', choices=['True', 'False'], help='Execute tasks immediately after import.')
	parser.add_argument('--container', dest='container', help='CSV File with the name of containers to be created')
	parser.add_argument('--cvpserver', dest='cvpserver', nargs='?', help='Name of IP address of CVP server')
	parser.add_argument('--port', dest='port', default='443', type=int, help='Web port service CVP is listening on')
	parser.add_argument('--compliance', dest='compliance', action='store_true', help='Use this flag if a compliance check is to be run after devices are uploaded')
	args=parser.parse_args()

	if len(sys.argv[1:]) == 0:
		parser.print_help()
		print('')
		readme()
		print('')
		parser.exit()

	return verifyargs(args)


def verifyargs(args):

	if args.cvpserver is None:
		args.cvpserver = str(raw_input("What is the name or the IP address of the CVP server? "))

	if args.user is None:
		args.user = str(raw_input("What is the CVP admin username? "))

	if args.passwd is None:
		args.passwd = getpass.getpass()

	return args


def createcontainer(cvpsvcauth,container):

	start = time.time()

	data = []
	with open(container, 'r') as rf:
		reader = csv.DictReader(rf)

		print('')
		for row in reader:
			cn = row['containerName']
			cpn = row['containerParentName']
			pck = row['parentContainerKey']

			if (pck == 'root'):
				print('Creating {} container beneath parent container {}'.format(cn,cpn))
				cvpsvcauth.addContainer(cn,cpn,pck)

			if (pck == ''):
				container_key = cvpsvcauth.searchContainer(cpn)
				key = container_key[0]['Key']

				data.append({
					"containerName": cn,
					"containerParentName": cpn,
					"parentContainerKey": key
					})

	for i in data:
		cn = i['containerName']
		cpn = i['containerParentName']
		pck = i['parentContainerKey']

		print('Creating {} container beneath parent container {}'.format(cn,cpn))
		cvpsvcauth.addContainer(cn,cpn,pck)

	end = time.time()
	exec_time = end - start

	print(color.HEADER + color.BOLD + "Process completed in {}\n".format(exec_time) + color.END)


def importinventory(cvpauth,inventory,execute):

	with open(inventory, 'r') as rf:
		reader = csv.DictReader(rf)

		print('')
		for row in reader:
			sw = row['switch']
			cn = row['containerName']
 			
			print('Importing {} into container {}...'.format(sw,cn))
			start = time.time()
			cvpauth.importDevice(sw,cn,execute)
			end = time.time()

			exec_time = end - start
			print(color.HEADER + color.BOLD + "Process completed in {}\n".format(exec_time) + color.END)
			print('')


def main():
	options = Arguments()

	#Authentication for cvpServices module
	cvpsvcauth = cvpServices.CvpService(options.cvpserver, ssl=True, port=options.port)
	cvpsvcauth.authenticate(options.user,options.passwd)

	#Authentication for cvp module
	cvpauth = cvp.Cvp(options.cvpserver, ssl=True, port=options.port)
	cvpauth.authenticate(options.user,options.passwd)
		
	if (options.container is not None):
		createcontainer(cvpsvcauth,options.container)

	if (options.inventory is not None):
		importinventory(cvpauth,options.inventory,options.execute)

	'''
	# NOT YET CODED
	if (options.compliance is not None):
		checkcompliance()
	'''

if __name__ == '__main__':
	main()