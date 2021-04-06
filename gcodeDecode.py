def sendGcode():
    gcode = open("ok_plotted.gcode", "r")

    line = gcode.readline()
    while('X' not in line and 'Z' not in line):
        line = gcode.readline()

    line = gcode.readline()

    while('Distance' not in line):
        if('Z' in line):
            #send path packet 2 if z=3, 3 if z=5
            command = line.split(' ')
            command = command[1]
            command = command.replace("Z", "")
            if(command == ".000"):
                command = 0
            else:
                command = 5

            print('Z = ', end='')
            print(command)
        elif('X' in line):
            #send path packet 1
            command = line.split(" ")
            commandX = command[1]
            commandX = commandX.replace('X', '')
            commandY = command[2]
            commandY = commandY.replace('Y', '')
            print("Move: X=", end='')
            print(commandX, end='')
            print(" Y=", end='')
            print(commandY)

        line = gcode.readline()

    #send path packet 4

if __name__ == "__main__":
    sendGcode()
