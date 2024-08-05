# list of global variables / constants

# used in the 'search_for_marker' function
# sets to be false when marker is found, 
# resets back to True after marker is found and processed
marker_not_found = True

do_not_move_forward = True

# marker name of the last marker found
## maybe do not need this variable
last_marker_name = ""

# sets to True when the person is found at the marker
# resets to False after robot dropped-off person at safety and returned
# flags that robot has to go back and do not look for makers on the way back
got_person = False
already_going_back_to_stand = False

# sets to True when all stops are done and robot is on the way home
all_done_on_the_way_home = False

# sets to True when robot has to skip the next movement
# after dropping off the person it returns to the next reset point,
# not stoppping at the makrer point where the person was found
skip_next_movement = False

# stop point name to do interesting movements (on the way back home)
DO_DANCE_STEP = 'D'

# stop point name to move closer to marker sideways (not to rotate)
SIDEWAYS_TO_MARKER = 'F'

# stop point after which robot has to do zigzag movements
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

DISTANCE_SPLIT = 490 # (cm) split longer distances into smaller steps of 490 cm

RESET_SLEEP_TIME = 6.0 # (s) time to sleep at the reset point
DEFAULT_FLASH_PER_SECOND = 3 # default flash rate for the leds

DEFAULT_TRANSLATION_SPEED = 0.5 # m/s
DEFAULT_ROTATION_SPEED = 60
DEFAULT_GIMBAL_ROT_SPEED = 30
DISTANCE_TO_MOVE_CLOSER_TO_MARKER = 0.6 # m
DISTANCE_TO_MOVE_SIDEWAYS_CLOSER_TO_MARKER = 0.8 # m

# dictionary of zigzag movements
DICT_ZIGZAG = {        
                'distance':     [0 ,     85-3,      35,      164-3,     42,     60,    148,      51,    84,     33+7+20-5],
                'angle':        [90-3.5, 90-3.5,  90-3.5,  90-3.5,  90,     39.6,  90-39.6,  90,    90,     0],
                'clockwise':    [False,  True,    True,    False,   False,  True,  True,     True,  False,  True]
}           

# dictionary of lists of point names and corresponding distances robot has to go along the path (indexes 0-8) to reach that point
# zigzag has two corresponding points - 'B0' as start, and 'B' as it's end
# cm, index 0 = start point A, index 8 = finish point H
DICT_STOPS = {
               'name':     ['A', 'B0',                  'B',    'C',    'D',    'E',    'F',    'G',    'H' ],
               'distance': [ 0,   585,  5+35+10+42+96+51+33+27-10, 665+32-27, 458+50, 371+38, 419+58, 398+40, 569+10 ]
}

# 'forward': list of adjustments to the stop points (in cm) on the way up while returning after dropping off the person, 
# is may be needed since the robot doesn't stop anymore at B0 and marker points, filled out experimentally
#
# 'backward': list of adjustments to the stop points (in cm) on the way back to the stand, 
# is needed to account for robot's length and other factors, filled out experimentally
#
# *** these corrections are added to the distances between the stop points in the DICT_STOPS['distance'] list)
DICT_ADJ = {
    DIRECTION_FORWARD:  [ 0,    0,                          0,      0,      -5,      0,      0,      0,      -10 ],
    DIRECTION_BACKWARD: [ 0,    -42,                          +30,      0,      0,      0,      0,      0,      0 ]
}

# set defining which stops are reset points
SET_RESETS= { 'A', 'B', 'D', 'F', 'H' }
# set defining which stops have markers to scan
SET_MARKERS = { 'C', 'E', 'F', 'G' }

# degugging set of points - to skip movement in them
#SET_DEBUGGING = { 'A', 'B0', 'B', 'C', 'D', 'E', 'F', 'G', 'H' }
SET_DEBUGGING = { }

WAIT_FOR_CLAPS = False

# contains total distance from "0" to reach each stop point (per 'DICT_STOPS'), list is filled out in the 'start' function
list_distances = []
                      
# counters/accumulators
# distance_counter = 0
# total_distance = 0
# marker_counter = 0

def sound_recognized_applause_twice(msg):
    print("Claps detected!..")
    #media_ctrl.disable_sound_recognition(rm_define.sound_detection_applause)
    
def wait_for_clap():
    # enable applause detection
    media_ctrl.enable_sound_recognition(rm_define.sound_detection_applause)
    # wait until 2 claps is detected
    print("waiting for 2 claps to start...")
    media_ctrl.cond_wait(rm_define.cond_sound_recognized_applause_twice)
    # disable applause detection after 2 claps is detected
    media_ctrl.disable_sound_recognition(rm_define.sound_detection_applause)


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
# splits distance into smaller steps if total distance is bigger than 490 cm
def move_forward(distance_to_move):
    # list do divide distance into smaller steps if total distance is bigger than 490 cm
    small_distances = []
    small_distances = split_distance(distance_to_move)
    number_of_distance_steps = len(small_distances)
    print('Move forward:', small_distances, ' - total', number_of_distance_steps, 'distance steps')
    number_of_distance_steps = len(small_distances)
    for step_no in range(number_of_distance_steps):
        dist_cm = small_distances[step_no]
        print('move', dist_cm, '(step', step_no+1, 'of', number_of_distance_steps,')')
        if (dist_cm != 0): chassis_ctrl.move_with_distance(0, float(dist_cm)/100.0)

# do zigzag at point B
def do_zigzag():
    for i in range(len(DICT_ZIGZAG['distance'])):
        print('Zigzag:', i, '-- distance:', DICT_ZIGZAG['distance'][i], '-- angle:', DICT_ZIGZAG['angle'][i], '-- clockwise:', DICT_ZIGZAG['clockwise'][i])
        time.sleep(1)
        if DICT_ZIGZAG['distance'][i] != 0:  # skip movement if distance is 0
            chassis_ctrl.move_with_distance(0, float(DICT_ZIGZAG['distance'][i]) /100.0)
        time.sleep(1)
        if DICT_ZIGZAG['angle'][i] != 0:  # skip rotation if angle is 0
            direction = rm_define.clockwise if DICT_ZIGZAG['clockwise'][i] else rm_define.anticlockwise
            chassis_ctrl.rotate_with_degree(direction, DICT_ZIGZAG['angle'][i])
    time.sleep(0.5)


# move robot closer to to the wall to scan the marker    
def move_closer(distance, sideways=False):
    if sideways:
        chassis_ctrl.move_with_distance(-90, distance)
    else: 
        chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
        chassis_ctrl.move_with_distance(0, distance)
    gimbal_ctrl.recenter()    


# move robot away from the wall after scanning the marker
def move_away(distance, sideways=False):
    if sideways:
        chassis_ctrl.move_with_distance(90, distance)
    else:
        chassis_ctrl.move_with_distance(180, distance)
         
        # turn off leds, could have been left on after danger marker
        if not got_person: 
            gimbal_ctrl.recenter()
            led_ctrl.turn_off(rm_define.armor_all)
            #led_ctrl.set_flash(rm_define.armor_all, DEFAULT_FLASH_PER_SECOND)
       
        direction = rm_define.anticlockwise if got_person else rm_define.clockwise
        chassis_ctrl.rotate_with_degree(direction, 90)
        gimbal_ctrl.recenter()
         

# scan for the marker
def scan_for_marker(sideways=False):
    global marker_not_found

    print('***** Scanning for any marker *****')
    # turn on bottom leds with 'breath' effect, color white
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 255, 255, rm_define.effect_breath)
    
    # recenter gimbal and play sound
    gimbal_ctrl.recenter()
    media_ctrl.play_sound(rm_define.media_sound_scanning)
    
    # correct for the yaw angle if the robot approaching the marker sideways    
    if sideways:
        gimbal_ctrl.yaw_ctrl(-90)
        yaw_add = -90
    else:
        yaw_add = 0
    
    # do quick first scan
    gimbal_ctrl.yaw_ctrl(-60+yaw_add)
    gimbal_ctrl.yaw_ctrl(60+yaw_add)
    gimbal_ctrl.recenter()
    
    # now enable marker detection
    vision_ctrl.enable_detection(rm_define.vision_detection_marker)
    
    # allow to scan for a marker for 7 sweeps
    count = 0
    while (marker_not_found and count < 7):
        if marker_not_found: gimbal_ctrl.yaw_ctrl(-60+yaw_add)
        if marker_not_found: gimbal_ctrl.yaw_ctrl(60+yaw_add)
        count += 1
    
    time.sleep(2)

    # reset marker_not_found to True
    marker_not_found = True
    
    print('***** End of scanning for any marker *****')

# marker 'P' found, has to bring the person to the stand
# setting got_person to True, skip_next_movement to True
# set last_marker_name to 'P'
def vision_recognized_marker_letter_P(msg):
    global marker_not_found
    global got_person
    global skip_next_movement
    global last_marker_name

    # set marker to not found to stop scanning
    marker_not_found = False
    last_marker_name = MARKER_PERSON

    # set flag that robot has to return to the stand to drop off the person    
    got_person = True
    
    # importand parameter, after robot drops off a person at the stand,
    # and returns back, it will skip this point, and go through up to the next reset point
    skip_next_movement = True
    
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)    
    led_ctrl.turn_off(rm_define.armor_bottom_all)
    
    print(' ***** Marker found:', last_marker_name, '*****')
    
    # turn on the gun led for aiming
    led_ctrl.gun_led_on()

    print(' --> Start aiming:', last_marker_name, '<--')    
    vision_ctrl.detect_marker_and_aim(rm_define.marker_letter_P)
    media_ctrl.play_sound(rm_define.media_sound_recognize_success)
    print(' --> Aiming ended:', last_marker_name, '<--')

    # if got person, return it to the stand with flashing red top leds
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_breath)

    led_ctrl.gun_led_off()    
    gimbal_ctrl.recenter()    

    print(' ***** End marker',last_marker_name, 'procedure *****')
    
    time.sleep(2)
    

 
# marker 'F' found           
def vision_recognized_marker_letter_F(msg):
    global marker_not_found
    global last_marker_name
    
    marker_not_found = False
    last_marker_name = MARKER_FIRE
    
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)        
    led_ctrl.turn_off(rm_define.armor_bottom_all)    
    
    print(' ***** Marker found:', last_marker_name, '*****')
    # turn on the gun led for aiming    
    led_ctrl.gun_led_on()
    
    print(' --> Start aiming:', last_marker_name, '<--')
    vision_ctrl.detect_marker_and_aim(rm_define.marker_letter_F)
    media_ctrl.play_sound(rm_define.media_sound_recognize_success)
    print(' --> Aiming ended:', last_marker_name, '<--')

    led_ctrl.set_flash(rm_define.armor_all, 10)
    led_ctrl.set_top_led(rm_define.armor_top_all, 0, 0, 255, rm_define.effect_flash)
    time.sleep(2)
    gun_ctrl.set_fire_count(2)
    gun_ctrl.fire_once()
    led_ctrl.set_top_led(rm_define.armor_top_all, 0, 0, 255, rm_define.effect_always_on)
    led_ctrl.set_flash(rm_define.armor_all, DEFAULT_FLASH_PER_SECOND)
    time.sleep(1)
    gun_ctrl.fire_once()
    led_ctrl.gun_led_off()    
    gimbal_ctrl.recenter()    
    time.sleep(2)
    led_ctrl.turn_off(rm_define.armor_all)
    print(' ***** End marker',last_marker_name, 'procedure *****')
    
      
# marker 'D' found           
def vision_recognized_marker_letter_D(msg):
    global marker_not_found
    global last_marker_name
    
    marker_not_found = False
    last_marker_name = MARKER_DANGER
        
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)                
    gimbal_ctrl.recenter()


    print(' ***** Marker found:', last_marker_name, '*****')
    # if danger marker found, robot has to move away from the wall, no need to aim
    media_ctrl.play_sound(rm_define.media_sound_attacked)

    # red leds on the top and bottom
    led_ctrl.set_flash(rm_define.armor_all, 6)
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_flash)
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_flash)
    gimbal_ctrl.pitch_ctrl(-20)
    #gimbal_ctrl.rotate_with_degree(rm_define.gimbal_down, 20)
    
    print(' ***** End marker',last_marker_name, 'procedure *****')
    time.sleep(3)
   
# marker '1' found
def vision_recognized_marker_number_one(msg):
    global marker_not_found
    global last_marker_name
    
    marker_not_found = False
    last_marker_name = MARKER_1

    vision_ctrl.disable_detection(rm_define.vision_detection_marker)                
    media_ctrl.play_sound(rm_define.media_sound_recognize_success)
    
    print(' ***** Marker found:', last_marker_name, '*****')
    
    gimbal_ctrl.recenter()
    
    print(' ***** End marker',last_marker_name, 'procedure *****')    
    
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
    
    print(' ***** Marker found:', last_marker_name, '*****')
    
    gimbal_ctrl.recenter()
    
    print(' ***** End marker',last_marker_name, 'procedure *****')    
    
    time.sleep(1)        
    led_ctrl.turn_off(rm_define.armor_bottom_all)
    
   
    
# marker '3' found        
def vision_recognized_marker_number_three(msg):
    global marker_not_found
    global last_marker_name
    
    marker_not_found = False
    last_marker_name = MARKER_2

    vision_ctrl.disable_detection(rm_define.vision_detection_marker)                
    media_ctrl.play_sound(rm_define.media_sound_recognize_success)
    
    print(' ***** Marker found:', last_marker_name, '*****')
    
    gimbal_ctrl.recenter()
    
    print(' ***** End marker',last_marker_name, 'procedure *****')    
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

    for note, duration, color in melody:
        play_music_with_lights(note, duration, color)

    # turn off the lights after the melody is done
    led_ctrl.turn_off(rm_define.armor_all)    
        

# robot dance at the 'D' point on the way back home
def perform_dance():
    print('**** DOING DANCE ****')
    melody_with_lights()    
    print('**** END DOING ****')

# robot turn
def robot_turn(degrees, clockwise=True, sleep_time=1.0):
    print('**** TURNING AROUND ****')
    time.sleep(sleep_time)
    direction = rm_define.clockwise if clockwise else rm_define.anticlockwise
    chassis_ctrl.rotate_with_degree(direction, degrees)
    time.sleep(sleep_time)
    print('**** END TURNING AROUND ****')

# reset point procedure, robot stops for 5 seconds and flashes the leds yellow color
def reset_point_procedure(current_step_id, current_step_name, reset_point=True):
    if reset_point:
        print('reset point ', current_step_id,'(',current_step_name,') --> sleeping for', RESET_SLEEP_TIME,'seconds')
        media_ctrl.play_sound(rm_define.media_sound_count_down)
        led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 192, 0, rm_define.effect_flash)
        time.sleep(RESET_SLEEP_TIME)
        if WAIT_FOR_CLAPS: wait_for_clap()
        led_ctrl.turn_off(rm_define.armor_bottom_all)
    else:
        print('regular point, sleeping 0.5 seconds')
        time.sleep(0.5)
        if WAIT_FOR_CLAPS: wait_for_clap()
    
# function prepares the list of distances for a simplified move 
# (no marker look up, and no stopping at the marker points):
# - to move 0 to 'step_no' point if direction='forward'
# - from 'step_no' to 0 if direction='backward'
#
# Important: if directiuon='forward', and if 'step_no' 
# is not a reset point (not the list of reset points),
# that means that the robot has to go back to the marker point,
# but we do not want to stop there again, so the function will add one step, 
# so the robot will shoot throung 'step_no' up to the next reset point
def prepare_list_for_simplified_move(step_no, direction=DIRECTION_FORWARD):
    global all_done_on_the_way_home

    # is current point a marker point?
    # this will happen in the case of P marker, when the robot has to go back to the stand
    # otherwise this function is called only for the final backward move from the point H
    is_marker_point = (direction == DIRECTION_FORWARD) and (DICT_STOPS['name'][step_no] in SET_MARKERS)

    # increase step_no by 1 if in forward move we need to go through up to the next reset point
    if is_marker_point:
        step_no += 1
        
    new_steps = step_no + 1

    # prepare list of distances to move
    list_of_stops = DICT_STOPS['distance'][:new_steps]
    list_of_names = DICT_STOPS['name'][:new_steps]
    
    # on the very last part when already moving back to base from H,
    # B and F not rest points anymore, remove them from the set
    new_set_resets = SET_RESETS.copy()
    if all_done_on_the_way_home:
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
    return length_stops, list_of_stops, list_of_names, list_of_distances

   
# function moves robot forward to the stop point with the index 'to_step_index'
# 
# if 'do_actions' is set to True, robot will do actions at the stop points (like looking for markers)
# otherwise robot will just move forward to the point, skipping all possible marker places(if after dropping off saved person)
# 
# by default, will use global lists
# when this function is used for returning back to the start point, those lists will be inverted
def move_forward_to_point(to_step_index, 
                        stop_points_list=DICT_STOPS['distance'],
                        names_list=DICT_STOPS['name'],
                        distances_list=list_distances,
                        do_actions=True, 
                        do_reset_on_first_point=True, do_reset_on_last_point=True):                                
    
    global last_marker_name
    global got_person
    global skip_next_movement
    global already_going_back_to_stand
    
    final_point_name = names_list[to_step_index]
    print(':: MOVE FORWARD --> Final Destination:', final_point_name)
    print(stop_points_list)
    print(names_list)
    print(distances_list)
    
    # reset gimbal and turn off leds just in case
    gimbal_ctrl.recenter()
    led_ctrl.turn_off(rm_define.armor_all)
    
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

        # first do robot movements, then check if we need to do actions after arriving at the stop point
        # will need zigzag movements is next stop point is 'B' and do_actions is set to True (so it's not on the way back or person drop off)

        # will need zigzag movements is next stop point is 'B' and do_actions is set to True (so it's not on the way back or person drop off)
        need_zigzag = (step_name == ZIGZAG_POINT) and (do_actions)
        
        # do zigzag (if this is a first run) or just move forward
        #need_zigzag = False
        
        #need_zigzag = False
        
        if need_zigzag:
            print('**** DO ZIGZAG ****')
            if step_name not in SET_DEBUGGING: 
                do_zigzag()
        else:   
            # if we just dropped off a person and on the way back, skip movement of this marker step,
            # since the robot is driving through it up to the next reset or end point
            # scan for marker function will temporarily set last_marker_name to 'P'
            
            if do_actions and skip_next_movement:
                print('**** SKIP ROBOT MOVE STEP (after person drop off):', distance_to_move, 'cm ***')
                skip_next_movement = False
            else: 
                print('**** MOVE FORWARD ****', distance_to_move, 'cm')
                if step_name not in SET_DEBUGGING:
                    print('11111')
                    #if (not do_not_move_forward) and (not person_on_board):
                    move_forward(distance_to_move)
                time.sleep(1)
                print('**** END MOVING FORWARD ****')

        # account for possible manual override of the 1st and last points (even if in the list of reset points)
        reset_point = (step_name in SET_RESETS) and (do_reset_on_first_point or (step != 0)) and (do_reset_on_last_point or (step != to_step_index))
        
        # look for marker yes/no, step with index 0 never used for a marker look up
        look_up_marker = (step != 0) and (step_name in SET_MARKERS) and (do_actions)

        print(':: Actions:',do_actions,':: Step:',step,'(',step_name,'), Reset Point:',reset_point,', Zigzag:', need_zigzag,' --> Distance to move:', distance_to_move,'cm')
        
        # if on the way back, then need to do robot dance at 'D' point
        do_dance = (step_name == DO_DANCE_STEP) and (all_done_on_the_way_home)
        if do_dance:
            perform_dance()
    
        # if reset point, sleep for 5 sec and flash lights
        reset_point_procedure(step, step_name, reset_point)

        #look_up_marker = False
        # look for marker if needed
        if look_up_marker:
            # if we are at point F, we need to move closer to the marker sideways            
            if step_name == SIDEWAYS_TO_MARKER:
                sideways = True
                distance = DISTANCE_TO_MOVE_SIDEWAYS_CLOSER_TO_MARKER
            else:
                sideways = False
                distance = DISTANCE_TO_MOVE_CLOSER_TO_MARKER
                
            print('**** moving closer to MARKER ****, SIDEWAYS=', sideways)    
            move_closer(distance, sideways)

            # now scan for the marker
            scan_for_marker(sideways)
            
            print('**** moving away from MARKER ****, SIDEWAYS=', sideways)                                      
            move_away(distance, sideways)
            
            # now code to move back to the path after scanning the marker
            print('**** END LOOKING FOR MARKER ****')
            
            # need to add appropriate functions for '1' and '3' markers
            if last_marker_name == MARKER_1:
                perform_dance()
            elif last_marker_name == MARKER_2:
                melody_with_lights() # play melody with lights
            elif last_marker_name == MARKER_3:
                perform_dance()
               
        # in case of a passenger, have to go back to the stand, and return (without looking for markers)
        if got_person and (not already_going_back_to_stand):
            already_going_back_to_stand = True
            print('**** GOT PERSON ****, have to return to the stand --> last_marker_name:', last_marker_name)

            # now need to truncate the list of distances to move, since we are going back to the stand    
            person_dropoff_steps, person_dropoff_stops, person_dropoff_names, person_dropoff_distances = prepare_list_for_simplified_move(step, DIRECTION_BACKWARD)
            print('**** Going BACK TO STAND **** from index', step, ' ---> With', person_dropoff_steps, 'steps')
            print(person_dropoff_stops)
            print(person_dropoff_names)
            print(person_dropoff_distances)
            
            # now move back to the stand, this is a recursive function call!
            # move_forward_to_point being called from inside of itself
            move_forward_to_point(person_dropoff_steps-1, person_dropoff_stops, person_dropoff_names, person_dropoff_distances, False)

            # turn off leds (they were flashing while bringing the person to the stand)
            led_ctrl.turn_off(rm_define.armor_all)    
            time.sleep(2)
            robot_turn(180)
            
            # now need to go back to the next reset point, skipping the marker point where the person was found
            return_dropoff_steps, return_dropoff_stops, return_dropoff_names, return_dropoff_distances = prepare_list_for_simplified_move(step, DIRECTION_FORWARD)
            print('**** Going BACK TO PICKUP POINT **** to index', step, ' ---> With', return_dropoff_steps, 'steps')
            print(return_dropoff_stops)
            print(return_dropoff_names)
            print(return_dropoff_distances)            

            # after dropoff, move back to the next reset point, this is a recursive function call!
            # move_forward_to_point being called from inside of itself
            move_forward_to_point(return_dropoff_steps-1, return_dropoff_stops, return_dropoff_names, return_dropoff_distances, False)

            # reset the flag that we got a person
            got_person = False
            already_going_back_to_stand = False
            

        # if we were at point F, it is allowed to do the reset again after doing some stuff with the chassis
        if reset_point and do_actions and (step_name == SIDEWAYS_TO_MARKER) and ((last_marker_name == MARKER_1) or (last_marker_name == MARKER_3)):
            print('* Reset again after marker scan after sideways for marker 1 or 2*')
            reset_point_procedure(step, step_name, reset_point)
        
        # increment distance traveled
        distance_accumulator += distance_to_move
        print(':: Step:',step,'(',step_name,') ended, distance accumulated so far:', distance_accumulator,'cm')
        
        last_marker_name = ""
        
# filling out the list of total distances to reach each stop point
def fill_distances(list_stops):
    result = []
    distance = 0
    for i in range(len(list_stops)):
        distance += list_stops[i]
        result.append(distance)
    return result

def start():
    global list_distances
    global marker_not_found

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
    print('== ROBOT PROGRAM START == PATH LENGTH: --->', list_distances[steps-1], 'cm')   
    
    wait_for_clap()
    
    # call move forward function to the last point H
    move_forward_to_point(steps-1)    
    
    # END MOVE FORWARD CYCLE
    all_done_on_the_way_home = True
 
    # START COMING BACK TO STAND
    robot_turn(180)
        
    # new list of distances to move back to the stand (reversed for the backward move)
    back_to_home_number_of_steps, back_to_home_stops, back_to_home_names, back_to_home_distances = prepare_list_for_simplified_move(steps-1, DIRECTION_BACKWARD)
    
    print('== ALL DONE, ON THE WAY HOME, number of steps:', back_to_home_number_of_steps)
    print(back_to_home_stops)
    print(back_to_home_names)
    
    # now point 'A' is the last point to reach
    # during the backward move, we do not need to stop at the marker points
    # the only action (robot dance) will be at the 'D' point
    move_forward_to_point(back_to_home_number_of_steps-1, back_to_home_stops, back_to_home_names, back_to_home_distances, False)
    
    robot_turn(180)
    reset_point_procedure(999, 'END')
    
    # ALL DONE
        
    return(0)    


# start the robot program    
#start()
