import math as m
import time

from resolution import eval_, ramap
from tcasClass import *


class Dispvar:
    def __init__(self):
        """Group cor_prev"""
        self.goalcl = None #Own goal climb rate
        self.goaldes = None #Own goal descent rate
        self.raind = None #Strength of RA issued against a threat
        self.success = None #Set if any ITF.INCREASE flag is TRUE

        """Group crossing_RA"""
        self.proj_zint = None #Projected altitude of intruder at CPA

        """Group annunciation"""
        self.anyaltlost = None #Threat became non-altitude-reporting during RA
        self.anytrackdrop = None #Surveillance dropped track during RA

        """Group output"""
        self.aid = np.full(13, False, dtype=bool) #Mode A identity code
        self.ara = np.full(14, False, dtype=bool) #active RA
        self.cac = np.full(13, False, dtype=bool) #Mode C altitude code
        self.rac = np.full(4, False, dtype=bool) #RA complement
        self.mte = None #Multiple threat encounter


"""VALID"""
def determine_goal_rate(tf, g, p, dispvar):
    if(tf.permtent[6] == False):
        dispvar.goalcl = max(dispvar.goalcl, p.climbgoal[dispvar.raind])
        if(dispvar.raind == 8):
            if(g.clstrold < 8 or g.anynewthr == True):
                g.zdmodel = max(max(dispvar.goalcl, min(g.zdown, p.maxdrate)), g.zdmodel)
                if(g.anynewthr == True and g.zdmodel > p.inc_clmrate):
                    g.anyincrease = False
            dispvar.goalcl = max(dispvar.goalcl, g.zdmodel)
    else:
        dispvar.goaldes = min(dispvar.goaldes, p.desgoal[dispvar.raind])
        if(dispvar.raind == 8):
            if(g.destrold < 8 or g.anynewthr == True):
                g.zdmodel = min(min(dispvar.goaldes, max(g.zdown, p.mindrate)), g.zdmodel)
                if(g.anynewthr == True and g.zdmodel < p.inc_desrate):
                    g.anyincrease = False
            dispvar.goaldes = min(dispvar.goaldes, g.zdmodel)
"""VALID"""


"""VALID"""
def set_up_goal_rate(TF, g, p, dispvar):
    dispvar.goalcl = -p.huge
    dispvar.goaldes = p.huge
    for tf in TF:
        if(tf.iptr != None):
            dispvar.raind = eval_(tf.permtent)
            if(tf.iptr.increase_pending == False and tf.iptr.retention == False):
                if(dispvar.raind != 0):
                    determine_goal_rate(tf, g, p, dispvar)
    dispvar.success = False
    if(g.anyincrease == True):
        for tf in TF:
            if(dispvar.success != False):
                break
            if(tf.iptr.increase == True):
                dispvar.success = True
        if(dispvar.success == False):
            g.anyincrease = False
"""VALID"""


"""VALID"""
def corrective_preventive_test(g, p, dispvar):
    if(g.corrective_clm == True and g.clstrong < g.clstrold and ((m.fabs(dispvar.goalcl) > 1e-10 and g.zdown > dispvar.goalcl) or (m.fabs(dispvar.goalcl) < 1e-10 and g.zdown > -p.hystercor))):
        g.corrective_clm = False
    else:
        if(g.corrective_des == True and g.destrong < g.destrold and ((m.fabs(dispvar.goaldes) > 1e-10 and g.zdown < dispvar.goaldes) or (m.fabs(dispvar.goaldes) < 1e-10 and g.zdown < p.hystercor))):
            g.corrective_des = False
    if(g.corrective_clm == False and min(g.zdown, p.maxdrate) <= dispvar.goalcl):
        if((m.fabs(dispvar.goalcl) > 1e-10) or (m.fabs(dispvar.goalcl) < 1e-10 and g.zdown < -p.hystercor)):
            g.corrective_clm, g.anyprecor = True, True
            g.corrective_des = False
    else:
        if(g.corrective_des == False and max(g.zdown, p.mindrate) >= dispvar.goaldes):
            if((m.fabs(dispvar.goaldes) > 1e-10) or (m.fabs(dispvar.goaldes) < 1e-10 and g.zdown > p.hystercor)):
                g.corrective_des, g.anyprecor = True, True
                g.corrective_clm = False
"""VALID"""


"""VALID"""
def crossing_flag_check(itf, g, p, dispvar):
    if(itf.tacode == RA and itf.tptr != None and itf.trtru >= p.min_ri_time):
        if((itf.tptr.permtent[6] == False and itf.rz <= -p.crossthr) or (itf.tptr.permtent[6] == True and itf.rz >= p.crossthr)):
            if(itf.int_cross == False and itf.own_cross == False):
                if(itf.tptr.permtent[4] == False and itf.tptr.permtent[5] == False and itf.increase_pending == False and itf.retention == False):
                    g.anycross = True
                dispvar.proj_zint = itf.zint + (itf.zdint*min(p.tvpetbl[itf.lev], itf.trtru))
                if(g.ra[0] == False and g.ra[5] == False):
                    itf.int_cross = True
                elif(m.fabs(itf.zdint) > p.olev and ((g.ra[0] == True and g.zown > dispvar.proj_zint) or (g.ra[5] == True and g.zown < dispvar.proj_zint))):
                    itf.int_cross = True
                else:
                    itf.own_cross = True
            else:
                if((g.clstrong == 8 and g.clstrold <= 4) or (g.destrong == 8 and g.destrold <= 4)):
                    g.anycross = True
        else:
            if(itf.int_cross == True or itf.own_cross == True):
                if((itf.tptr.permtent[6] == False and itf.rz >= p.crossthr) or (itf.tptr.permtent[6] == True and itf.rz <= -p.crossthr)):
                    itf.int_cross = False
                    itf.own_cross = False
    else:
        itf.int_cross = False
        itf.own_cross = False
"""VALID"""


"""VALID"""
def load_display_and_aural_info(g, to_disp_aurl):
    if(True in g.ra[:10]):
        if(g.anycross == True):
            to_disp_aurl.vertical_control = CROSSING
            to_disp_aurl.crossing = True
        elif(g.anyreverse == True):
            to_disp_aurl.vertical_control = REVERSE
        elif(g.anyincrease == True):
            to_disp_aurl.vertical_control = INCREASE
        else:
            to_disp_aurl.vertical_control = VERTICAL_CONTROL_NONE
        if(g.maintain == True):
            to_disp_aurl.vertical_control = MAINTAIN
        if(g.corrective_clm == True):
            to_disp_aurl.combined_control = CLIMB_CORR
        elif(g.corrective_des == True):
            to_disp_aurl.combined_control = DESCEND_CORR
        else:
            to_disp_aurl.combined_control = PREVENTIVE
        if(g.ra[0] == True):
            to_disp_aurl.up_advisory = CLIMB
        elif(g.ra[1] == True):
            to_disp_aurl.up_advisory = DONT_DESCEND
        elif(g.ra[2] == True):
            to_disp_aurl.up_advisory = DONT_DESCEND500
        elif(g.ra[3] == True):
            to_disp_aurl.up_advisory = DONT_DESCEND1000
        elif(g.ra[4] == True):
            to_disp_aurl.up_advisory = DONT_DESCEND2000
        else:
            to_disp_aurl.up_advisory = UP_ADVISORY_NONE
        if(g.ra[5] == True):
            to_disp_aurl.down_advisory = DESCEND
        elif(g.ra[6] == True):
            to_disp_aurl.down_advisory = DONT_CLIMB
        elif(g.ra[7] == True):
            to_disp_aurl.down_advisory = DONT_CLIMB500
        elif(g.ra[8] == True):
            to_disp_aurl.down_advisory = DONT_CLIMB1000
        elif(g.ra[9] == True):
            to_disp_aurl.down_advisory = DONT_CLIMB2000
        else:
            to_disp_aurl.down_advisory = DOWN_ADVISORY_NONE
        to_disp_aurl.rate = g.zdmodel
    else:
        to_disp_aurl.vertical_control = VERTICAL_CONTROL_NONE
        to_disp_aurl.combined_control = COMBINED_CONTROL_NONE
        to_disp_aurl.up_advisory = UP_ADVISORY_NONE
        to_disp_aurl.down_advisory = DOWN_ADVISORY_NONE
        to_disp_aurl.rate = 0
        to_disp_aurl.crossing = False
        if(g.allclear == True):
            to_disp_aurl.combined_control = CLEAR_OF_CONFLICT
"""VALID"""


"""VALID"""
def set_up_display_outputs(g, p, to_disp_aurl, dispvar):
    if(True in g.ra[:10]):
        if(g.anyincrease == True):
            g.anyreverse, g.maintain, g.anycross = False, False, False
            if(g.previncrease == False):
                g.anycorchang, g.previncrease = True, True
        else:
            g.previncrease = False
            if((g.ra[0] == True and g.zdmodel > p.clmrt and g.zdown > p.clmrt) or (g.ra[5] == True and g.zdmodel < p.desrt and g.zdown < p.desrt)):
                g.maintain = True
                g.anyreverse = False
            else:
                if((g.clstrold == 4 and g.destrold == 4) and (g.clstrong == 0 or g.destrong == 0)):
                    g.maintain = False
            if(g.anyreverse == True):
                g.anycross = False
                g.maintain = False
            if(g.corrective_clm == False and g.corrective_des == False):
                if(g.ra[1] == True and g.ra[6] == True):
                    g.maintain = True
                else:
                    g.maintain = False
                    if(g.clstrong == 4 and g.clstrold == 8 and g.destrong == 0):
                        g.corrective_clm, g.anyprecor = True, True
                    else:
                        if(g.destrong == 4 and g.destrold == 8 and g.clstrong == 0 and g.extalt == False):
                            g.corrective_des, g.anyprecor = True, True
                g.zdmodel = 0
            else:
                if(g.ra[0] == False and g.ra[5] == False):
                    g.maintain = False
                    g.zdmodel = 0
        g.allclear = False
    else:
        g.maintain, g.anyincrease = False, False
        g.zdmodel = 0
        if(dispvar.anyaltlost == True):
            dispvar.anytrackdrop, g.allclear = False, False
        else:
            if(dispvar.anytrackdrop == True):
                g.allclear = False
    load_display_and_aural_info(g, to_disp_aurl)
"""VALID"""


"""VALID"""
def set_up_global_flags(ITF, g, p, to_disp_aurl, dispvar):
    g.alarm, g.anycorchang, g.anycross, g.allclear = False, False, False, False
    g.anyreverse, dispvar.anytrackdrop, dispvar.anyaltlost = False, False, False
    for itf in ITF:
        if(itf.tacode == RA and itf.tptr != None):
            if(g.corrective_clm == True or g.corrective_des == True):
                if(itf.tptr.permtent[10] == True or itf.tptr.permtent[11] == True):
                    if(itf.tptr.permtent[6] == False):
                        g.ra[1] = True
                        g.ra[2] = False
                        g.ra[3] = False
                        g.ra[4] = False
                    if(itf.tptr.permtent[6] == True):
                        g.ra[6] = True
                        g.ra[7] = False
                        g.ra[8] = False
                        g.ra[9] = False
                    itf.tptr.permtent[4] = True
                    itf.tptr.permtent[5] = False
                    itf.tptr.permtent[10] = False
                    itf.tptr.permtent[11] = False
                    g.zdmodel = 0
                    if(itf.tptr.permtent[6] == False):
                        g.clstrong = max(g.clstrong, eval_(itf.tptr.permtent))
                        dispvar.goalcl = 0
                    else:
                        g.destrong = max(g.destrong, eval_(itf.tptr.permtent))
                        dispvar.goaldes = 0
                    itf.tptr.poowrar = ramap(itf.tptr.permtent)
        if(np.array_equal(g.ra[:10], np.full(10, False, dtype=bool))):
            if(itf.altitude_lost == True):
                if(itf.rd <= 0):
                    dispvar.anyaltlost = True
                itf.altitude_lost = False
            else:
                if(itf.ditf == True):
                    dispvar.anytrackdrop = True
        else:
            crossing_flag_check(itf, g, p, dispvar)
            if(itf.reverse == True and (g.ra[0] == True or g.ra[5] == True)):
                g.anyreverse = True
            itf.reverse = False
            if(itf.altitude_lost == True and itf.rd > 0):
                itf.altitude_lost = False
        if(itf.clear_conflict == True):
            g.allclear = True
            itf.clear_conflict = False
    if(g.mac_reverse == True and (g.ra[0] == True or g.ra[5] == True)):
        g.anyreverse = True
        g.mac_reverse = False
    set_up_display_outputs(g, p, to_disp_aurl, dispvar)
    dispvar.success = False
    for itf in ITF:
        if(dispvar.success != False):
            break
        if(itf.int_cross == True or itf.own_cross == True):
            dispvar.success = True
    if(dispvar.success == True):
        g.crossing_ra = True
    else:
        g.crossing_ra = False
    if(g.anyreverse == True):
        g.reversal_ra = True
    if(g.anynewthr == True or g.anyprecor == True or g.anycorchang == True or (g.clstrong != 0 and (g.clstrong != g.clstrold or (g.destrong == 0 and g.destrold != 0))) or (g.destrong != 0
    and (g.destrong != g.destrold or (g.clstrong == 0 and g.clstrold != 0)))):
        g.alarm = True
"""VALID"""


"""VALID"""
def store_threat_info(TF, g, dispvar):
    dispvar.success = False
    for tf in TF:
        if(dispvar.success != False):
            break
        if(tf.new == True):
            if(tf.iptr.eqp != ATCRBS):
                g.id = tf.id
                g.active = 1
            else:
                g.pointer = tf.iptr
                g.active = 2
                g.altnew = tf.iptr.zrint
                g.rngnew = tf.iptr.r
                g.rngvalid = tf.iptr.rflg
                g.brngnew = tf.iptr.bearing
                g.brngvalid = tf.iptr.bearok
            dispvar.success = True
    for tf in TF:
        if(tf.new == True):
            tf.new = False
    for tf in TF:
        if(dispvar.success != False):
            break
        if(g.active == 2 and tf.iptr != None):
            if(tf.iptr == g.pointer):
                g.altnew = tf.iptr.zrint
                g.rngnew = tf.iptr.r
                g.rngvalid = tf.iptr.rflg
                g.brngnew = tf.iptr.bearing
                g.brngvalid = tf.iptr.bearok
                dispvar.success = True
"""VALID"""


"""VALID"""
def set_up_rac_and_mte(g, ra_to_trans, to_ground_station, dispvar):
    dispvar.rac = g.intent
    if(True in g.ra[:10]):
        if(g.macflg == True):
            dispvar.mte = True
            if(g.clstrong != 0 and g.destrong != 0):
                dispvar.ara[0] = False
            else:
                dispvar.ara[0] = True
        else:
            dispvar.mte = False
            dispvar.ara[0] = True
    else:
        for i in range(len(dispvar.ara)):
            dispvar.ara[i] = False
    if(True in g.ra[:10]):
        ra_to_trans.rai = False
    else:
        ra_to_trans.rai = True
    if((np.array_equal(g.ra[:10], np.full(10, False, dtype=bool))) and (True in g.prevra[:10])):
        to_ground_station.rat = True
    else:
        to_ground_station.rat = False
"""VALID"""


"""VALID"""
def set_up_ara(g, dispvar):
    for i in range(1,len(dispvar.ara)):
        dispvar.ara[i] = False
    if(dispvar.ara[0] == True):
        if((g.corrective_clm == True or g.corrective_des == True) and g.maintain == False):
            dispvar.ara[1] = True
        if(True in g.ra[5:10]):
            dispvar.ara[2] = True
        if(g.anyincrease == True):
            dispvar.ara[3] = True
        if(g.reversal_ra == True):
            dispvar.ara[4] = True
        if(g.crossing_ra == True):
            dispvar.ara[5] = True
        if(g.ra[0] == True or g.ra[5] == True):
            dispvar.ara[6] = True
    else:
        if(dispvar.mte == True):
            if(g.corrective_clm == True and g.maintain == False):
                dispvar.ara[1] = True
            if(g.ra[0] == True):
                dispvar.ara[2] = True
            if(g.corrective_des == True and g.maintain == False):
                dispvar.ara[3] = True
            if(g.ra[5] == True):
                dispvar.ara[4] = True
            if(g.crossing_ra == True):
                dispvar.ara[5] = True
            if(g.reversal_ra == True):
                dispvar.ara[6] = True
"""VALID"""


"""VALID"""
def set_up_tti_and_tid(g, ra_to_trans):
    ra_to_trans.tti[0] = False
    ra_to_trans.tti[1] = False
    for i in range(len(ra_to_trans.tid)):
        ra_to_trans.tid[i] = False
    if(g.active == 2):
        ra_to_trans.tti[0] = True
        ra_to_trans.tti[1] = False
        """Pass ra_to_trans.tid"""
    else:
        if(g.active == 1):
            ra_to_trans.tti[0] = False
            ra_to_trans.tti[1] = True
"""VALID"""


"""VALID"""
def set_up_ra_broadcast(g, ra_to_trans, to_ground_station, dispvar):
    set_up_rac_and_mte(g, ra_to_trans, to_ground_station, dispvar)
    if(True in g.ra[:10]):
        set_up_ara(g, dispvar)
    set_up_tti_and_tid(g, ra_to_trans)
    g.prevmte = g.macflg
"""VALID"""


"""OK"""
def broadcast(TF, g, o, p, ra_to_trans, to_ground_station, brdcst_data, dispvar):
    store_threat_info(TF, g, dispvar)
    set_up_ra_broadcast(g, ra_to_trans, to_ground_station, dispvar)
    if(g.brdcst == False):
        if(True in g.ra[:10]):
            g.brdcst = True
    if(g.brdcst == True and (g.ncycle == p.rabrdcst or to_ground_station.rat == True)):
        if(to_ground_station.rat == True):
            to_ground_station.ara = brdcst_data.prv_ara
            to_ground_station.rac = brdcst_data.prv_rac
            to_ground_station.mte = brdcst_data.prv_mte
            to_ground_station.aid = brdcst_data.prv_aid
            to_ground_station.cac = brdcst_data.prv_cac
        else:
            to_ground_station.ara = dispvar.ara
            to_ground_station.rac = dispvar.rac
            to_ground_station.mte = dispvar.mte
            g.aid = o.aid
            if(g.airdata == True):
                """Pass g.cac"""
                pass
            to_ground_station.aid = g.aid
            to_ground_station.cac = g.cac
            brdcst_data.prv_ara = dispvar.ara
            brdcst_data.prv_rac = dispvar.rac
            brdcst_data.prv_mte = dispvar.mte
            brdcst_data.prv_aid = g.aid
            brdcst_data.prv_cac = g.cac
        if(np.array_equal(g.ra[:10], np.full(10, False, dtype=bool))):
            g.brdcst, g.brngvalid, g.rngvalid = False, False, False
            g.crossing_ra, g.reversal_ra = False, False
            g.active, g.id = 0, 0
            g.altnew, g.brngnew, g.rngnew = 0, 0, 0
            g.pointer = None
            g.ncycle = p.rabrdcst
    if(g.brdcst == True):
        g.ncycle -= 1
    if(g.ncycle == 0):
        g.ncycle = p.rabrdcst
"""OK"""


# def send_atcrbs_info_to_surveillance(ITF, g, ATCRBSList):
#     ATCRBSList.clear()
#     if(g.tamode == True):
#         for itf in ITF:
#             if(itf.eqp == ATCRBS and itf.tacode >= TANMC):
#                 pass


"""VALID"""
def display_advisories(ITF, TF, g, o, p, realtime, to_disp_aurl, ra_to_trans, to_ground_station, brdcst_data, dispvar):
    time_lock_begin = time.time()
    while (g.colock == True):
        if ((time.time() - time_lock_begin) > p.tunlock):
            assert ()
        time.sleep(0.01)
    g.colock = True
    g.tlock = realtime.tclock
    g.clstrold = g.clstrong
    g.destrold = g.destrong
    g.anynewthr, g.anyprecor = False, False
    g.destrong, g.clstrong = 0, 0
    for tf in TF:
        if(tf.poowrar != 0):
            if(tf.iptr != None):
                if(tf.iptr.increase_pending == False and tf.iptr.retention == False):
                    if(tf.permtent[6] == False):
                        g.clstrong = max(g.clstrong, eval_(tf.permtent))
                    else:
                        g.destrong = max(g.destrong, eval_(tf.permtent))
            if(tf.new == True):
                g.anynewthr = True
    if(g.clstrong == 8):
        if(g.clstrold < 8):
            g.tposra = g.tcur
            g.ztv = g.zown
            g.zdtv = g.zdown
    else:
        if(g.destrong == 8):
            if(g.destrold < 8):
                g.tposra = g.tcur
                g.ztv = g.zown
                g.zdtv = g.zdown
    set_up_goal_rate(TF, g, p, dispvar)
    corrective_preventive_test(g, p, dispvar)
    set_up_global_flags(ITF, g, p, to_disp_aurl, dispvar)
    broadcast(TF, g, o, p, ra_to_trans, to_ground_station, brdcst_data, dispvar)
    if(g.transvi == 0):
        ra_to_trans.rac = g.intent
        ra_to_trans.ara = g.ra
    else:
        ra_to_trans.ara = dispvar.ara
        ra_to_trans.rac = dispvar.rac
        ra_to_trans.mte = dispvar.mte
    g.colock = False
    g.prevra = g.ra
    # send_atcrbs_info_to_surveillance()
"""VALID"""