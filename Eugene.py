variable_marker_not_found = True
variable_got_person = False
list_stops = [ 0, 550, 20+15+5+35+10+42+96+51+33, 665+32, 458+50, 371+38, 419+58, 398+40, 569+10 ]
list_back_stops = [ 0, 569+398+58, 419+38+371+50, 458+32+665, 341+585+30 ]
list_stops1 = [ 0, 46, 30, 51+23, 32+23, 43+24, 53+22, 75+24, 47+30 ]
list_resets = [ True, False, True, False, True, False, True, False, True ]
list_markers = [ False, False, False, True, False, True, True, True, True ]
list_move_back = [ 0, 0, 0, 0, 0 ]
list_move_back_adj = [ 0, 0, 0, 0, 0 ]
list_move_forward_adj = [ 0, 0, 0, 0, 0 ]
list_small_distances = []
list_distances = []
variable_distance_counter = 0
variable_total_distance = 0

def fill_distances(total_distance, divisor=490):
    list_result = []
    while total_distance >= divisor:
        list_result.append(divisor)
        total_distance = total_distance - divisor
    if total_distance >= 0:
        list_result.append(total_distance)
    return list_result    
    
def do_zigzag(multiplier=1.0, time_to_sleep=0.5):
    chassis_ctrl.move_with_distance(0, 0.35*multiplier)
    chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90-3.5)
    chassis_ctrl.move_with_distance(0, 0.845*multiplier)
    chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90-3.5)
    chassis_ctrl.move_with_distance(0, 0.35*multiplier)
    chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90-3.5)
    chassis_ctrl.move_with_distance(0, 1.64*multiplier)
    chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90-3.5)
    chassis_ctrl.move_with_distance(0, 0.42*multiplier)
    chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
    chassis_ctrl.move_with_distance(0, 0.60*multiplier)
    chassis_ctrl.rotate_with_degree(rm_define.clockwise, 39.6)
    chassis_ctrl.move_with_distance(0, 1.48*multiplier)
    chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90-39.6)
    chassis_ctrl.move_with_distance(0, 0.51*multiplier)
    chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)
    chassis_ctrl.move_with_distance(0, 0.84*multiplier)
    chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
    chassis_ctrl.move_with_distance(0, 0.33*multiplier)
    time.sleep(time_to_sleep)
    
def move_closer(distance, multiplier, sideways=True):
    if sideways:
        chassis_ctrl.move_with_distance(-90, distance*multiplier)
    else: 
        chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
        chassis_ctrl.move_with_distance(0, distance*multiplier)

def move_away(distance, multiplier, sideways=True):
    if sideways:
        chassis_ctrl.move_with_distance(90, distance*multiplier)
    else:
        chassis_ctrl.move_with_distance(180, distance*multiplier)
        chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)
        
        
def scan_for_marker(sideways=False):
    global variable_marker_not_found
    
    gimbal_ctrl.recenter()
    #media_ctrl.play_sound(rm_define.media_sound_attacked)
    
    if sideways:
        yaw_add = -90
    else:
        yaw_add = 0
    
    #led_ctrl.set_flash(rm_define.armor_all, 2)

    gimbal_ctrl.yaw_ctrl(-90+yaw_add)
    gimbal_ctrl.yaw_ctrl(90+yaw_add)
    vision_ctrl.enable_detection(rm_define.vision_detection_marker)
    
    while (variable_marker_not_found):
        if variable_marker_not_found: gimbal_ctrl.yaw_ctrl(-90)
        if variable_marker_not_found: gimbal_ctrl.yaw_ctrl(90)
    
    #time.sleep(5)
    #gimbal_ctrl.recenter()
    variable_marker_not_found = True
    
    
   # move_away(distance, multiplier, sideways)
    
def vision_recognized_marker_letter_F(msg):
    global variable_marker_not_found
    variable_marker_not_found = False
    led_ctrl.gun_led_on()
    led_ctrl.set_top_led(rm_define.armor_top_all, 69, 215, 255, rm_define.effect_always_on)
    led_ctrl.set_flash(rm_define.armor_all, 2)
    media_ctrl.play_sound(rm_define.media_sound_recognize_success)
    vision_ctrl.detect_marker_and_aim(rm_define.marker_letter_F)
    
    gun_ctrl.fire_once()
    
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)
    time.sleep(3)
    led_ctrl.turn_off(rm_define.armor_all)
    led_ctrl.gun_led_off()
    gimbal_ctrl.recenter()
        
    time.sleep(20)
       
    
def vision_recognized_marker_letter_P(msg):
    global variable_marker_not_found
    global variable_got_person
    variable_marker_not_found = False
    variable_got_person = True
    gimbal_ctrl.recenter()
    led_ctrl.gun_led_on()
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 193, 0, rm_define.effect_flash)
    #led_ctrl.turn_off(rm_define.armor_all)
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 193, 0, rm_define.effect_flash)
    #led_ctrl.set_single_led(rm_define.armor_top_all, [1,2,3,4,5,6,7,8], rm_define.effect_always_on)
    
    
    #led_ctrl.set_top_led(rm_define.armor_top_all, , rm_define.effect_always_on)
    #led_ctrl.set_flash(rm_define.armor_all, 2)
    media_ctrl.play_sound(rm_define.media_sound_scanning)
    vision_ctrl.detect_marker_and_aim(rm_define.marker_letter_P)
    
    #gun_ctrl.fire_once()
    
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)
    gimbal_ctrl.rotate_with_degree(rm_define.gimbal_up, 30)
    
    time.sleep(20)
    #led_ctrl.turn_off(rm_define.armor_all)
    led_ctrl.gun_led_off()
    gimbal_ctrl.recenter()
        
    time.sleep(3)    
    
def vision_recognized_marker_letter_D(msg):
    global variable_marker_not_found
    variable_marker_not_found = False
    gimbal_ctrl.recenter()
    #led_ctrl.gun_led_on()
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_breath)
    #led_ctrl.turn_off(rm_define.armor_all)
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_breath)
    #led_ctrl.set_single_led(rm_define.armor_top_all, [1,2,3,4,5,6,7,8], rm_define.effect_always_on)
    
    
    #led_ctrl.set_top_led(rm_define.armor_top_all, , rm_define.effect_always_on)
    #led_ctrl.set_flash(rm_define.armor_all, 2)
    media_ctrl.play_sound(rm_define.media_sound_attacked)
    #vision_ctrl.detect_marker_and_aim(rm_define.marker_letter_D)
    
    #gun_ctrl.fire_once()
    
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)
    gimbal_ctrl.rotate_with_degree(rm_define.gimbal_down, 20)
    
    time.sleep(20)
    #led_ctrl.turn_off(rm_define.armor_all)
    #led_ctrl.gun_led_off()
    gimbal_ctrl.recenter()
        
    time.sleep(3)    
    
def vision_recognized_marker_number_one(msg):
    global variable_marker_not_found
    variable_marker_not_found = False
    gimbal_ctrl.recenter()
    #led_ctrl.gun_led_on()
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_breath)
    #led_ctrl.turn_off(rm_define.armor_all)
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_breath)
    #led_ctrl.set_single_led(rm_define.armor_top_all, [1,2,3,4,5,6,7,8], rm_define.effect_always_on)
    
    
    #led_ctrl.set_top_led(rm_define.armor_top_all, , rm_define.effect_always_on)
    #led_ctrl.set_flash(rm_define.armor_all, 2)
    media_ctrl.play_sound(rm_define.media_sound_attacked)
    #vision_ctrl.detect_marker_and_aim(rm_define.marker_letter_D)
    
    #gun_ctrl.fire_once()
    
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)
    #gimbal_ctrl.rotate_with_degree(rm_define.gimbal_down, 20)
    
    time.sleep(20)
    #led_ctrl.turn_off(rm_define.armor_all)
    #led_ctrl.gun_led_off()
    gimbal_ctrl.recenter()
        
    time.sleep(3)    
    
def vision_recognized_marker_number_one(msg):
    global variable_marker_not_found
    variable_marker_not_found = False
    gimbal_ctrl.recenter()
    #led_ctrl.gun_led_on()
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_breath)
    #led_ctrl.turn_off(rm_define.armor_all)
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_breath)
    #led_ctrl.set_single_led(rm_define.armor_top_all, [1,2,3,4,5,6,7,8], rm_define.effect_always_on)
    
    
    #led_ctrl.set_top_led(rm_define.armor_top_all, , rm_define.effect_always_on)
    #led_ctrl.set_flash(rm_define.armor_all, 2)
    media_ctrl.play_sound(rm_define.media_sound_attacked)
    #vision_ctrl.detect_marker_and_aim(rm_define.marker_letter_D)
    
    #gun_ctrl.fire_once()
    
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)
    #gimbal_ctrl.rotate_with_degree(rm_define.gimbal_down, 20)
    
    time.sleep(20)
    #led_ctrl.turn_off(rm_define.armor_all)
    #led_ctrl.gun_led_off()
    gimbal_ctrl.recenter()
        
    time.sleep(3)        

def vision_recognized_marker_number_two(msg):
    global variable_marker_not_found
    variable_marker_not_found = False
    gimbal_ctrl.recenter()
    #led_ctrl.gun_led_on()
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_breath)
    #led_ctrl.turn_off(rm_define.armor_all)
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_breath)
    #led_ctrl.set_single_led(rm_define.armor_top_all, [1,2,3,4,5,6,7,8], rm_define.effect_always_on)
    
    
    #led_ctrl.set_top_led(rm_define.armor_top_all, , rm_define.effect_always_on)
    #led_ctrl.set_flash(rm_define.armor_all, 2)
    media_ctrl.play_sound(rm_define.media_sound_attacked)
    #vision_ctrl.detect_marker_and_aim(rm_define.marker_letter_D)
    
    #gun_ctrl.fire_once()
    
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)
    #gimbal_ctrl.rotate_with_degree(rm_define.gimbal_down, 20)
    
    time.sleep(20)
    #led_ctrl.turn_off(rm_define.armor_all)
    #led_ctrl.gun_led_off()
    gimbal_ctrl.recenter()
        
    time.sleep(3)    
        
def vision_recognized_marker_number_three(msg):
    global variable_marker_not_found
    variable_marker_not_found = False
    gimbal_ctrl.recenter()
    #led_ctrl.gun_led_on()
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_breath)
    #led_ctrl.turn_off(rm_define.armor_all)
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_breath)
    #led_ctrl.set_single_led(rm_define.armor_top_all, [1,2,3,4,5,6,7,8], rm_define.effect_always_on)
    
    
    #led_ctrl.set_top_led(rm_define.armor_top_all, , rm_define.effect_always_on)
    #led_ctrl.set_flash(rm_define.armor_all, 2)
    media_ctrl.play_sound(rm_define.media_sound_attacked)
    #vision_ctrl.detect_marker_and_aim(rm_define.marker_letter_D)
    
    #gun_ctrl.fire_once()
    
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)
    #gimbal_ctrl.rotate_with_degree(rm_define.gimbal_down, 20)
    
    time.sleep(20)
    #led_ctrl.turn_off(rm_define.armor_all)
    #led_ctrl.gun_led_off()
    gimbal_ctrl.recenter()
        
    time.sleep(3)        
    
def goto_a(distance, curr_step):
    global list_distances
    global list_resets
    
    if curr_step == len(list_distances): do_d_dance = True
    else: do_d_dance = False
    
    down_distances = []
    down_resets = []
        
    for i in range(curr_step):
        if list_resets[i]:
          down_distances.append(list_distances[i])
    down_distances.append(list_distances[curr_step])
    print(down_distances)
    
    for i in range(len(down_distances)-1):
        down_distances[i+1] = down_distances[i+1]-down_distances[i]
    print(down_distances)
    
    down_distances_rev = down_distances[::-1]
    print(down_distances_rev)
    
    steps = len(down_distances)
    for step in range(steps):
    
        distance_to_move = down_distances_rev[step]
        #variable_distance_counter = variable_distance_counter + distance_to_move
        print('Current Step:',step,'-> Distance:', distance_to_move,'cm')
        small_distances = []
        small_distances = fill_distances(distance_to_move)
        print(small_distances)
        for i in range(int(len(small_distances))):
            dist_cm = list_small_distances[i]
            print(dist_cm, "-small distance-", i)
            chassis_ctrl.move_with_distance(0, float(float(dist_cm))/100.0) 
        
        print('step',step,'- reset point')
        led_ctrl.set_flash(rm_define.armor_all, 2)
        #if step == len(down_distances):
                #chassis_ctrl.rotate_with_degree(rm_define.clockwise, 180)
        time.sleep(5)
        led_ctrl.turn_off(rm_define.armor_all)
        
        
#def go_from_a(distance, curr_step):
 #   pass
    
def goto_a_and_back(distance, curr_step):
    global list_distances
    print(list_distances)
    print(list_distances[curr_step], len(list_distances))
    for i in range(len(list_distances)):
        print(i,' ---', list_distances[i])
    print('distance to travel back:', distance, ' CURRENT STEP:', curr_step, ':', list_distances[curr_step])
    goto_a(distance, curr_step)
    
    

def start():
    global list_stops
    global list_resets
    global list_distances
    global list_move_back
    global variable_marker_not_found
    global variable_distance_counter
    global variable_total_distance
    
        
    multiplier=1.0
    time_to_sleep=0.0
    
    robot_ctrl.set_mode(rm_define.robot_mode_free)
    chassis_ctrl.set_trans_speed(0.5) 
    chassis_ctrl.set_rotate_speed(30)
    gimbal_ctrl.set_rotate_speed(60)
    vision_ctrl.disable_detection(rm_define.vision_detection_marker)
    led_ctrl.turn_off(rm_define.armor_all)
    
    #chassis_ctrl.move_with_distance(0, 0.585*multiplier)
    time.sleep(time_to_sleep)
    #do_zigzag(multiplier, time_to_sleep)
    gimbal_ctrl.recenter()
    time.sleep(1)
    
    #chassis_ctrl.move_with_distance(0, 0.3)
    #scan_for_marker(0.5, multiplier, False)
    #chassis_ctrl.move_with_distance(180, 0.3)
    
    # gimbal_ctrl.yaw_ctrl(250)
    
    variable_distance_counter = 0
    steps = int(len(list_stops))
    for step in range(steps):
        variable_distance_counter = variable_distance_counter + list_stops[step]
        list_distances.append(variable_distance_counter)
        #time.sleep(1)
        print(step, ' - ',variable_distance_counter)
        
    print(list_distances)    
    variable_total_distance = variable_distance_counter 
        
    variable_distance_counter = 0
    
    resets_index = 0
    reset_distance = 0
    for step in range(steps):
        #led_ctrl.set_flash(rm_define.armor_all, 2)
        
        distance_to_move = list_stops[step]
        
#        reset_distance += distance_to_move
#        if list_resets[step]:
#            list_move_back.append(reset_distance)
#            resets_index += 1
#            reset_distance = 0
            
        print('resets number', resets_index-1, '-----', list_move_back)    
        
        
        #distance_to_move = list_stops[step]
        variable_distance_counter = variable_distance_counter + distance_to_move
        print('Current Step:',step,'-> Distance:', distance_to_move,'cm')
        list_small_distances = []
        list_small_distances = fill_distances(distance_to_move)
        if step == 2:
            do_zigzag(1.0, 1)
            print('do zigzag')
        else:    
            print('move straight')
            print(list_small_distances)
            number_of_distance_steps = len(list_small_distances)
            print('will be total of', number_of_distance_steps,'steps')
            for step_no in range(number_of_distance_steps):
                dist_cm = list_small_distances[step_no]
                print(dist_cm, "-small distance-", step_no, 'of', number_of_distance_steps)
                chassis_ctrl.move_with_distance(0, float(float(dist_cm))/100.0) 

        # check if reset point
        if list_resets[step]:
            print('step',step,'- reset point')
            led_ctrl.set_flash(rm_define.armor_all, 2)
            #if step == len(list_distances):
                #chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 180)
            time.sleep(5)
            led_ctrl.turn_off(rm_define.armor_all)
        else:
            print('step',step,'- regular point')
            time.sleep(5)
            
            
            
        if list_markers[step]:           
            if step == 6:
                chassis_ctrl.move_with_distance(-90, 0.7*multiplier)
                sideways = True
            else:
                chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
                chassis_ctrl.move_with_distance(0, 0.5*multiplier)
                sideways = False
                
            scan_for_marker(sideways)
            
            if step == 6:
                chassis_ctrl.move_with_distance(90, 0.7*multiplier)
            else:
                chassis_ctrl.move_with_distance(180, 0.5*multiplier)
                if variable_got_person:
                    chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
                else:
                    chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)
        
#        variable_got_person = True  
#        if step == 3:
#            goto_a_and_back(variable_distance_counter,step)
#            variable_got_person = False
#            break
#            
        
        
                  
                 
            
            
            
        #led_ctrl.turn_off(rm_define.armor_all)
        #time.sleep(5)
        
        
        
    
        
    
    