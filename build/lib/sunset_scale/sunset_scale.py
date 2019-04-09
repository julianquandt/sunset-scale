import pygame, csv, os, random, math, sys

scrInfo = pygame.display.Info()
#rgb-colors
black = (0,0,0)
white = (255,255,255)
green = (0,96,27)
red = (225,0,25)

def quitExp():
    quitDlg = gui.Dlg(title="Quit Experiment?")
    quitDlg.addText("Quit Experiment?")
    quitDlg.show()  # show dialog and wait for OK or Cancel
    if quitDlg.OK:
        pygame.quit()
        sys.exit()
    else:
       pass

def drawContinue(Screen, feedback, feedback_color):
    button_img = pygame.image.load("material//img//continue.png").convert_alpha()
    button_mouseover_img = pygame.image.load("material//img//continue_mouseover.png").convert_alpha()
    feedback_font = pygame.font.SysFont('Arial', 50)
    feedback_text = feedback_font.render(str(feedback), True, feedback_color)
    cont = False
    while not cont:
        Screen.fill(white)  # draw background
        Screen.blit(feedback_text,
                    (int(scrInfo.current_w / 2 - feedback_text.get_rect().size[0] / 2),
                     int(scrInfo.current_h / 2 - feedback_text.get_rect().size[1] / 2 - 200)))  # draw background
        button = Screen.blit(button_img, (int(scrInfo.current_w / 2 - button_img.get_size()[0] / 2),
                                          int(scrInfo.current_h / 2 - button_img.get_rect().size[1] / 2)))
        if button.collidepoint(pygame.mouse.get_pos()):
            button = Screen.blit(button_mouseover_img, (int(scrInfo.current_w / 2 - button_img.get_size()[0] / 2),
                                              int(scrInfo.current_h / 2 - button_img.get_size()[1] / 2)))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quitExp()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.collidepoint(pygame.mouse.get_pos()):
                    cont = True


def createRatingStimList(n_calibration, scale_anchors, stimulus, n_reps):
    # adding "calibration-trials" to the target-trials, i.e. numbers that need to be matched on the scale (optional)
    ran_values_set = [round(random.randint(scale_anchors[0], scale_anchors[1]-10),-1) for i in range(100)]
    ran_values_set = [int(i) for i in ran_values_set]
    one_block_trialList = list(set(ran_values_set)) # for some reason this is ordered so needs to be shuffled first
    random.shuffle(one_block_trialList)
    one_block_trialList = one_block_trialList[0:3]
    one_block_trialList.append(stimulus)
    trialList = []
    for i in range(n_reps):
        random.shuffle(one_block_trialList)
        trialList = trialList + one_block_trialList

    return(trialList)


def drawTicks(Screen, n_ticks, arc_init_x, arc_init_y, r, tickFont, scale_anchors, label_list):
    # drawing the tick-marks alongside the scale (if needed)

    # win.blit(tempMark, (arc_init_x-r, arc_init_y))
    r = r + 50 # get the radius of the scale and increase it by 50 to draw numbers outside of the scale
    n_ticks = n_ticks-1 # this is necessary to draw the tick-marks at the right position (i.e. including the highest)
                        # without changing their positions

    if not label_list == None: # check whether there is a label-list indicating that it is a likert-like scale
        n_ticks = len(label_list)-1 # automatically adjust number of ticks to match length of likert-scale

    for i_tick in range(0,n_ticks+1): # draw the ticks
        if i_tick > 0:
            angle = 180.0/n_ticks*i_tick
        else:
            angle = 0 # position for first tick-mark at 0

        if label_list == None: # draw numbers if no label-list is provided otherwise draw label at that position
            rating = int(round((angle * ((scale_anchors[1] - scale_anchors[0]) / 180.0)), 0))
        else:
            rating = label_list[i_tick]
        tempMark = tickFont.render(str(rating), True, (0, 0, 0))

        # set position of the tickmark
        x_tick = int(int(arc_init_x) + r * math.cos(math.radians(180.0 - angle)))
        if i_tick > 0 and i_tick == n_ticks/2: # center x-pos of item if it is in the middle of the scale
            x_tick = x_tick - tempMark.get_rect().size[0]/2
        elif (i_tick > 0 and i_tick < (n_ticks + 1) * 0.5) or i_tick == n_ticks: # and adjust x-pos items on the right side
            x_tick = x_tick - tempMark.get_rect().size[0]
        y_tick = int(int(arc_init_y) - r * math.sin(math.radians(180.0 - angle)))

        Screen.blit(tempMark, (x_tick, y_tick))
#TODO: optimize this by drawing instead of blitting https://stackoverflow.com/questions/35964370/pygame-blitting-many-images-lags-game

def getDistance(df_name_mouse, pp_info, trial_number, stimulus, scale_x, scale_y, mouse_x, mouse_y, rt,
                started_trial, r, **kwargs):
    # calculating the distance from the scale-midpoint/starting-point to the current mouse-position

    x_distance = mouse_x - scale_x #distance of x-values
    y_distance = mouse_y - scale_y #distance of y-values
    distance = math.sqrt(math.pow(x_distance, 2) + math.pow(y_distance, 2))

    if started_trial: # start saving mouse tracking data as soon as the trial is started (i.e. if box is green)
        saveMouseTrackingData(df_name_mouse, pp_info, trial_number, stimulus, mouse_x, mouse_y,
                              r - distance, rt, **kwargs)

    return(distance) #return distance: length of vector sqrt(a^2+b^2)


def saveMouseTrackingData(df_name_rating, pp_info, trial_number, stimulus, mouse_x, mouse_y, distance, rt, **kwargs):
    # saving mouse tracking data (called each iteration)
    if len(kwargs) > 0:
        added_vars = kwargs
    else:
        added_vars = None

    if not os.path.isfile(df_name_rating):
        with open(df_name_rating, "a") as dbf:
            wr = csv.writer(dbf, delimiter=',', lineterminator='\r')
            row_names = ["ppid", 'trial_number', "stimulus", "mouse_x", "mouse_y", "distance", "rt"]
            if added_vars:
                row_names = row_names + [added_vars['added_vars'][i][0] for i in range(len(added_vars['added_vars']))]
            wr.writerow(row_names)

    with open(df_name_rating, "a") as dbf:
        wr = csv.writer(dbf, delimiter=',',lineterminator='\r')
        row = [pp_info['subjectID'], trial_number, stimulus, mouse_x, mouse_y, distance, rt]
        if added_vars:
            row = row + [added_vars['added_vars'][i][1] for i in range(len(added_vars['added_vars']))]
        wr.writerow(row)


def saveRatingData(df_name, pp_info, trial_number, stimulus,rating, rating_ord, rt, ndc, **kwargs):
    # saving the rating data at the end of each trial
    if len(kwargs) > 0:
        added_vars = kwargs
    else:
        added_vars = None

    if not  os.path.isfile(df_name):
        with open(df_name, "a") as rdf:
            wr = csv.writer(rdf, delimiter=',', lineterminator='\r')
            row_names = ['ppid', 'trial_number', 'stimulus', 'rating', 'ordinal_rating', 'rt', 'non_dec_time']
            if added_vars:
                row_names = row_names + [added_vars['added_vars'][i][0] for i in range(len(added_vars['added_vars']))]
            wr.writerow(row_names)


    with open(df_name, "a") as rdf:
        wr = csv.writer(rdf, delimiter=',',lineterminator='\r')
        row = [pp_info['subjectID'], trial_number, stimulus, rating, rating_ord, rt, ndc]
        if added_vars:
            row = row + [added_vars['added_vars'][i][1] for i in range(len(added_vars['added_vars']))]
        wr.writerow(row)


#TODO: add obligatory trajectory for the beginning of the trial to make it easier to analyze movements?
def ratingTrial(df_name_rating, df_name_mouse, pp_info, Screen, stimulus, r_scale=0.8, pos=(0, 0),
                show_stim="no_move_hide", scale_anchors=(0, 200), n_ticks=2, trial_number=0, scale=True,
                label_list=None, instr_reminder=" ", scale_color="blue", tick_size=20,
                time_line="pre", delay_time = 500, max_duration = 0, **kwargs):
    '''
    :param df_name_rating:  STR:    a file name or file-location in which the ratings should be stored
    :param df_name_mouse:   STR:    a file name for the mouse-tracking data
    :param pp_info:         DICT:   a dictionary containing the participant identifier at key subject_number
    :param Screen:          PG:     a pygame window object
    :param stimulus:        STR:    file name or location to a picture that should be rated
    :param r_scale:         FLOAT:  scale-size relative to screen size (default 0.8) # TODO: FIX THIS
    :param pos:             TUPLE:  (X,Y) an offset of the scale if it needs to be shifted TODO: fix this
    :param show_stim:       STR:    "always", "delayed", "no_move_hide"; mode in which the picture is presented
    :param scale_anchors:   TUPLE:  (min,max) minimum and maximum of scale
    :param n_ticks:         INT:    how many tick-marks should be displayed along the scale
    :param trial_number:    INT:    a trial number passed to the data-saving functions (is updated and returned here)
    :param scale:           BOOL:   should presented pictures be scaled down to 600*X pixels?
    :param label_list:      LIST:   custom ticks (e.g. words) can be passed if needed instead of numbers
    :param instr_reminder:  STR:    a text that should be displayed above the scale as a reminder to participants
    :param scale_color:     STR:    "red_green", "green", "blue"; the color of the scale
    :param tick_size:       INT:    font-size of tick-marks in pixels
    :param time_line:       STR:    an identifier of measurement timepoint that will be passed to data saving
    :param delay_time:      INT:    if the show_stim mode "delayed" is used, how long should the delay be?
    :return:                        trial_number, stimulus_type, rating, non_dec_time
    '''

    r = int(scrInfo.current_h*r_scale) # the radius of the scale (only for the calculations not optical)
    arc_init_x = int(scrInfo.current_w/2)+int(pos[0]) # x-value of circle midpoint/scale-starting point (half the winwidth by default)
    arc_init_y = int(scrInfo.current_h*0.9)+int(pos[1]) # y-value of the starting-point: 90 percent to the bottom of the win

    if scale_color == "red_green":
        scale_img = pygame.image.load("material//img//arc_scale_regular.png").convert_alpha() # load the visual scale image #TODO: make this scalable
    elif scale_color == "green":
        scale_img = pygame.image.load("material//img//arc_scale_green.png").convert_alpha() # load the visual scale image #TODO: make this scalable
    else:
        scale_img = pygame.image.load("material//img//arc_scale_blue.png").convert_alpha() # load the visual scale image #TODO: make this scalable

    tick_font = pygame.font.SysFont('Arial', tick_size, bold=True)
    stim_number_font = pygame.font.SysFont('Arial', 120, bold = True)
    instr_reminder_font = pygame.font.SysFont('Arial', 50)
    instr_reminder_text = instr_reminder_font.render(str(instr_reminder), True, (0,0,0))

    n_ticks = n_ticks

    stim_name = str(stimulus)
    trial_number += 1


    stimulus_img = pygame.image.load(stimulus).convert_alpha()  # load the current stimulus-image from disk
    # display stimulus in the middle of the win
    if scale == True:
        if stimulus_img.get_rect().size[0] > 600:
            stimulus_img = pygame.transform.scale(stimulus_img,
                                                  (600, int(stimulus_img.get_rect().size[1]*(600.0/stimulus_img.get_rect().size[0]))))
    stim_x = int(scrInfo.current_w/2-stimulus_img.get_rect().size[0]/2) # x-value of image display (upper left corner)
    stim_y = int(scrInfo.current_h/2-stimulus_img.get_rect().size[1]/2) # y-value

    #initiate other variables
    rect_size = 20 # size of the starting-point box
    last_time = 0  # event-timer (counting time since last event occured for hiding the image when the mouse it not moved for X ms)
    rt = pygame.time.get_ticks() # reaction time (just in case people respond too fast)
    ndc_init = 0 # non-decision time initial value
    box_time_init = 0 # time that people spend in the starting box (for the delayed trials)
    box_time = 0
    reset_box_time = True
    reset_rt = True # should the rt-counter be reset?
    reset_ndc = True # should the non-decision-time counter be reset?
    started_trial = False # has the trial started?
    inside_box = False # is the mouse inside the starting-box?
    count_ndc = True # count non-decision-time?
    trial_end = False # variable for loop initiation
    box_color = red
    reset_trial_duration = True
    non_dec_time = 0

    while not trial_end: # while the arc is not crossed, i.e. no rating is given

        #loop_test_time = pygame.time.get_ticks()
        if not inside_box:
            box_time_init = pygame.time.get_ticks()

        if not started_trial:  # if trial has not been started (i.e. when mouse has not been moved to starting box after the last trial)
            Screen.fill(white)  # draw background
            if not show_stim == "delayed":
                Screen.blit(instr_reminder_text,
                            (int(scrInfo.current_w / 2 - instr_reminder_text.get_rect().size[0] / 2), 0))  # draw background
            Screen.fill(box_color, [arc_init_x - rect_size / 2, arc_init_y - rect_size / 2, rect_size,
                                    rect_size])  # draw red starting-box

            if show_stim == "delayed":
                if inside_box:
                    box_time = pygame.time.get_ticks()
                    box_color = green
                    Screen.blit(scale_img, (0, 0))  # draw scale
                    if n_ticks > 0:
                        drawTicks(Screen, n_ticks, arc_init_x, arc_init_y, r, tick_font, scale_anchors, label_list)
                else:
                    box_color = red

                if box_time - box_time_init > delay_time:
                    started_trial = True

        if started_trial: # if the trial has already started (i.e. mouse in starting box)
            if reset_trial_duration:
                trial_start_time = pygame.time.get_ticks()
                reset_trial_duration = False

            box_color = green

            time_diff = pygame.time.get_ticks() - last_time # calculate time since last mouse movement

            Screen.fill(white) # draw background
            Screen.blit(instr_reminder_text, (int(scrInfo.current_w/2-instr_reminder_text.get_rect().size[0]/2), 0)) # draw background
            Screen.blit(scale_img, (0, 0)) # draw scale
            Screen.fill(box_color, [arc_init_x-rect_size/2, arc_init_y-rect_size/2, rect_size, rect_size]) # change starting-box color to green
            if n_ticks > 0:
                drawTicks(Screen, n_ticks, arc_init_x, arc_init_y, r, tick_font, scale_anchors, label_list)

            if reset_ndc: # reset non-decision time on the beginning of every trial
                ndc_init = pygame.time.get_ticks() # initial non-decision time (i.e. when mouse moves to box in beginning of trial)
                reset_ndc = False # do not reset ndc anymore in this trial

            if show_stim == "always" or show_stim == "delayed":
                Screen.blit(stimulus_img, (stim_x, stim_y))  # draw the stimulus
                Screen.blit(instr_reminder_text,
                            (int(scrInfo.current_w / 2 - instr_reminder_text.get_rect().size[0] / 2),
                             0))  # draw background
                if reset_rt:  # if the rt should be reset
                    rt = pygame.time.get_ticks()  # reset it
                    reset_rt = False  # and do not reset it anymore this trial
            else:
                if show_stim == "no_move_hide":
                    #box_color = green
                    if time_diff < 140 and not inside_box: # if the mouse was moved in the last X ms and is not inside the starting box TODO: optimize this
                        Screen.blit(stimulus_img, (stim_x, stim_y)) #draw the stimulus
                else:
                    if not inside_box: # if the mouse was moved in the last X ms and is not inside the starting box TODO: optimize this
                        Screen.blit(stimulus_img, (stim_x, stim_y)) #draw the stimulus
                if reset_rt: # if the rt should be reset
                    rt = pygame.time.get_ticks() # reset reaction time here too as the picture needs to be visible first (this makes it more accurate)
                    reset_rt = False # and do not reset it anymore this trial

            pygame.display.update() # draw all stimuli to Screen

        ### now everything is on the screen [either before or after trial-start], check for what is going on ###

        for event in pygame.event.get(): # check whether an event occured
            #ask whether experiment should be quit when ESCAPE is pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quitExp()

        if show_stim == "no_move_hide":
            last_time = pygame.time.get_ticks() # reset event-timer for

        mt = pygame.time.get_ticks() - rt # save movement time

        mouse_x = pygame.mouse.get_pos()[0] # get current mouse position x-value
        mouse_y = pygame.mouse.get_pos()[1] # get current mouse position y-value

        if reset_rt:  # reset the RT here when the mouse is moved for the first time per trial to get initial RTs before picture is visible
            rt = pygame.time.get_ticks()

        # print([mouse_x, mouse_y])
        distance = getDistance(df_name_mouse, pp_info, trial_number, stim_name, arc_init_x,
                              arc_init_y, mouse_x, mouse_y, mt, started_trial,
                              r, **kwargs)  # call getDistance to check whether rating is given
        # check whether mouse is in starting-box
        if mouse_x >= arc_init_x - rect_size / 2 and mouse_x <= arc_init_x + rect_size / 2:
            if mouse_y >= arc_init_y - rect_size / 2 and mouse_y <= arc_init_y + rect_size / 2:
                inside_box = True # mouse is in starting-box
        else:
            inside_box = False # mouse is not in starting-box

        if not started_trial and inside_box and not show_stim == "delayed": # if trial has not started but mouse is inside the box
            started_trial = True  # start trial
            Screen.fill(box_color,
                        [arc_init_x - rect_size / 2, arc_init_y - rect_size / 2, rect_size, rect_size]) #draw green box

        pygame.display.update() #update Screen
           # time.sleep(0.2) # wait 0.2 seconds for user experience

        if started_trial: # if the trial has started

            if not inside_box and count_ndc: # if mouse is not in the box and the non-decison-time is still counting
                non_dec_time = pygame.time.get_ticks()-ndc_init # calculate ndc (time that mouse was in the box)
                count_ndc = False # stop counting non-decision-time in this trial
            # print(pygame.time.get_ticks() - loop_test_time)
            if distance >= r and mouse_y < arc_init_y: # if a decision is made
                dt = pygame.time.get_ticks()-rt # save reaction time (time since picture presentation (after ndc)


                angle = 180-(math.degrees(math.atan2(-(mouse_y-arc_init_y), (mouse_x-arc_init_x)))) # calculate angle between
                    # the x-axis and the vector from scale-starting point to crossing-point
                rating = round((angle*((scale_anchors[1]-scale_anchors[0])/180.0)), 0) # calculate value on the rating-scale
                if label_list:
                    divis = (scale_anchors[1]-scale_anchors[0])/float(len(label_list)-1) # label-list -1 because of half-intervals at scale ends
                    rating_ord = round(rating/float(divis),0)
                else:
                    rating_ord = rating

                dt = dt-non_dec_time
                # print(non_dec_time)
                # print(dt)
                saveRatingData(df_name_rating, pp_info, trial_number, stim_name, rating, rating_ord, dt,
                               non_dec_time, **kwargs)
                trial_end = True
            if max_duration > 0:
                if pygame.time.get_ticks() - trial_start_time > max_duration:
                    non_dec_time = -999
                    rating = -999
                    rating_ord = -999
                    dt = -999
                    saveRatingData(df_name_rating, pp_info, trial_number, stim_name, rating, rating_ord, dt,
                                   non_dec_time, **kwargs)
                    trial_end = True
    return trial_number, rating, non_dec_time, inside_box, kwargs
