'''
lightring_publisher.py
Tufts Create®3 Educational Robot Example
by Maddie Pero 

In this example we will publish random colors to the LED ring on the Create®3.
'''

'''
These statements allow the Node class to be used.
'''
import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from irobot_create_msgs.msg import AudioNoteVector, AudioNote
from rclpy.time import Duration
from std_msgs.msg import String  # Import String message type for battle cry
import requests
import json
import termios
import tty
import select


'''
These statements import iRobot Create®3 messages and actions.
'''



def fetch_commands(self):
# """ Fetches movement commands from Airtable and maps them to keys """
    URL = 'https://api.airtable.com/v0/app7psTY3i95TjiYI/Table%201'
    HEADERS = {'Authorization': 'Bearer patU8FCP20PtCQfA2.32f6fc12175797c8c6f67985395aef9fb168d3c177ecc092feec853724fd35bd'}

    response = requests.get(url=URL, headers=HEADERS)
    commands = {}

    if response.status_code == 200:
        data = response.json()
        for record in data.get("records", []):
            name = record["fields"].get("Name", "").upper()
            key = record["fields"].get("Notes", "").lower()
            if name and key:
                commands[name] = key
    return commands


def get_key(self):
    """ Reads a single character from terminal without requiring ENTER """
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, termios.tcgetattr(sys.stdin))
    return key

class AudioPublisher(Node):
    def __init__(self):
        super().__init__('audio_publisher')
        self.publisher_ = self.create_publisher(AudioNoteVector, '/cmd_audio', 10)
        self.timer = self.create_timer(20.0, self.publish_audio_notes)  # Adjust timer as needed

    def publish_audio_notes(self):
        audio_msg = AudioNoteVector()
        audio_msg.append = False  # Ensure it does not append to previous notes

        # Define the sequence of notes
        C = AudioNote(frequency=262, max_runtime = Duration(seconds=.5).to_msg())
        D = AudioNote(frequency=294, max_runtime = Duration(seconds=.5).to_msg())
        E = AudioNote(frequency=330, max_runtime = Duration(seconds=.5).to_msg())
        F = AudioNote(frequency=349, max_runtime = Duration(seconds=.5).to_msg())
        G = AudioNote(frequency=392, max_runtime = Duration(seconds=.5).to_msg())
        A2 = AudioNote(frequency=440, max_runtime = Duration(seconds=.5).to_msg())
        B_f = AudioNote(frequency=464, max_runtime = Duration(seconds=0.5).to_msg())
        notes = [
            # E, E, F, G, G, F, E, D, C, C, D, E, E, D, D
            D, D, A2, A2, B_f, B_f, A2, G, G, F, F, E, E, D

        ]

        audio_msg.notes = notes

        self.get_logger().info('Publishing audio notes')
        self.publisher_.publish(audio_msg)


class Publisher(Node):
    '''
    The LEDPublisher class is created which is a subclass of Node.
    This defines the class' constructor.
    '''
    def __init__(self):    
        '''
        The following line calls the Node class's constructor and gives it the Node name,
        which is 'led_publisher.'
        '''
        super().__init__('robot_publisher')

        self.cp = Twist()
        self.cp.angular.x=0.0
        self.cp.angular.y=0.0
        self.cp.angular.z = 0.0
        self.cp.linear.x=0.0
        self.cp.linear.y=0.0
        self.cp.linear.z = 0.0
        self.buffer=""
        self.buffer2=""


        '''
        We are declaring how we want the Node to publish message. We've imported LightringLeds
        from irobot_create_msgs.msg over the topic '/cmd_lightring' with a queue size of 10.
        Queue size is a quality of service setting that limiits amount of queued messages.
        Basically, we are determining what type of data we want to publish. 
        '''
        print('Creating publisher')
        # only want the most recent out, disregard all other changes. 
        self.vel_publisher = self.create_publisher(Twist,'/cmd_vel', 10)
        # self.audio_publisher = self.create_publisher(AudioNoteVector,'/cmd_audio', 10)
        '''
        The timer allows the callback to execute every 2 seconds, with a counter iniitialized.
        '''
        print('Creating a callback timer') 
        timer_period = 0.4
        self.timer = self.create_timer(timer_period, self.timer_callback)
    

    def timer_callback(self):
        '''
        In this function we have an array of all the LED colors we want, and then a 
        randomized list of those colors. 
        The colors and timer are then published. 
        '''

        # current_time = self.get_clock().now()
        # # current_time = 'hello world: %d'
        URL = 'https://api.airtable.com/v0/app7psTY3i95TjiYI/Table%201'


        ''' Format: {'Authorization':'Bearer Access_Token'}
        Note that you need to leave "Bearer" before the access token '''
        Headers = {'Authorization':'Bearer patU8FCP20PtCQfA2.32f6fc12175797c8c6f67985395aef9fb168d3c177ecc092feec853724fd35bd'}

        r = requests.get(url = URL, headers = Headers, params = {})
        '''
        The get request data comes in as a json package. We will convert this json package to a python dictionary so that it can be parsed
        '''
        data = r.json()
        commands = {}
        for record in data.get("records", []):
                name = record["fields"].get("Name", "").upper()
                key = record["fields"].get("Notes", "").lower()
                if name and key:
                    commands[name] = key
        
    
        #self.cp.linear.x=float(commands['LINEAR'])
        #self.cp.angular.z=float(commands['ANGULAR'])
        print(commands)
        
        temp=commands['CONTROL'][1:].strip()
        linear=float(commands['LINEAR'][1:].strip())
        angular=float(commands['ANGULAR'][1:].strip())
        # if True: 
        # if temp !=self.buffer or (temp==self.buffer2 and temp==self.buffer):
        print(temp)
        if temp == "w":
            print("forward")
            self.cp.linear.x= linear
            self.cp.angular.z=0.0
            print(self.cp.linear.x)
        elif temp == "s":
            self.cp.linear.x= -1*linear
            self.cp.angular.z=0.0
        elif temp == "a":    
            self.cp.angular.z = angular
            self.cp.linear.x=0.0
        elif temp == "d":    
            self.cp.angular.z = -1*angular
            self.cp.linear.x=0.0
        else:
            self.cp.linear.x=0.0
            self.cp.angular.z=0.0
    # else:
    #     self.cp.linear.x=0.0
    #     self.cp.angular.z=0.0
        # print(self.vel_publisher)
        print(self.cp)
        self.vel_publisher.publish(self.cp)
        self.buffer2=self.buffer
        self.buffer=temp

        # print(self.cp.angular.y)
        

        # self.lightring.header.stamp = current_time.to_msg()
        # self.lights_publisher.publish(self.lightring)

    def reset(self):
        '''
        This function releases contriol of the lights and "gives" it back to the robot. 
        '''
        self.cp.angular.x=0.0
        self.cp.angular.y=0.0
        self.cp.linear.x= 0.0
        #works
        self.cp.linear.y=0.0
        self.cp.angular.z = 0.0
        #works
        self.cp.linear.z = 0.0

        self.vel_publisher.publish(self.cp)
        
    # def control_robot(self):
    #     """ Keyboard control loop using Airtable keys """
    #     print("\nUse the defined Airtable keys to control the robot. Press 'Q' to exit.")
    #     print("Press 'B' to send a battle cry.")
    #     print(f"Commands: {self.commands}")

    #     key = self.get_key()
    #     print(key)
    #     if key == self.commands.get("FORWARD", ""):  # Move forward
    #         print("forwards")
    #     #     self.cp.linear.x = 0.2
    #     #     self.cp.angular.z = 0.0
    #     elif key == self.commands.get("BACKWARD", ""):  # Move backward
    #         print("backwards")
    #         # self.cp.linear.x = -0.2
    #         # self.cp.angular.z = 0.0
    #     elif key == self.commands.get("LEFT", ""): 
    #         print("left") # Rotate left
    #         # self.cp.linear.x = 0.0
    #         # self.cp.angular.z = 2.0
    #     elif key == self.commands.get("RIGHT", ""): 
    #         print("fright") # Rotate right
    #         # self.cp.linear.x = 0.0
    #         # self.cp.angular.z = -1.0
    #     # elif key.lower() == 'b':  # Send Battle Cry
    #     #     # self.publish_battle_cry()
    #     # elif key.lower() == 'q':  # Quit
    #         print("Exiting...")
            
    #     else:  # Stop when no valid key is pressed
    #         self.cp.linear.x = 0.0
    #         self.cp.angular.z = 0.0
        
        
import threading

def main(args=None):
    '''
    The rclpy library is initialized.
    '''
    rclpy.init(args=args)
    
    '''
    The nodes are created.
    '''
    robot_move = Publisher()
    audio_publisher = AudioPublisher()

    # Create threads for both nodes to run concurrently

    
    # robot_thread = threading.Thread(target=rclpy.spin, args=(robot_move,))
    # audio_thread = threading.Thread(target=rclpy.spin, args=(audio_publisher,))

    try:
        # robot_thread.start()
        # audio_thread.start()

        # # Keep the main thread running until keyboard interrupt
        # robot_thread.join()
        # audio_thread.join()
        rclpy.spin(robot_move)

    except KeyboardInterrupt:
        pass
    finally:
        # audio_publisher.destroy_node()
        robot_move.reset()
        robot_move.destroy_node()
        print('Shutting down')
        rclpy.shutdown()


if __name__ == '__main__':
    main()
