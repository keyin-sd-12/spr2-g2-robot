# Robot - Group 2
# FINAL SPRINT
# KEYIN College

# version 2.5
# 12-AUG-2024

# list of global variables / constants

# used in the 'search_for_marker' function
# sets to be false when marker is found, 
# resets back to True after marker is found and processed
marker_not_found = True

# marker name of the last marker found
## maybe do not need this variable
last_marker_name = ""

# sets to True when the person is found at the marker
# resets to False after robot dropped-off person at safety and returned
# flags that robot has to go back and do not look for makers on the way back
got_person = False

# sets to True when all stops are done and robot is on the way home
all_done_on_the_way_home = False

# sets to True when robot returns after the person drop-off
# and if person was picked up not at reset point, 
# then we skip the pickup point, robot goes further to the next stop point
skip_next_movement = False

# stop point name to do interesting movements (on the way back home)
DO_DANCE_STEP = 'D'

# stop point name to move closer to marker sideways (not to rotate)
SIDEWAYS_TO_MARKER = 'F'

# stop point before zigzag
ZIGZAG_START_POINT = 'B0'
# stop point after zigzag
ZIGZAG_POINT = 'B'

DIRECTION_FORWARD = 'forward'
DIRECTION_BACKWARD = 'backward'

# marker signs
MARKER_PERSON = 'P'
MARKER_DANGER = 'D'
MARKER_FIRE = 'F'
MARKER_1 = '1'
MARKER_2 = '2'
MARKER_3 = '3'

DISTANCE_SPLIT = 450 # (cm) split longer distances into smaller steps of 490 cm

RESET_SLEEP_TIME = 5 # (s) time to sleep at the reset point

DEFAULT_FLASH_PER_SECOND = 3 # default flash rate for the leds
FAST_FLASH_PER_SECOND = 5 # fast flash rate for the leds
SUPER_FAST_FLASH_PER_SECOND = 10 # super fast flash rate for the leds

DEFAULT_TRANSLATION_SPEED = 1 # m/s
DEFAULT_TRANSLATION_SPEED_SLOW = 0.5 # m/s
DEFAULT_ROTATION_SPEED = 60
DEFAULT_GIMBAL_ROT_SPEED = 30
DISTANCE_TO_MOVE_CLOSER_TO_MARKER = 0.5 # m
DISTANCE_TO_MOVE_SIDEWAYS_CLOSER_TO_MARKER = 0.6 # m

COLOR_ORANGE = (255, 127, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_PURPLE = (127, 0, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_BLUE = (0, 0, 255)

# latest
# dictionary of zigzag movements
DICT_ZIGZAG = {        
                'distance':     [    0 ,      80,      35,     158,     40,    46,     152,   48,     83,     63],
                'angle':        [90-3.5,  90-3.5,  90-3.5,  90-3.5,     90,  39.6, 90-39.6,   90,     90,      0],
                'clockwise':    [ False,    True,    True,   False,  False,  True,    True, True,  False,   True]
}           

# dictionary of lists of point names and corresponding distances robot has to go along the path (indexes 0-8) 
# (to reach that point from the previus stop point)
# zigzag has two corresponding points - 'B0' as start, and 'B' as it's end
# cm, index 0 = start point A, index 8 = finish point H
DICT_STOPS = {
               'name':     ['A', 'B0',   'B',   'C',   'D',   'E',   'F',   'G',    'H' ],
               'distance': [ 0,   576,   279,   661,   496,   412,   468,   438,    573 ]
}

# 'forward': list of adjustments to the stop points (in cm) on the way up while returning after dropping off the person, 
# is may be needed since the robot doesn't stop anymore at B0 and marker points, filled out experimentally
#
# 'backward': list of adjustments to the stop points (in cm) on the way back to the stand, 
# is needed to account for robot's length and other factors, filled out experimentally
#
# *** these corrections are added to the distances between the stop points in the DICT_STOPS['distance'] list)
DICT_ADJ = {
    DIRECTION_FORWARD:  [ 0,   0,    0,  0, -5,  0,  0,   0,  -10 ],
    DIRECTION_BACKWARD: [ 0, -22,  +30,  0, +5,  0,  0,   0,    0 ]
}

ANGLE_ADJ_LEFT = 0
ANGLE_ADJ_RIGHT = 0

# set defining which stops are reset points
SET_RESETS= { 'A', 'B', 'D', 'F', 'H' }

# set defining which stops have markers to scan
SET_MARKERS = { 'C', 'E', 'F', 'G' }

# DEBUGGING CONSTANTS / variables - helped to debug the code
recursion_level = 0
WAIT_FOR_CLAPS = False
WAIT_AFTER_EACH_MOVEMENT = False
TIME_TO_WAIT_AFTER_EACH_MOVEMENT = 30
TIME_TO_WAIT_AFTER_EACH_SMALL_MOVEMENT = 5
TIME_TO_WAIT_AFTER_EACH_CALCULATION_MOVEMENT_LISTS = 0
STAND_STILL = False
SKIP_ZIGZAG = False
IMITATE_MARKERS = False
IMITATE_MARKER_LIST = {
                         'name':   [ 'C',           'E',           'F',           'G'           ],
                         'marker': [ MARKER_PERSON, MARKER_PERSON, MARKER_PERSON, MARKER_PERSON ]
}

def sound_recognized_applause_twice(msg):
    print('LEVEL',recursion_level,'-::- ',"Claps detected!..")
    # disable applause detection after 2 claps is detected
    media_ctrl.disable_sound_recognition(rm_define.sound_detection_applause)
    
def wait_for_clap():
    # enable applause detection
    media_ctrl.enable_sound_recognition(rm_define.sound_detection_applause)
    # wait until 2 claps is detected
    print('LEVEL',recursion_level,'-::- ',"waiting for 2 claps to start...")
    media_ctrl.cond_wait(rm_define.cond_sound_recognized_applause_twice)
    # disable applause detection after 2 claps is detected
    #media_ctrl.disable_sound_recognition(rm_define.sound_detection_applause)

# function returns list of smaller distances if total distance is bigger than 490 cm
# otherwise returns list with only one element - total distance
def split_distance(total_distance, divisor=DISTANCE_SPLIT):
    result = []
    while total_distance >= divisor:
        result.append(divisor)
        total_distance = total_distance - divisor
    if total_distance >= 0:
        result.append(total_distance)
    return result    

# function moves robot forward
# splits distance into smaller steps if total distance is longer than DISTANCE_SPLIT (490 cm)
def move_forward(distance_to_move):
    # list do divide distance into smaller steps if total distance is bigger than 490 cm
    small_distances = []
    small_distances = split_distance(distance_to_move)
    number_of_distance_steps = len(small_distances)
    print('LEVEL',recursion_level,'-::- ','CALL TO FIXED DISTANCE:', distance_to_move,' ---> SPLIT',small_distances, ' - (', number_of_distance_steps, ') steps')
    number_of_distance_steps = len(small_distances)
    for step_no in range(number_of_distance_steps):
        dist_cm = small_distances[step_no]
        #print('LEVEL',recursion_level,'-::- ','move', dist_cm, '(step index', step_no+1, 'of', number_of_distance_steps,')')
        if (dist_cm != 0) and (not STAND_STILL): chassis_ctrl.move_with_distance(0, float(dist_cm)/100.0)
    print('LEVEL',recursion_level,'-::- ','FIXED DISTANCE MOVE DONE')
    if WAIT_AFTER_EACH_MOVEMENT: 
       print('LEVEL',recursion_level,'-::- ','waiting after fixed distance move')
       time.sleep(TIME_TO_WAIT_AFTER_EACH_MOVEMENT)        

# do zigzag at point B
def do_zigzag():
    led_ctrl.set_flash(rm_define.armor_all, FAST_FLASH_PER_SECOND)
    led_ctrl.set_top_led(rm_define.armor_top_all, *COLOR_PURPLE, rm_define.effect_flash)
    
    # set gimbal to follow movements of the chassis
    robot_ctrl.set_mode(rm_define.robot_mode_gimbal_follow)
    time.sleep(0.5)
    # set speed to slow for zigzag
    chassis_ctrl.set_trans_speed(DEFAULT_TRANSLATION_SPEED_SLOW)
    time.sleep(0.5)

    # loop through zigzag path
    for i in range(len(DICT_ZIGZAG['distance'])):
        print('LEVEL',recursion_level,'-::- ','Zigzag:', i, '-- distance:', DICT_ZIGZAG['distance'][i], '-- angle:', DICT_ZIGZAG['angle'][i], '-- clockwise:', DICT_ZIGZAG['clockwise'][i])
        if (not STAND_STILL):
            time.sleep(0.5)
            if DICT_ZIGZAG['distance'][i] != 0:  # skip movement if distance is 0
                chassis_ctrl.move_with_distance(0, float(DICT_ZIGZAG['distance'][i]) /100.0)
            time.sleep(0.5)
            if DICT_ZIGZAG['angle'][i] != 0:  # skip rotation if angle is 0
                direction = rm_define.clockwise if DICT_ZIGZAG['clockwise'][i] else rm_define.anticlockwise
                chassis_ctrl.rotate_with_degree(direction, DICT_ZIGZAG['angle'][i])
        media_ctrl.play_sound(rm_define.media_sound_recognize_success,wait_for_complete_flag=True)
                
    # set for independent gimbal control
    robot_ctrl.set_mode(rm_define.robot_mode_free)
    time.sleep(0.5)
    # recenter gimbal
    gimbal_ctrl.recenter()
    chassis_ctrl.set_trans_speed(DEFAULT_TRANSLATION_SPEED)

    led_ctrl.turn_off(rm_define.armor_all)
    led_ctrl.set_flash(rm_define.armor_all, DEFAULT_FLASH_PER_SECOND)
    
    if WAIT_AFTER_EACH_MOVEMENT: 
        print('LEVEL',recursion_level,'-::- ','waiting after zigzar')
        time.sleep(TIME_TO_WAIT_AFTER_EACH_MOVEMENT)        

# move robot closer to to the wall to scan the marker    
def move_closer(distance, sideways=False):
    chassis_ctrl.set_trans_speed(DEFAULT_TRANSLATION_SPEED_SLOW)
    time.sleep(0.5)
    if sideways:
        if not STAND_STILL: chassis_ctrl.move_with_distance(-90, distance)
    else: 
        if not STAND_STILL: 
            robot_ctrl.set_mode(rm_define.robot_mode_gimbal_follow)
            time.sleep(0.5)
            chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
            time.sleep(0.5)
            chassis_ctrl.move_with_distance(0, distance)
            time.sleep(0.5)            
            robot_ctrl.set_mode(rm_define.robot_mode_free)
    gimbal_ctrl.recenter()
    chassis_ctrl.set_trans_speed(DEFAULT_TRANSLATION_SPEED)

    if WAIT_AFTER_EACH_MOVEMENT: time.sleep(TIME_TO_WAIT_AFTER_EACH_SMALL_MOVEMENT)

# move robot away from the wall after scanning the marker
def move_away(distance, sideways=False):
    chassis_ctrl.set_trans_speed(DEFAULT_TRANSLATION_SPEED_SLOW)    
    if sideways:
        if not STAND_STILL: chassis_ctrl.move_with_distance(90, distance)
    else:
        if not STAND_STILL: chassis_ctrl.move_with_distance(180, distance)   # check if we need to deduct some value here
         
    # turn off leds, could have been left on after danger marker
    if (last_marker_name == MARKER_DANGER): 
        led_ctrl.turn_off(rm_define.armor_all)
        led_ctrl.set_flash(rm_define.armor_all, DEFAULT_FLASH_PER_SECOND)

    gimbal_ctrl.recenter()

    # turn back to the stand, if last marker point was MARKER_PERSON, otherwise turn to the ENDPOIND
    if (not sideways) and (not STAND_STILL):
        direction = rm_define.anticlockwise if (last_marker_name == MARKER_PERSON) else rm_define.clockwise
        robot_ct111rl.set_mode(rm_define.robot_mode_gimbal_follow)        
        time.sleep(0.5)
        chassis_ctrl.rotate_with_degree(direction, 90)
        time.sleep(0.5)
        robot_ctrl.set_mode(rm_define.robot_mode_free)        
        time.sleep(0.5)
    elif sideways and (not STAND_STILL) and (last_marker_name == MARKER_PERSON):
        robot_turn(180, False, 1.0)        

    gimbal_ctrl.recenter()
    chassis_ctrl.set_trans_speed(DEFAULT_TRANSLATION_SPEED)
    
    if WAIT_AFTER_EACH_MOVEMENT: time.sleep(TIME_TO_WAIT_AFTER_EACH_SMALL_MOVEMENT)
         

# scan for the marker
def scan_for_marker(current_step, sideways=False):
    global marker_not_found
    global last_marker_name
    
    gimbal_ctrl.set_rotate_speed(DEFAULT_GIMBAL_ROT_SPEED)

    current_step_name = DICT_STOPS['name'][current_step]
    print(recursion_level,'***** Scanning for any marker *****, Step',current_step,'(',current_step_name,') last marker found was:', last_marker_name)

    # recenter gimbal
    gimbal_ctrl.recenter()
    # turn on bottom leds with 'breath' effect, color white
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, *COLOR_WHITE, rm_define.effect_breath)
    
    # correct for the yaw angle if the robot approaching the marker sideways    
    if sideways:
        gimbal_ctrl.yaw_ctrl(-90)
        yaw_add = -90
    else:
        yaw_add = 0
   
    time.sleep(1)

    # reset last marker name
    last_marker_name = ""
    
    # allow to scan for a marker for 10 sweeps
    vision_ctrl.set_marker_detection_distance(2)
    media_ctrl.play_sound(rm_define.media_sound_scanning)
    count = 0
    while (marker_not_found and count < 7):
        if count == 1: 
            vision_ctrl.enable_detection(rm_define.vision_detection_marker)
            time.sleep(1)
        if marker_not_found: gimbal_ctrl.yaw_ctrl(-60+yaw_add)
        if marker_not_found: gimbal_ctrl.yaw_ctrl(60+yaw_add)
        count += 1
 
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)
    time.sleep(1)
    
    # reset gimbal only if no danges, otherwise if should back off with gimbal down
    if (last_marker_name != MARKER_DANGER): gimbal_ctrl.recenter()

    # reset marker_not_found to True
    marker_not_found = True

    # assume marker 2 if no marker was found
    if last_marker_name == "":
        print('LEVEL',recursion_level,'-::- ','***** ERROR! NO MARKER WAS FOUND, assuming number 2 *****')
        last_marker_name = MARKER_2
    
    print('LEVEL',recursion_level,'-::- ','***** End skanning for marker *****, MARKER FOUND', last_marker_name)

# marker 'P' found, has to bring the person to the stand
# skip_next_movement to True, set last_marker_name to 'P'
def vision_recognized_marker_letter_P(msg):
    global marker_not_found
    global last_marker_name

    # set marker to not found to stop scanning
    gimbal_ctrl.stop()
    marker_not_found = False
    last_marker_name = MARKER_PERSON

    led_ctrl.turn_off(rm_define.armor_all)    
    
    print('LEVEL',recursion_level,'-::- ',' ***** Marker found:', last_marker_name, '*****')

    vision_ctrl.detect_marker_and_aim(rm_define.marker_letter_P)
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)    
    led_ctrl.gun_led_on()
    time.sleep(1)
    media_ctrl.play_sound(rm_define.media_sound_recognize_success)    
    # if got person, return it to the stand with flashing red top leds
    time.sleep(1)
    led_ctrl.gun_led_off()    
    
    led_ctrl.set_top_led(rm_define.armor_top_all, *COLOR_CYAN, rm_define.effect_breath)

    led_ctrl.gun_led_off()    
    gimbal_ctrl.recenter()    

    print('LEVEL',recursion_level,'-::- ',' ***** End marker',last_marker_name, 'procedure *****')
    
    time.sleep(2)
  
# marker 'F' found           
def vision_recognized_marker_letter_F(msg):
    global marker_not_found
    global last_marker_name
    
    gimbal_ctrl.stop()
    marker_not_found = False
    last_marker_name = MARKER_FIRE
    
    led_ctrl.turn_off(rm_define.armor_all)    

    led_ctrl.set_flash(rm_define.armor_all, SUPER_FAST_FLASH_PER_SECOND)
    led_ctrl.set_top_led(rm_define.armor_top_all, *COLOR_RED, rm_define.effect_flash)
    
    print('LEVEL',recursion_level,'-::- ',' ***** Marker found:', last_marker_name, '*****')
   
    vision_ctrl.detect_marker_and_aim(rm_define.marker_letter_F)
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)        
    led_ctrl.gun_led_on()
    time.sleep(1)
    media_ctrl.play_sound(rm_define.media_sound_recognize_success)

    time.sleep(1)
    gun_ctrl.set_fire_count(2)
    gun_ctrl.fire_once()
    gun_ctrl.set_fire_count(1)
    time.sleep(2)
    gun_ctrl.fire_once()
    time.sleep(1)
        
    led_ctrl.turn_off(rm_define.armor_top_all)
    led_ctrl.set_flash(rm_define.armor_all, DEFAULT_FLASH_PER_SECOND)    
    led_ctrl.set_top_led(rm_define.armor_top_all, *COLOR_GREEN, rm_define.effect_always_on)
    led_ctrl.gun_led_off()    
    gimbal_ctrl.recenter()        
    time.sleep(2)
    led_ctrl.turn_off(rm_define.armor_all)
    print('LEVEL',recursion_level,'-::- ',' ***** End marker',last_marker_name, 'procedure *****')
      
# marker 'D' found           
def vision_recognized_marker_letter_D(msg):
    global marker_not_found
    global last_marker_name
    
    marker_not_found = False
    last_marker_name = MARKER_DANGER
        
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)                
    led_ctrl.turn_off(rm_define.armor_all)        
    gimbal_ctrl.recenter()

    print('LEVEL',recursion_level,'-::- ',' ***** Marker found:', last_marker_name, '*****')

    # if danger marker found, robot has to move away from the wall, no need to aim
    media_ctrl.play_sound(rm_define.media_sound_attacked)

    # red leds on the top and bottom
    led_ctrl.set_flash(rm_define.armor_all, FAST_FLASH_PER_SECOND)
    led_ctrl.set_top_led(rm_define.armor_top_all, *COLOR_ORANGE, rm_define.effect_flash)
    gimbal_ctrl.pitch_ctrl(-20)
    
    
    print('LEVEL',recursion_level,'-::- ',' ***** End marker',last_marker_name, 'procedure *****')
    time.sleep(3)
  
# marker '1' found
def vision_recognized_marker_number_one(msg):
    global marker_not_found
    global last_marker_name
    
    marker_not_found = False
    last_marker_name = MARKER_1

    vision_ctrl.disable_detection(rm_define.vision_detection_marker)                
    media_ctrl.play_sound(rm_define.media_sound_recognize_success)
    
    print('LEVEL',recursion_level,'-::- ',' ***** Marker found:', last_marker_name, '*****')
    gimbal_ctrl.recenter()
    
    time.sleep(1)        
    led_ctrl.turn_off(rm_define.armor_bottom_all)

# marker '2' found
def vision_recognized_marker_number_two(msg):
    global marker_not_found
    global last_marker_name
    
    marker_not_found = False
    last_marker_name = MARKER_2

    vision_ctrl.disable_detection(rm_define.vision_detection_marker)                
    media_ctrl.play_sound(rm_define.media_sound_recognize_success)
    
    print('LEVEL',recursion_level,'-::- ',' ***** Marker found:', last_marker_name, '*****')
    gimbal_ctrl.recenter()
    
    time.sleep(1)        
    led_ctrl.turn_off(rm_define.armor_bottom_all)
    
# marker '3' found        
def vision_recognized_marker_number_three(msg):
    global marker_not_found
    global last_marker_name
    
    marker_not_found = False
    last_marker_name = MARKER_3

    vision_ctrl.disable_detection(rm_define.vision_detection_marker)                
    media_ctrl.play_sound(rm_define.media_sound_recognize_success)
    
    print('LEVEL',recursion_level,'-::- ',' ***** Marker found:', last_marker_name, '*****')
    gimbal_ctrl.recenter()

    time.sleep(1)        
    led_ctrl.turn_off(rm_define.armor_bottom_all)
    
# play melody with lights for marker '2'
def melody_with_lights():

    def play_music_with_lights(note, duration, color):
        r, g, b = color  # get the color as a tuple of (r, g, b)
        # set the led mode as always_on
        led_ctrl.set_top_led(rm_define.armor_top_all, r, g, b, rm_define.effect_always_on)
        led_ctrl.set_bottom_led(rm_define.armor_bottom_all, r, g, b, rm_define.effect_always_on)
        media_ctrl.play_sound(note) # play the note
        time.sleep(duration)
   
    melody = [
        (rm_define.media_sound_solmization_1C, 0.3, (255, 0, 0)),  # red
        (rm_define.media_sound_solmization_1E, 0.3, (0, 255, 0)),  # green
        (rm_define.media_sound_solmization_1F, 0.3, (0, 0, 255)),  # blue
        (rm_define.media_sound_solmization_1G, 0.3, (255, 255, 0)),  # yellow
        (rm_define.media_sound_solmization_1A, 0.3, (255, 0, 255)),  # magenta
        (rm_define.media_sound_solmization_1C, 0.3, (0, 255, 255)),  # cyan
        (rm_define.media_sound_solmization_1E, 0.3, (255, 127, 0)),  # orange
        (rm_define.media_sound_solmization_1F, 0.3, (127, 0, 255)),  # purple
        (rm_define.media_sound_solmization_1G, 0.3, (255, 255, 255)),  # white
        (rm_define.media_sound_solmization_1A, 0.3, (127, 127, 127)),  # grey
        (rm_define.media_sound_solmization_1G, 0.6, (255, 0, 0)),  # red
        (rm_define.media_sound_solmization_1F, 0.6, (0, 255, 0)),  # green
        (rm_define.media_sound_solmization_1E, 0.3, (0, 0, 255)),  # blue
        (rm_define.media_sound_solmization_1C, 0.3, (255, 255, 0)),  # yellow
        (rm_define.media_sound_solmization_1D, 0.3, (255, 0, 255)),  # magenta
        (rm_define.media_sound_solmization_1F, 0.3, (0, 255, 255)),  # cyan
        (rm_define.media_sound_solmization_1G, 0.3, (255, 127, 0)),  # orange
        (rm_define.media_sound_solmization_1A, 0.3, (127, 0, 255)),  # purple
        (rm_define.media_sound_solmization_1D, 0.3, (255, 255, 255)),  # white
        (rm_define.media_sound_solmization_1F, 0.3, (127, 127, 127)),  # grey
        (rm_define.media_sound_solmization_1G, 0.3, (255, 0, 0)),  # red
        (rm_define.media_sound_solmization_1A, 0.3, (0, 255, 0)),  # green
        (rm_define.media_sound_solmization_1B, 0.3, (0, 0, 255)),  # blue
        (rm_define.media_sound_solmization_2C, 0.6, (255, 255, 0))  # yellow
    ]

    print('LEVEL',recursion_level,'-::- ','**** DOING MELODY ****')
    for note, duration, color in melody:
        play_music_with_lights(note, duration, color)

    # turn off the lights after the melody is done
    led_ctrl.turn_off(rm_define.armor_all)    
    
def marker_1():
    print('LEVEL',recursion_level,'-::- ','**** DOING MARKER 1 ****')
    sequences = [
                    (60, 0.8),
                    (90, 0.6),
                    (120, 0.4),
                    (120, 0.4),
                    (90, 0.6),
                    (60, 0.8)
    ]   

    media_ctrl.play_sound(rm_define.media_sound_recognize_success)
    #chassis_ctrl.set_trans_speed(DEFAULT_TRANSLATION_SPEED_SLOW)  #question
    
    # set 'chassis_follow' mode (chassis follows gimbal)
    robot_ctrl.set_mode(rm_define.robot_mode_chassis_follow)
    time.sleep(0.5)
    gimbal_ctrl.recenter()
   
    chassis_ctrl.set_trans_speed(0.5)
    chassis_ctrl.set_rotate_speed(30)
    gimbal_ctrl.set_rotate_speed(90)

    gimbal_ctrl.rotate(rm_define.gimbal_right)
    chassis_ctrl.move_and_rotate(45, rm_define.clockwise)
    time.sleep(4)

    gimbal_ctrl.rotate(rm_define.gimbal_left)
    chassis_ctrl.move_and_rotate(-45, rm_define.anticlockwise)
    time.sleep(4)

    gimbal_ctrl.stop()
    chassis_ctrl.stop()

    media_ctrl.play_sound(rm_define.media_sound_recognize_success)

    robot_ctrl.set_mode(rm_define.robot_mode_free)
    time.sleep(0.5)
    gimbal_ctrl.recenter()

    chassis_ctrl.set_rotate_speed(60)
    gimbal_ctrl.set_rotate_speed(60)
   
    gimbal_ctrl.rotate(rm_define.gimbal_right)
    chassis_ctrl.rotate_with_time(rm_define.anticlockwise, 0.4)

    for speed, duration in sequences:
        chassis_ctrl.set_rotate_speed(speed)
        gimbal_ctrl.set_rotate_speed(speed)
        gimbal_ctrl.rotate(rm_define.gimbal_left)
        chassis_ctrl.rotate_with_time(rm_define.clockwise, duration)
        gimbal_ctrl.rotate(rm_define.gimbal_right)
        chassis_ctrl.rotate_with_time(rm_define.anticlockwise, duration)

    gimbal_ctrl.rotate(rm_define.gimbal_left)
    chassis_ctrl.rotate_with_time(rm_define.clockwise, 0.4)
    
    # Stop all movements and reset
    gimbal_ctrl.stop()
    chassis_ctrl.stop()
    time.sleep(1)
    led_ctrl.turn_off(rm_define.armor_all)    
    gimbal_ctrl.recenter()

    # set back default parameters
    robot_ctrl.set_mode(rm_define.robot_mode_free)
    time.sleep(0.5)
    chassis_ctrl.set_trans_speed(DEFAULT_TRANSLATION_SPEED)
    chassis_ctrl.set_rotate_speed(DEFAULT_ROTATION_SPEED)
    gimbal_ctrl.set_rotate_speed(DEFAULT_GIMBAL_ROT_SPEED)
    time.sleep(0.5)

    print('LEVEL',recursion_level,'-::- ','**** END MARKER 1 ****')    

def marker_3(robot_translation_speed=0.5, time_to_move=1):
    print('LEVEL',recursion_level,'-::- ','**** DOING MARKER 3 ****')
    # define direction and rotation lists
    direction_list = [45, -45, -135, 135, -45, 45, 135, -135]
    rotation_list = [rm_define.gimbal_right, rm_define.gimbal_left]

    # define LED colors for each step
    led_colors = [
        (255, 0, 0),     # Red
        (0, 255, 0),     # Green
        (0, 0, 255),     # Blue
        (255, 127, 0),   # Orange
        (127, 0, 255),   # Purple
        (255, 255, 0),   # Yellow
        (255, 0, 255),   # Magenta
        (0, 255, 255)    # Cyan
    ]

    # define movement parameters
    gimbal_rotation_time = 0.25
    gimbal_rotation_speed = 120
    gimbal_rotation_speed_half = int(gimbal_rotation_speed / 2)
    number_of_gimbal_rotations = int(time_to_move / gimbal_rotation_time)

    # Initialize robot
    robot_ctrl.set_mode(rm_define.robot_mode_free)
    time.sleep(0.5)
    gimbal_ctrl.recenter()
    chassis_ctrl.set_trans_speed(robot_translation_speed)
    time.sleep(0.5)

    step_count = 0
    for direction in direction_list:
        # Set LED colors for the current step
        r, g, b = led_colors[step_count % len(led_colors)]
        led_ctrl.set_top_led(rm_define.armor_top_all, r, g, b, rm_define.effect_always_on)
        led_ctrl.set_bottom_led(rm_define.armor_bottom_all, r, g, b, rm_define.effect_always_on)

        # move chassis in the specified direction
        chassis_ctrl.move(direction)

        for rotate_count in range(number_of_gimbal_rotations):
            # set rotation speed
            if step_count == 0:
                rotate_speed = gimbal_rotation_speed_half
            else:
                rotate_speed = gimbal_rotation_speed
            
            gimbal_ctrl.set_rotate_speed(rotate_speed)
            
            gimbal_rotation = rotation_list[rotate_count % len(rotation_list)]
            gimbal_ctrl.rotate(gimbal_rotation)
            time.sleep(gimbal_rotation_time)

        step_count += 1

    # Stop all movements and reset
    gimbal_ctrl.stop()
    chassis_ctrl.stop()
    time.sleep(1)
    led_ctrl.turn_off(rm_define.armor_all)    
    gimbal_ctrl.recenter()

    # set back default parameters
    chassis_ctrl.set_trans_speed(DEFAULT_TRANSLATION_SPEED)
    chassis_ctrl.set_rotate_speed(DEFAULT_ROTATION_SPEED)
    gimbal_ctrl.set_rotate_speed(DEFAULT_GIMBAL_ROT_SPEED)
    time.sleep(0.5)
    
    print('LEVEL',recursion_level,'-::- ','**** END MARKER 3 ****')    


# robot dance at the 'D' point on the way back home
def perform_dance():
    print('LEVEL',recursion_level,'-::- ','**** DOING DANCE ****')

    # turn off leds if any, turn 90 clockwise
    led_ctrl.turn_off(rm_define.armor_all)
    robot_turn(90, True, 1.0)

    # robot wheel parameters
    track_width = 0.195  # Distance between wheels in meters
    wheel_diameter = 0.095  # Diameter of wheels in meters
    radius = 0.3
    inner_speed = 0.4
    correction_factor1 = 0.99
    correction_factor2 = 0.94

    # radii of paths for inner and outer wheels
    outer_track_radius = float(radius + track_width/2)
    inner_track_radius = float(radius - track_width/2)

    # outer wheel liear velocity
    outer_speed = inner_speed * (outer_track_radius / inner_track_radius)

    # linear velocity to wheel rpm
    rpm_inner = (inner_speed * 60) / (math.pi * wheel_diameter)
    rpm_outer = (outer_speed * 60) / (math.pi * wheel_diameter)

    led_ctrl.set_top_led(rm_define.armor_top_all, *COLOR_BLUE, rm_define.effect_always_on)
    # set robot mode to "gimbal lead" (gimbal follows the chassis)
    robot_ctrl.set_mode(rm_define.robot_mode_gimbal_follow)
    time.sleep(0.5)

    # complete the circle
    circle_time = 2 * math.pi * correction_factor1  # Time to complete the circle

    chassis_ctrl.set_wheel_speed(rpm_inner, rpm_outer, rpm_inner, rpm_outer)

    # do 1st circle (rotating to the left)
    tools.timer_ctrl(rm_define.timer_start)
    #start_time = tools.timer_current()
    while True:
        current_time = tools.timer_current()
        if current_time >= circle_time: break

    # time to complete circle
    circle_time = 2 * math.pi * correction_factor2

    chassis_ctrl.set_wheel_speed(rpm_outer, rpm_inner, rpm_outer, rpm_inner)            

    # do 2nd circle (rotating to the right)
    tools.timer_ctrl(rm_define.timer_reset)                
    tools.timer_ctrl(rm_define.timer_start)    
    #start_time = tools.timer_current()
    while True:
        current_time = tools.timer_current()
        if current_time >= circle_time: break

    led_ctrl.turn_off(rm_define.armor_all)                
    gimbal_ctrl.stop()
    chassis_ctrl.stop()
    led_ctrl.turn_off(rm_define.armor_all)    
    gimbal_ctrl.recenter()
    
    robot_turn(90, False, 1.0)
    media_ctrl.play_sound(rm_define.media_sound_recognize_success)
    
    led_ctrl.set_top_led(rm_define.armor_top_all, *COLOR_PURPLE, rm_define.effect_always_on)
    # set 'chassis_follow' mode (chassis follows gimbal)
    robot_ctrl.set_mode(rm_define.robot_mode_chassis_follow)
    time.sleep(0.5)

    gimbal_ctrl.recenter()
   
    chassis_ctrl.set_trans_speed(0.5)
    chassis_ctrl.set_rotate_speed(30)
    gimbal_ctrl.set_rotate_speed(90)

    gimbal_ctrl.rotate(rm_define.gimbal_right)
    chassis_ctrl.move_and_rotate(45, rm_define.clockwise)
    time.sleep(4)

    gimbal_ctrl.rotate(rm_define.gimbal_left)
    chassis_ctrl.move_and_rotate(-45, rm_define.anticlockwise)
    time.sleep(4)

    # Stop all movements and reset
    gimbal_ctrl.stop()
    chassis_ctrl.stop()
    
    led_ctrl.turn_off(rm_define.armor_all)    
    gimbal_ctrl.recenter()
    # set back default parameters
    robot_ctrl.set_mode(rm_define.robot_mode_free)
    time.sleep(0.5)
    gimbal_ctrl.recenter()
    chassis_ctrl.set_trans_speed(DEFAULT_TRANSLATION_SPEED)
    chassis_ctrl.set_rotate_speed(DEFAULT_ROTATION_SPEED)
    gimbal_ctrl.set_rotate_speed(DEFAULT_GIMBAL_ROT_SPEED)
    
    print('LEVEL',recursion_level,'-::- ','**** END DANCE ****')

# robot turn
def robot_turn(degrees, clockwise=True, sleep_time=0.5):
    
    print('LEVEL',recursion_level,'-::- ','**** TURNING AROUND ****')
    direction = rm_define.clockwise if clockwise else rm_define.anticlockwise
    if not STAND_STILL: 
        robot_ctrl.set_mode(rm_define.robot_mode_gimbal_follow)
        time.sleep(sleep_time)
        chassis_ctrl.rotate_with_degree(direction, degrees)
        time.sleep(sleep_time)
        robot_ctrl.set_mode(rm_define.robot_mode_free)
        time.sleep(sleep_time)    
        gimbal_ctrl.recenter()
    print('LEVEL',recursion_level,'-::- ','**** END TURNING AROUND ****')

# reset point procedure, robot stops for 5 seconds and flashes the leds yellow color
def reset_point_procedure(current_step_id, current_step_name, reset_point=True):
    if reset_point:
        print('LEVEL',recursion_level,'-::- ','reset point ', current_step_id,'(',current_step_name,') --> sleeping for', RESET_SLEEP_TIME,'seconds')
        gimbal_ctrl.recenter()        
        media_ctrl.play_sound(rm_define.media_sound_count_down)
        led_ctrl.set_bottom_led(rm_define.armor_bottom_all, *COLOR_YELLOW, rm_define.effect_flash)
        time.sleep(RESET_SLEEP_TIME)
        if WAIT_FOR_CLAPS: wait_for_clap()
        led_ctrl.turn_off(rm_define.armor_bottom_all)
        gimbal_ctrl.recenter()
    else:
        print('LEVEL',recursion_level,'-::- ','regular point (no position needed, not waiting)', current_step_id,'(',current_step_name,')')
        #time.sleep(0.5)
        if WAIT_FOR_CLAPS: wait_for_clap()
    
# function prepares the list of distances for a simplified move 
# (no marker look up, and no stopping at the marker points):
# - to move 0 to 'step_no' point if direction='forward'
# - from 'step_no' to 0 if direction='backward'
def prepare_list_for_simplified_move(step_no, direction=DIRECTION_FORWARD):
    global all_done_on_the_way_home
        
    new_steps = step_no + 1

    # prepare list of distances to move
    list_of_stops = DICT_STOPS['distance'][:new_steps]
    list_of_names = DICT_STOPS['name'][:new_steps]

    # on the very last part when already moving back to base from H,
    # B and F not reset points anymore, remove them from the set
    new_set_resets = SET_RESETS.copy()
    if all_done_on_the_way_home:
        print()
        new_set_resets.discard(ZIGZAG_POINT)
        new_set_resets.discard(SIDEWAYS_TO_MARKER)
           
    # add adjustments to the stop points
    for i in range(new_steps):
        list_of_stops[i] += DICT_ADJ[direction][i]    

    # now need to keep only the reset points in the list
    new_stops = []
    new_names = []
    distance = 0
    for i in range(new_steps):
        if (list_of_names[i] in new_set_resets) or (i == new_steps-1):
            new_stops.append(distance+list_of_stops[i])
            new_names.append(list_of_names[i])
            distance = 0
        else:
            distance += list_of_stops[i]

    #empty the list of stops and names
    list_of_stops = []
    list_of_names = []

    # if direction is forward, then just use the new lists
    if direction == DIRECTION_FORWARD:
        list_of_stops = new_stops
        list_of_names = new_names
    else:
        # now need to reverse the list if we are moving backwards
        new_stops.append(0)
        list_of_stops = new_stops[::-1][:-1]
        list_of_names = new_names[::-1]
        
    # fill out the list of total distances to reach each stop point
    list_of_distances = fill_distances(list_of_stops)

    # new number of steps to be made
    length_stops = len(list_of_stops)

    # returning new number of steps to be made, list of stops, list of names, list of distances
    
    print('='*30)
    print('- LEVEL',recursion_level,'-', direction)
    print('------> Steps:', length_stops)
    print('------> Names:', list_of_names)
    print('------> Stops:', list_of_stops)
    print('--> Distances:', list_of_distances)
    
    if int(TIME_TO_WAIT_AFTER_EACH_CALCULATION_MOVEMENT_LISTS) != 0:
        for i in range (3):
            media_ctrl.play_sound(rm_define.media_sound_attacked)
            time.sleep(TIME_TO_WAIT_AFTER_EACH_CALCULATION_MOVEMENT_LISTS)
    
    return length_stops, list_of_stops, list_of_names, list_of_distances
   
# function moves robot forward to the stop point with the index 'to_step_index'
# if 'do_actions' is set to True, robot will do actions at the stop points (like looking for markers)
# otherwise robot will just move forward to the point, skipping all possible marker places (if after dropping off saved person)
# when this function is used for returning back to the start point, the input lists will be reversed
def move_forward_to_point(to_step_index, stop_points_list, names_list, distances_list, do_actions=True, do_reset_on_first_point=True, do_reset_on_last_point=True):                                
    global all_done_on_the_way_home
    global last_marker_name
    global got_person
    global skip_next_movement
    global recursion_level

    recursion_level += 1
    final_point_name = names_list[to_step_index]
    print('LEVEL',recursion_level,'-::- ',':: call to MOVE_FORWARD_TO_POINT (Recursion level:',recursion_level ,') --> Destination:', final_point_name)
    print('LEVEL',recursion_level,'-::- ','Stops:',stop_points_list)
    print('LEVEL',recursion_level,'-::- ','Names',names_list)
    print('LEVEL',recursion_level,'-::- ','Distances',distances_list)
    
    # reset gimbal
    gimbal_ctrl.recenter()

    # counters / accumulators 
    distance_accumulator = 0
    
    # loop through all stop points, move forward and do actions if needed
    # if do_actions = False, so robot just returning after dropping off the person
    # we do not look for markers on the way back, and pass those stop point without stopping 
    for step in range(to_step_index+1):

        # this is the distance to move to reach the next stop point       
        distance_to_move = stop_points_list[step]
        
        # step name
        step_name = names_list[step]

        # account for possible manual override of the 1st and last points (even if in the list of reset points)
        reset_point = (step_name in SET_RESETS) and (do_reset_on_first_point or (step != 0)) and (do_reset_on_last_point or (step != to_step_index))
        
        # look for marker yes/no, step with index 0 never used for a marker look up
        look_up_marker = (step != 0) and (step_name in SET_MARKERS) and (do_actions)

        # will need zigzag movements is next stop point is 'B' and do_actions is set to True (so it's not on the way back or person drop off)
        need_zigzag = (step_name == ZIGZAG_POINT) and (do_actions) and (not SKIP_ZIGZAG)
        
        print('LEVEL',recursion_level,'-::- ',':LOOPING STEPS::: Step:',step,'(',step_name,'), Do Actions: ',do_actions,', Reset Point:',reset_point,', Zigzag:', need_zigzag,' --> Distance to move:', distance_to_move,'cm')
        
        # now move forward to this stop point, the robot is not at it yet
        if need_zigzag:
            print('LEVEL',recursion_level,'-::- ','**** DO ZIGZAG ****')
            do_zigzag()
        else:   
            # if we just dropped off a person and on the way back, may need skip movement on step,
            # if it not a reset point, just go further to the next stop
            if do_actions and skip_next_movement:
                print('LEVEL',recursion_level,'-::- ','**** SKIP moving', distance_to_move, 'cm, robot has already moved to this point (',step_name,') ***')
                skip_next_movement = False
            # otherwise just proceed with the movement
            else: 
                print('LEVEL',recursion_level,'-::- ','**** MOVE FORWARD ****', distance_to_move, 'cm')
                #if step == 3: 
                move_forward(distance_to_move)
                #else: 
                    #time.sleep(30)
        
        # increment distance traveled
        distance_accumulator += distance_to_move
        print('LEVEL',recursion_level,'-::- ',':: Step:',step,'(',step_name,') MOVEMENT done!, distance accumulated so far:', distance_accumulator,'cm')

        # account for possible manual override of the 1st and last points (even if in the list of reset points)
        reset_point = (step_name in SET_RESETS) and (do_reset_on_first_point or (step != 0)) and (do_reset_on_last_point or (step != to_step_index))
        
        # look for marker yes/no, step with index 0 never used for a marker look up
        look_up_marker = (step != 0) and (step_name in SET_MARKERS) and (do_actions)
 
        # if reset point, sleep for 5 sec and flash lights
        reset_point_procedure(step, step_name, reset_point)

        # if on the way back, then need to do robot dance at 'D' point
        do_dance = (step_name == DO_DANCE_STEP) and all_done_on_the_way_home
        if do_dance:
            if STAND_STILL:
                melody_with_lights()
            else:
                perform_dance()
    
        # look for marker if needed
        if look_up_marker:
            # if we are at point F, we need to move closer to the marker sideways            
            if step_name == SIDEWAYS_TO_MARKER:
                sideways = True
                distance = DISTANCE_TO_MOVE_SIDEWAYS_CLOSER_TO_MARKER
            else:
                sideways = False
                distance = DISTANCE_TO_MOVE_CLOSER_TO_MARKER
                
            # if stand still, assume that robot is sideways
            if STAND_STILL: sideways = True
                
            if not IMITATE_MARKERS:
                move_closer(distance, sideways)
                scan_for_marker(step, sideways)
                move_away(distance, sideways)
            else:
                last_marker_name = IMITATE_MARKER_LIST['marker'][IMITATE_MARKER_LIST['name'].index(step_name)]
                if last_marker_name == MARKER_PERSON:
                    media_ctrl.play_sound(rm_define.media_sound_recognize_success)
                    led_ctrl.set_top_led(rm_define.armor_top_all, *COLOR_CYAN, rm_define.effect_breath)
                    robot_turn(180)
                elif last_marker_name == MARKER_FIRE:
                    media_ctrl.play_sound(rm_define.media_sound_recognize_success,wait_for_complete_flag=True)
                    media_ctrl.play_sound(rm_define.media_sound_recognize_success,wait_for_complete_flag=True)
                    media_ctrl.play_sound(rm_define.media_sound_recognize_success,wait_for_complete_flag=True)
                elif last_marker_name == MARKER_DANGER  :
                    media_ctrl.play_sound(rm_define.media_sound_attacked, wait_for_complete_flag=True)
                    media_ctrl.play_sound(rm_define.media_sound_attacked, wait_for_complete_flag=True)
                    media_ctrl.play_sound(rm_define.media_sound_attacked, wait_for_complete_flag=True)

            # do actions required for the markers found
            if last_marker_name == MARKER_1:
                if not STAND_STILL: 
                    marker_1() # do something with chassiss and gimbal
                else:
                    melody_with_lights()
            elif last_marker_name == MARKER_2:
                melody_with_lights() # play melody with lights
            elif last_marker_name == MARKER_3:
                if not STAND_STILL:
                    marker_3() # do something with lights, chassiss and gimbal
                else:
                    melody_with_lights()
              
        # in case of a passenger, have to go back to the stand, and return (without looking for markers)
        # but skip if already going back to the stand (got_person flag is set to True) 
        # (in order to avoid additional recursion of the 'move_forward_to_point' function)
        if (last_marker_name == MARKER_PERSON) and (not got_person):
            got_person = True
            print('LEVEL',recursion_level,'-::- ','**** GOT PERSON ****(',got_person,'), have to return to the stand --> last_marker_name:', last_marker_name)

            # now need to truncate the list of distances to move, since we are going back to the stand    
            person_dropoff_steps, person_dropoff_stops, person_dropoff_names, person_dropoff_distances = prepare_list_for_simplified_move(step, DIRECTION_BACKWARD)
            print('LEVEL',recursion_level,'-::- ','**** CALL1: Going BACK TO STAND **** from index', step, ' ---> With', person_dropoff_steps, 'steps')
            print('LEVEL',recursion_level,'-::- ',person_dropoff_stops)
            print('LEVEL',recursion_level,'-::- ',person_dropoff_names)
            print('LEVEL',recursion_level,'-::- ',person_dropoff_distances)
            
            # now move back to the stand, this is a recursive function call!
            # move_forward_to_point being called from inside of itself
            move_forward_to_point(person_dropoff_steps-1, person_dropoff_stops, person_dropoff_names, person_dropoff_distances, False, True, False)

            # turn off leds (they were flashing while bringing the person to the stand)
            media_ctrl.play_sound(rm_define.media_sound_recognize_success,wait_for_complete_flag=True)
            time.sleep(1)
            led_ctrl.turn_off(rm_define.armor_all)    
                        
            robot_turn(180)
           
            # important - we are going back to continue on path after person drop-off, but if person 
            # was originally picked up not at reset point, we have to go back one stop point further,
            # there is no need stopping on processed marker point again, since all the actions there have been done
            skip_next_movement = step_name not in SET_RESETS
            goto_step_no = (step+1) if skip_next_movement else step
            
            if (skip_next_movement): print('LEVEL',recursion_level,'-::- ','**** SKIP NEXT MOVEMENT SET TO TRUE, Going back one stop point more to', DICT_STOPS['name'][goto_step_no])
           
            # now need to go back to the next reset point, skipping the marker point where the person was found
            return_dropoff_steps, return_dropoff_stops, return_dropoff_names, return_dropoff_distances = prepare_list_for_simplified_move(goto_step_no, DIRECTION_FORWARD)
            print('LEVEL',recursion_level,'-::- ','**** CALL2: Going BACK TO PICKUP POINT **** to index', step, ' ---> With', return_dropoff_steps, 'steps')
            print('LEVEL',recursion_level,'-::- ',return_dropoff_stops)
            print('LEVEL',recursion_level,'-::- ',return_dropoff_names)
            print('LEVEL',recursion_level,'-::- ',return_dropoff_distances)            

            # after dropoff, move back to the next reset point, this is a recursive function call!
            # move_forward_to_point being called from inside of itself
            move_forward_to_point(return_dropoff_steps-1, return_dropoff_stops, return_dropoff_names, return_dropoff_distances, False, True, False)

            got_person = False

            print('LEVEL',recursion_level,'-::- ','**** END OF PERSON DROP OFF ****')
        
        #reset
            
        # we need to reset robot path again at reset point 'F' (markers '1','2,'3') on the way up
        # or at the end point 'D' (dance point) on the way back (when all_done_on_the_way_home is set to True)
        if do_actions:
            reset_2nd_time = reset_point and (step_name == SIDEWAYS_TO_MARKER) and ((last_marker_name == MARKER_1) or (last_marker_name == MARKER_3)) 
        else:
            reset_2nd_time = reset_point and do_dance

        if reset_2nd_time: 
            print('LEVEL',recursion_level,'-::- ','**** RESET 2nd-time is needed on step:', step_name, ' ****')
            reset_point_procedure(step, step_name, reset_2nd_time)

        print('LEVEL',recursion_level,'-::- ','^^^^^:: Step:',step,'(',step_name,') ended^^^^^^^')
        
        # reset the last marker name - important for the next iteration
        last_marker_name = ""

    recursion_level -= 1
       
# filling out the list of total distances to reach each stop point
def fill_distances(list_stops):
    result = []
    distance = 0
    for i in range(len(list_stops)):
        distance += list_stops[i]
        result.append(distance)
    return result

def start():
    global all_done_on_the_way_home
    
    # prepare robot for the mission
    robot_ctrl.set_mode(rm_define.robot_mode_free)
    chassis_ctrl.set_trans_speed(DEFAULT_TRANSLATION_SPEED) 
    chassis_ctrl.set_rotate_speed(DEFAULT_ROTATION_SPEED)
    gimbal_ctrl.set_rotate_speed(DEFAULT_GIMBAL_ROT_SPEED)
    led_ctrl.set_flash(rm_define.armor_all, DEFAULT_FLASH_PER_SECOND)
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)
    gimbal_ctrl.recenter()
    led_ctrl.turn_off(rm_define.armor_all)

    # START MOVE FORWARD CYCLE
   
    # total number of steps
    steps = len(DICT_STOPS['distance'])

    # filling out list_distances with total distance to reach each stop point
    list_distances = fill_distances(DICT_STOPS['distance'])
    print('LEVEL',recursion_level,'-::- ','== ROBOT PROGRAM START == PATH LENGTH: --->', list_distances[steps-1], 'cm')   
    
    # start of the program, waits for 2 claps
    # wait_for_clap()
    
    print('LEVEL',recursion_level,'-::- ',DICT_STOPS)
    print('LEVEL',recursion_level,'-::- ',list_distances)
    
    # call move forward function to the last point H
    move_forward_to_point(steps-1, DICT_STOPS['distance'], DICT_STOPS['name'], list_distances, True, True, False)    
    
    # END MOVE FORWARD CYCLE
    all_done_on_the_way_home = True
 
    # START COMING BACK TO STAND
    
    print('now has to come back')
    media_ctrl.play_sound(rm_define.media_sound_recognize_success,wait_for_complete_flag=True)
    time.sleep(3)    
    
    print('now has to turn back')
    robot_turn(180)
        
    # new list of distances to move back to the stand (reversed for the backward move)
    back_to_home_number_of_steps, back_to_home_stops, back_to_home_names, back_to_home_distances = prepare_list_for_simplified_move(steps-1, DIRECTION_BACKWARD)
    
    print('LEVEL',recursion_level,'-::- ','== ALL DONE, ON THE WAY HOME, number of steps:', back_to_home_number_of_steps)
    print('LEVEL',recursion_level,'-::- ',back_to_home_stops)
    print('LEVEL',recursion_level,'-::- ',back_to_home_names)
    print('LEVEL',recursion_level,'-::- ',back_to_home_distances)
    
    # now point 'A' is the last point to reach
    # during the backward move, we do not need to stop at the marker points
    # the only action (robot dance) will be at the 'D' point
    move_forward_to_point(back_to_home_number_of_steps-1, back_to_home_stops, back_to_home_names, back_to_home_distances, False, True, False)
    
    robot_turn(180)
    gimbal_ctrl.recenter()    
    
    # END COMING BACK TO STAND
    melody_with_lights()
  
    # ALL DONE
    return(0)    
