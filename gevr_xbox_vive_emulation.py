from math import pi, sin, cos, tan, asin, acos, atan, atan2, sqrt
global pressed

import socket

UDP_IP = ""
UDP_PORT = 9999

def check_socket():
	global sock
	data = 0
	try:
		data, addr = sock.recvfrom(1024)
	except Exception as e:
		print "debug"
	else:
		diagnostics.debug(data)

eps = 38/180.0*pi

def vive_controller():
	i=0
	global posx0
	global posy0
	global posz0
	global Az0
	global h0
	global posx1
	global posy1
	global posz1
	global Az1
	global h1
	global pressed
	#hydra[1].start = xbox360[i].start
	#hydra[0].start = xbox360[i].back

	# Start here
	if pressed == 0:
		if ((xbox360[i].leftShoulder or xbox360[i].rightShoulder) and (xbox360[i].start or xbox360[i].back)):
			hydra[0].start = True
			hydra[1].start = True
			pressed = 1
		elif (xbox360[i].start):
			hydra[1].start = True
			pressed = 1
		elif (xbox360[i].back):
			hydra[0].start = True
			pressed = 1
	elif (xbox360[i].start or xbox360[i].back):
		pressed = 1
	else:
		hydra[0].start = False
		hydra[1].start = False
		pressed = 0

	speed_pos = 1
	speed_rot = .002
	db = 0.1

	# Joystick left controller
	#if xbox360[i].leftShoulder and xbox360[i].leftTrigger > 0.2:
	#	hydra[0].joybutton = xbox360[i].leftThumb
	#	hydra[0].joyx = filters.deadband(xbox360[i].leftStickX, db)
	#	hydra[0].joyy = filters.deadband(xbox360[i].leftStickY, db)

	# Joystick right controller
	if xbox360[i].rightTrigger > 0.2:
		hydra[1].joybutton = xbox360[i].rightThumb
		hydra[1].joyx = filters.deadband(xbox360[i].rightStickX, db)
		hydra[1].joyy = filters.deadband(xbox360[i].rightStickY, db) + 0.1
	elif xbox360[i].leftShoulder:
		# Orbit left controller
		if filters.deadband(xbox360[i].leftStickX, db):
			Az = atan2(posx0, -posz0)
			posx0 += xbox360[i].leftStickX * speed_pos * cos(Az)
			posz0 += xbox360[i].leftStickX * speed_pos * sin(Az)
		if filters.deadband(xbox360[i].leftStickY, db):
			posy0 += xbox360[i].leftStickY * speed_pos
	elif xbox360[i].leftThumb:
		posx0 = -150
		posy0 = 0
		posz0 = -1000
		Az0 = 0
		h0 = pi/4
		[alpha, beta, gamma] = hydra_angles(Az0, h0)
		hydra[0].roll = alpha
		hydra[0].pitch = beta
		hydra[0].yaw = gamma
	elif xbox360[i].rightThumb:
		posx1 = 150
		posy1 = 0
		posz1 = -1000
		Az1 = 0
		h1 = pi/4
		[alpha, beta, gamma] = hydra_angles(Az1, h1)
		hydra[1].roll = alpha
		hydra[1].pitch = beta
		hydra[1].yaw = gamma
	else:
		hydra[1].joybutton = False
		hydra[1].joyx = 0
		hydra[1].joyy = 0

		# Select controller
		if not xbox360[i].rightShoulder:
			ctrl = 0
			Az = Az0
			h = h0
			posx = posx0
			posy = posy0
			posz = posz0
		else:
			ctrl = 1
			Az = Az1
			h = h1
			posx = posx1
			posy = posy1
			posz = posz1

		# Rotate controller
		if filters.deadband(xbox360[i].leftStickX, db):
			Az += xbox360[i].leftStickX * speed_rot
		if filters.deadband(xbox360[i].leftStickY, db):
			dh = -xbox360[i].leftStickY * speed_rot
			if abs(h+dh) < pi/2:
				h += dh
		[alpha, beta, gamma] = hydra_angles(Az, h)

		# Move controller
		if xbox360[i].right:
			posx += speed_pos * cos(Az)
			posz += speed_pos * sin(Az)
		if xbox360[i].left:
			posx -= speed_pos * cos(Az)
			posz -= speed_pos * sin(Az)
		if xbox360[i].up:
			posx += speed_pos * sin(Az)
			posz -= speed_pos * cos(Az)
		if xbox360[i].down:
			posx -= speed_pos * sin(Az)
			posz += speed_pos * cos(Az)

		# Orbit controller
		if filters.deadband(xbox360[i].rightStickX, db):
			AZ = atan2(posx, -posz)
			posx += xbox360[i].rightStickX * speed_pos * cos(AZ)
			posz += xbox360[i].rightStickX * speed_pos * sin(AZ)
		if filters.deadband(xbox360[i].rightStickY, db):
			posy += xbox360[i].rightStickY * speed_pos
			
		# Set controller
		if ctrl == 0:
			Az0 = Az
			h0 = h
			posx0 = posx
			posy0 = posy
			posz0 = posz
		else:
			Az1 = Az
			h1 = h
			posx1 = posx
			posy1 = posy
			posz1 = posz
		hydra[ctrl].roll = alpha
		hydra[ctrl].pitch = beta
		hydra[ctrl].yaw = gamma

	hydra[0].x = posx0
	hydra[0].y = posy0
	hydra[0].z = posz0
	hydra[0].trigger = xbox360[i].leftTrigger

	if not xbox360[i].rightShoulder:
		# Keys left controller
		hydra[0].one = xbox360[i].a
		hydra[0].two = xbox360[i].b
		hydra[0].three = xbox360[i].x
		hydra[0].four = xbox360[i].y
		if xbox360[i].a != xbox360[i].b:
			hydra[0].joyy = (xbox360[i].b - 0.5)/3
			hydra[0].joyx = (xbox360[i].b-0.5)/100
			hydra[0].joybutton = True
		elif xbox360[i].x:
			hydra[0].joyy = 0.9
		else:
			hydra[0].joyx = 0
			hydra[0].joyy = 0
			hydra[0].joybutton = False
		hydra[0].bumper = xbox360[i].x
	else:
		# Keys right controller
		hydra[1].one = xbox360[i].a
		hydra[1].two = xbox360[i].b
		hydra[1].three = xbox360[i].x
		hydra[1].four = xbox360[i].y
		if xbox360[i].b != (xbox360[i].a or xbox360[i].x):
			hydra[0].joyx = (xbox360[i].b-0.5)/100
			hydra[1].joyx = (xbox360[i].b-0.5)/3
		else:
			hydra[0].joyx = 0
			hydra[1].joyx = 0
		hydra[1].joybutton = xbox360[i].a or xbox360[i].b or xbox360[i].x

	hydra[1].x = posx1
	hydra[1].y = posy1
	hydra[1].z = posz1
	hydra[1].trigger = xbox360[i].rightTrigger

	diagnostics.watch(xbox360[i].a)
	diagnostics.watch(xbox360[i].b)
	diagnostics.watch(xbox360[i].x)
	diagnostics.watch(xbox360[i].y)
	diagnostics.watch(xbox360[i].start)
	diagnostics.watch(xbox360[i].back)
	diagnostics.watch(xbox360[i].left)
	diagnostics.watch(xbox360[i].right)
	diagnostics.watch(xbox360[i].up)
	diagnostics.watch(xbox360[i].down)
	diagnostics.watch(xbox360[i].leftStickX)
	diagnostics.watch(xbox360[i].leftStickY)
	diagnostics.watch(xbox360[i].rightStickX)
	diagnostics.watch(xbox360[i].rightStickY)
	diagnostics.watch(xbox360[i].leftShoulder)
	diagnostics.watch(xbox360[i].rightShoulder)
	diagnostics.watch(xbox360[i].leftTrigger)
	diagnostics.watch(xbox360[i].rightTrigger)
	diagnostics.watch(posx0)
	diagnostics.watch(posy0)
	diagnostics.watch(posz0)
	diagnostics.watch(Az0)
	diagnostics.watch(h0)
	diagnostics.watch(posx1)
	diagnostics.watch(posy1)
	diagnostics.watch(posz1)
	diagnostics.watch(Az1)
	diagnostics.watch(h1)
	
def hydra_angles(Az, h):
	return [0, h-eps, Az]

def hydra_init():
	global Az0
	global h0
	[alpha, beta, gamma] = hydra_angles(Az0, h0)

	hydra[0].roll = alpha
	hydra[0].pitch = beta
	hydra[0].yaw = gamma
	hydra[0].x = 0
	hydra[0].y = 0
	hydra[0].z = 0

	hydra[1].roll = alpha
	hydra[1].pitch = beta
	hydra[1].yaw = gamma
	hydra[1].x = 0
	hydra[1].y = 0
	hydra[1].z = 0

def vive_init():
	global posx0
	global posy0
	global posz0
	posx0 = -150
	posy0 = 0
	posz0 = -1000
	global Az0
	global h0
	Az0 = 0
	h0 = pi/4
	global posx1
	global posy1
	global posz1
	posx1 = 150
	posy1 = 0
	posz1 = -1000
	global Az1
	global h1
	Az1 = 0
	h1 = pi/4

global s

if starting:
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setblocking(0)
	sock.bind((UDP_IP, UDP_PORT))
	pressed = 0
	vive_init()
	s = 1
	hydra_init()

if s == 1:
	check_socket()
	vive_controller()
