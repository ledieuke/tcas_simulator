import numpy as np
import math as m
import time

from tcasClass import *
from tcasConstant import *

from detect import vertical_miss_distance_calculation, project_vertical_given_zdgoal, project_over_interval, model_sep, model_maneuvers, pm

class Resvar:
    def __init__(self):
        """Group sense"""
        self.alt_diff = None #Difference between intruder's projected and own's current altitude
        self.complement = None #Numeric value of complement of intent
        self.direction = None #Direction (sense)
        self.increase_sep = None #Separation given increase RA
        self.mzdint = None #Modeled intruder altitude rate
        self.new_sense = None #Sense of RA after Reversal
        self.nominal_sep = None #Separation given nominal RA
        self.ownlev = None #Calculated own altitude following a leveloff
        self.relalt = None #Altitude relative to TF threat
        self.tacc = None #Time to accelerate
        self.tagr = None #Time at goal rate
        self.taulim = None #Threshold value of modified tau
        self.tdgr = None #Time to accel. from current rate to goal rate in response to nonreversal RA
        self.trtlim = None #Time to closest approach (with ceiling)
        self.vmdo = None #Vertical miss distance for TF threat
        self.zdgoal = None #Goal rate associated with RA
        self.zint1 = None #Intruder altitude projected at end of critical interval
        self.zint2 = None #Intruder altitude projected at beginning of critical interval
        self.zmp = None #Separation
        self.zmpclm = None #Separation given climb sense
        self.zmpdes = None #Separation given descend sense
        self.zown1 = None #Own altitude projected at end of critical interval
        self.zown2 = None #Own altitude projected at beginning of critical interval

        """Group altitude_alerter"""
        self.level_off_ok = None #Boolean indicating whether a level-off is appropriate
        self.start_capture_alt = None #Altitude at the beginning of an altitude capture maneuver

        """Group select_advisory"""
        self.alimod = None #Modification to ALIM (hysteresis)
        self.avsl = None #Advisory vertical speed limit (rate)
        self.consider_increase = None #Flag set by reversal logic to consider increase rate RA
        self.dmod = None #Incremental range protection
        self.inthr = None #TRUE = separation falls within given threshold
        self.noweaken_time = None #Time advisory not allowed to weaken
        self.oldgoal = None #Previous cycles RA goal rate in feet per minute
        self.owntent = np.full(12, False, dtype=bool) #Advisory for WL (input) threat
        self.positn = None #Position (altitude)
        self.tempthr = None #Temporary variable for holding altitude threshold of ZTHR for slow closure and ALIM otherwise
        self.thrhld = None #Threshold value used for checking POSITN
        self.trthr = None #Range tau threshold
        self.ttlozthr = None #Minimum vertical separation needed to force initial level-off against TCAS-equipped threat
        self.vo = None #Predicted altitude
        self.vslok = None #TRUE = given VSL or neg RA is safe
        self.vvmd = None #Reduction of own rate to VSL

        """Group threat_file_update"""
        self.ind1 = None #Pointer to RA to delete
        self.ind2 = None #Pointer to RA to add
        self.oldpoi = None #Advisory to delete
        self.optr = None #Advisory to add
        self.raind = None #Pointer to RA for current threat
        self.success = None #Flag indicating success of action (msg. transfer,etc)

        """Group RA_monitoring"""
        self.thres_rz = None #Altitude threshold
        self.t_rz = None #Time threshold for reversal RA leading to altitude crossing
        self.delta_z_cpa = None #CPA
        self.delta_z_min = None #Minimum CPA
        self.delta_z_max = None #Maximum CPA
        self.delta_t_rz = None #Delta time threshold to add to t_rz
        self.fact_mult = None #Multiplying factor
        self.zi_in = None #Intruder’s altitude computed with ITF.ZDINR
        self.zi_out = None #Intruder’s altitude computed with ITF.ZDOUTR

        """Group Take_decision"""
        self.zi25 = None #Projected altitude of intruder 2.5s after current time
        self.zo25 = None #Projected altitude of own 2.5s after current time

        """Group coordination"""
        self.sit = None #Local index for Mode S sites

        """Group modeling"""
        self.accel = None #Vertical acceleration to model
        self.cur_sense = None #Current sense of own versus threat
        self.delay = None #Modeled pilot delay for climb/descent during critical interval
        self.hveq = None #Horizontal/vertical equivalence factor
        self.proj_zint = None #Int. projected alt. at CPA using ZDINT
        self.sense = None #Sense of own versus threat
        self.tauarg = None #Local copy of a tau value used for modeling
        self.tauhold = None #Temporary storage for ITF.TAUR
        self.tm = None #Time of minimum or maximum vertical separation when acceleration applied
        self.tproj = None #Time projected for acceleration to resolution advisory maneuver
        self.truhold = None #Temporary storage for ITF.TRTRU
        self.t1 = None #Intermediate value of range tau
        self.varg = None #Local copy of a vertical speed limit for modeling
        self.vdproj = None #Projected altitude rate
        self.vproj = None #Projected altitude at end of acceleration to RA maneuver
        self.z = None #Own altitude
        self.zd = None #Own altitude rate
        self.zmptm = None #Aircraft separation at extremum during critical interval
        self.zdi = None #Intruder rate bound
        self.zdproj = None #Projected altitude rate
        self.zi = None #Intruder altitude
        self.zproj = None #Projected altitude
        self.zpr1 = None #Projected intruder altitude at end of critical interval
        self.zpr2 = None #Projected intruder altitude at beginning of critical interval


"""VALID"""
def ramap(arg):
    if(np.array_equal(arg, np.array([False,False,False,True,False,False,False,False,False,False,False,False]))):
        ramap = 1
    elif(np.array_equal(arg, np.array([False,False,False,True,True,False,False,False,False,False,False,False]))):
        ramap = 2
    elif(np.array_equal(arg, np.array([False,False,False,True,True,True,False,False,False,False,False,True]))):
        ramap = 3
    elif(np.array_equal(arg, np.array([False,False,False,True,True,True,False,False,False,False,True,False]))):
        ramap = 4
    elif(np.array_equal(arg, np.array([False,False,False,True,True,True,False,False,False,False,True,True]))):
        ramap = 5
    elif(np.array_equal(arg, np.array([False,False,False,True,False,False,True,False,False,False,False,False]))):
        ramap = 6
    elif(np.array_equal(arg, np.array([False,False,False,True,True,False,True,False,False,False,False,False]))):
        ramap = 7
    elif(np.array_equal(arg, np.array([False,False,False,True,True,True,True,False,False,False,False,True]))):
        ramap = 8
    elif(np.array_equal(arg, np.array([False,False,False,True,True,True,True,False,False,False,True,False]))):
        ramap = 9
    elif(np.array_equal(arg, np.array([False,False,False,True,True,True,True,False,False,False,True,True]))):
        ramap = 10
    elif(np.array_equal(arg, np.array([True,False,False,False,False,False,False,False,False,False,False,False]))):
        ramap = 11
    elif(np.array_equal(arg, np.array([True,False,True,False,False,False,False,False,False,False,False,False]))):
        ramap = 12
    elif(np.array_equal(arg, np.array([True,True,True,False,False,False,False,False,False,False,False,False]))):
        ramap = 13
    elif(np.array_equal(arg, np.array([True,True,False,False,False,False,False,False,False,False,False,False]))):
        ramap = 14
    else:
        ramap = 0
    return ramap
"""VALID"""


"""VALID"""
def update_threat_file_own(itf, tf, TF, wl, g, resvar, DIL):
    if(wl.status == TERM):
        itf.permtent_copy = tf.permtent
        resvar.oldpoi = tf.poowrar
        resvar.optr = 0
        if((m.fabs(tf.pothrar[0]) > 1e-10 or m.fabs(tf.pothrar[1]) > 1e-10) and (itf.ditf == False) and (itf.altitude_lost == False)):
            tf.poowrar = 0
            for i in range(len(tf.permtent)):
                tf.permtent[i] = False
        else:
            DIL.append(tf.pothrar[0])
            DIL.append(tf.pothrar[1])
            TF.remove(tf)
            itf.tptr = Tf()
            itf.tptr = None
    else:
        if(not np.array_equal(resvar.owntent, tf.permtent)):
            for i in range(len(tf.permtent)):
                tf.permtent[i] = resvar.owntent[i]
            itf.tcmd = g.tcur
        resvar.optr = ramap(resvar.owntent)
        resvar.oldpoi = tf.poowrar
        tf.poowrar = resvar.optr
"""VALID"""


"""VALID2"""
def delete_resolution_advisory(raind, TF, g, resvar):
    if(raind != 0):
        resvar.success = False
        for tf in TF:
            if(resvar.success != False):
                break
            if(raind == tf.poowrar):
                resvar.success = True
        if(resvar.success == True):
            pass
        else:
            g.ra[raind-1] = False
"""VALID2"""


"""VALID"""
def new_threat_file_entry(itf, ITF, TF, g, p, resvar):
    resvar.success = False
    tf = None
    if(itf.eqp != ATCRBS):
        for tf_c in TF:
            if(resvar.success != False):
                break
            if(itf.idint == tf_c.id):
                resvar.success = True
                tf = tf_c
    if(resvar.success == False):
        tf = Tf()
        TF.append(tf)
        tf.id = itf.idint
        tf.poowrar, tf.pothrar[0], tf.pothrar[1] = 0, 0, 0
        tf.tthlrcm = p.tinit
        for i in range(len(tf.permtent)):
            tf.permtent[i] = False
    tf.iptr = ITF[itf.irow]
    tf.new = True
    itf.tiebreaker_reversal = False
    itf.valrevs = 0
    itf.cpt_rev = 0
    itf.rev_geom = False
    itf.tcmd = g.tcur
    itf.tptr = tf
"""VALID"""


"""VALID"""
def form_complement(tf, resvar):
    resvar.complement = tf.pothrar[0] - 1
    if(m.fabs(resvar.complement - 1) < 1e-10):
        resvar.owntent[6] = True
    else:
        resvar.owntent[6] = False
"""VALID"""


"""VALID"""
def select_sense(itf, tf, g, p, detvar, resvar):
    if(itf.eqp == TCAS and (tf.pothrar[0] in (1,2)) and (g.idown > itf.idint or not (((tf.pothrar[0] == 1
        and itf.rz <= -p.crossthr) or (tf.pothrar[0] == 2 and itf.rz >= p.crossthr))) or (g.idown < itf.idint
        and ((g.tcur - tf.t_intent) > p.tiethr or (g.tcur - g.ramode_on) <= p.tiethr)))):
        form_complement(tf, resvar)
    else:
        if(m.fabs(itf.badfok) < 1e-10):
            resvar.zmpclm, resvar.zmpdes = model_maneuvers(itf, g, p, detvar, resvar)
            if(resvar.zmpclm > resvar.zmpdes):
                resvar.owntent[6] = False
                itf.sech = resvar.zmpdes
            elif(g.climbinhib == True and itf.rz >= -p.crossthr and (resvar.zmpclm + p.nozcross) > resvar.zmpdes):
                resvar.owntent[6] = False
                itf.sech = resvar.zmpdes
            else:
                resvar.owntent[6] = True
                itf.sech = resvar.zmpclm
            resvar.z, resvar.zd = project_vertical_given_zdgoal(p.tv1 + m.fabs(g.zdown/p.vaccel), g.zown, g.zdown, 0, p.tv1, p.vaccel, resvar)
            resvar.zi, resvar.zdi = project_vertical_given_zdgoal(p.tv1 + m.fabs(g.zdown/p.vaccel), itf.zint, itf.zdint, itf.zdint, p.tv1, p.vaccel, resvar)
            if(itf.rz >= p.crossthr and (g.zdown >= 0 or resvar.z >= (resvar.zi + p.crossthr))):
                if((resvar.owntent[6] == True) and (resvar.zmpclm >= g.alim)):
                    resvar.owntent[6] = False
                    itf.sech = resvar.zmpdes
            if(itf.rz <= -p.crossthr and (g.zdown <= 0 or resvar.z <= (resvar.zi - p.crossthr))):
                if((resvar.owntent[6] == False) and (resvar.zmpdes >= g.alim)):
                    resvar.owntent[6] = True
                    itf.sech = resvar.zmpclm
        elif(m.fabs(itf.badfok-1) < 1e-10):
            resvar.owntent[6] = False
        else:
            resvar.owntent[6] = True
"""VALID"""


"""VALID"""
def reversal_modeling(itf, g, p, resvar):
    resvar.nominal_sep = 0
    resvar.z = g.zown
    resvar.zd = g.zdown
    resvar.delay = 0
    if(g.own_follow == False):
        resvar.nominal_sep = model_sep(resvar.delay, resvar.zd, resvar.z, resvar.zd, p.vaccel, resvar.owntent[6], itf.zint, itf.zdint, itf, g, p, resvar)
        if(resvar.owntent[6] == True):
            resvar.new_sense = False
        else:
            resvar.new_sense = True
        if(resvar.nominal_sep > 1.2*p.crossthr):
            itf.reverse = False
    else:
        if(resvar.owntent[4] == False and resvar.owntent[5] == False):
            resvar.delay = max(p.tv1 - (g.tcur - g.tposra), 0)
            if(resvar.owntent[6] == False):
                resvar.zdgoal = max(min(g.zdown, p.maxdrate), p.clmrt)
            else:
                resvar.zdgoal = min(max(g.zdown, p.mindrate), p.desrt)
            resvar.zproj, resvar.zdproj = project_vertical_given_zdgoal(g.tcur - g.tposra, g.ztv, g.zdtv, resvar.zdgoal, p.tv1, p.vaccel, resvar)
            if(((resvar.owntent[6] == False and resvar.zproj > g.zown and (g.zdown >= (g.zdtv - p.model_zd)))
                or (resvar.owntent[6] == True and resvar.zproj < g.zown and (g.zdown <= (g.zdtv + p.model_zd)))) and (g.tcur -g.tposra) < p.model_t):
                resvar.z = resvar.zproj
                resvar.zd = resvar.zdproj
            resvar.nominal_sep = model_sep(resvar.delay, resvar.zdgoal, resvar.z, resvar.zd, p.vaccel, resvar.owntent[6], itf.zint, itf.zdint, itf, g, p, resvar)
        if(resvar.owntent[6] == True):
            resvar.new_sense = False
        else:
            resvar.new_sense = True
        resvar.delay = max(p.tv1 - (g.tcur - g.tlastnewra), p.quikreac)
        if(resvar.new_sense == False):
            resvar.zdgoal = max(p.clmrt, min(g.zdown, p.maxdrate))
        else:
            if(g.nodescent == True):
                resvar.zdgoal = 0
            else:
                resvar.zdgoal = min(p.desrt, max(g.zdown, p.mindrate))
        if(g.rev_consdrd == False):
            if((itf.int_cross == True) or (m.fabs(itf.zdint) < 1e-10 and itf.rz > 0) or (itf.zdint*g.zdmodel < 0)):
                resvar.mzdint = itf.zdoutr
            else:
                resvar.mzdint = itf.zdinr
        else:
            resvar.mzdint = itf.zdint
        resvar.zmp = model_sep(resvar.delay, resvar.zdgoal, resvar.z, resvar.zd, p.raccel, resvar.new_sense, itf.zint, resvar.mzdint, itf, g, p, resvar)
        if(resvar.zmp <= 0 or resvar.nominal_sep >= g.alim):
            itf.reverse = False
"""VALID"""


"""VALID"""
def reversal_proj_check(itf, g, p, resvar):
    if((resvar.owntent[6] == False and itf.rz <= -p.avevalt) or (resvar.owntent[6] == True and itf.rz >= p.avevalt)
        or (itf.trtru > p.minrvstime and ((resvar.owntent[6] == False and itf.rz <= -p.crossthr) or (resvar.owntent[6] == True and itf.rz >= p.crossthr)))):
        if(itf.int_cross == True):
            if((resvar.owntent[6] == False and g.zown < resvar.proj_zint) or (resvar.owntent[6] == True and g.zown > resvar.proj_zint)):
                itf.reverse = True
        elif(itf.own_cross == True):
            if(((resvar.owntent[6] == False and g.zown > resvar.proj_zint) or (resvar.owntent[6] == True and g.zown < resvar.proj_zint)) and m.fabs(itf.zdint) >= p.olev):
                itf.own_cross, itf.int_cross = False, True
            else:
                if(g.macflg == False):
                    resvar.zmpclm, resvar.zmpdes = model_maneuvers(itf, g, p, resvar)
                    if(resvar.zmpclm > resvar.zmpdes):
                        if(resvar.owntent[6] == True and resvar.zmpclm > (resvar.zmpdes + p.nozcross)):
                            itf.reverse = True
                    else:
                        if(resvar.owntent[6] == False and resvar.zmpdes > (resvar.zmpclm + p.nozcross)):
                            itf.reverse = True
        if(itf.reverse == True):
            reversal_modeling(itf, g, p, resvar)
"""VALID"""


"""VALID"""
def cross_through_check(itf, g, p, resvar):
    if((resvar.owntent[6] == False and itf.rz <= -p.crossthr) or (resvar.owntent[6] == True and itf.rz >= p.crossthr)):
        itf.reverse = True
        reversal_modeling(itf, g, p, resvar)
    else:
        if(m.fabs(g.zdown) > p.olev and (g.zdmodel*g.zdown) < 0 and itf.eqp != TCAS):
            resvar.z, resvar.zd = project_vertical_given_zdgoal(m.fabs(g.zdown/p.vaccel), g.zown, g.zdown, 0, 0, p.vaccel, resvar)
            resvar.zi, resvar.zdi = project_vertical_given_zdgoal(m.fabs(g.zdown/p.vaccel), itf.zint, itf.zdint, itf.zdint, 0, p.vaccel, resvar)
            if((resvar.owntent[6] == False and (resvar.z - resvar.zi) <= 0) or (resvar.owntent[6] == True and (resvar.z - resvar.zi) >= 0)):
                itf.reverse = True
                reversal_modeling(itf, g, p, resvar)
    if(itf.eqp != TCAS and ((resvar.owntent[6] == False and itf.rz >= p.crossthr) or (resvar.owntent[6] == True
        and itf.rz <= -p.crossthr)) and m.fabs(itf.rz) <= p.maxaltdiff and (g.zdown*itf.zdint) > 0 and m.fabs(g.zdown) > p.ilev
        and (g.zdmodel*g.zdown) > 0 and resvar.owntent[4] == False and resvar.owntent[5] == False and m.fabs(itf.zdint) > p.ilev and itf.ifirm >= p.minfirm):
        resvar.z = g.zown + g.zdown*min(p.tvpetbl[itf.lev], itf.trtru)
        resvar.zi = itf.zint + itf.zdint*min(p.tvpetbl[itf.lev], itf.trtru)
        if((resvar.owntent[6] == False and (resvar.z - resvar.zi) < p.crossthr) or (resvar.owntent[6] == True and (resvar.z - resvar.zi) > -p.crossthr)):
            itf.reverse = True
            reversal_modeling(itf, g, p, resvar)
"""VALID"""


"""VALID"""
def take_decision(itf, g, p, resvar):
    if(g.zdown*itf.zdint > 0 and m.fabs(g.zdown) > p.ilev and m.fabs(itf.zdint) > p.ilev and (g.tcur - g.tlastnewra) >= g.bounded_ttf
    and (itf.trtru > resvar.t_rz or (g.tcur - itf.tcmd) > p.tv1 or g.anyincrease == False)):
        if(((resvar.owntent[6] == False and resvar.delta_z_min < 1.2*p.crossthr) or (resvar.owntent[6] == True
        and resvar.delta_z_max > -1.2*p.crossthr)) and m.fabs(itf.rz) < p.maxaltdiff and (itf.eqp == TCAS
        or g.zdown*g.zdmodel > 0) and ((resvar.owntent[6] == False and itf.rz <= -resvar.thres_rz)
        or (resvar.owntent[6] == True and itf.rz >= resvar.thres_rz))):
            itf.cpt_rev += 1
            if((g.anyincrease == False or (g.tcur - itf.tcmd) > 1) and (m.fabs(itf.cpt_rev - 3) < 1e-10 or m.fabs(itf.cpt_rev - 5) < 1e-10 or m.fabs(itf.cpt_rev - 7) < 1e-10)):
                itf.reverse = True
                g.rev_consdrd = True
                reversal_modeling(itf, g, p, resvar)
        if((g.anyincrease == False or (g.tcur - itf.tcmd) > 1) and itf.reverse == False and ((resvar.owntent[6] == False and resvar.delta_z_cpa < g.alim/2)
        or (resvar.owntent[6] == True and resvar.delta_z_cpa > -g.alim/2)) and itf.eqp == TCAS and resvar.owntent[5] == False
        and ((g.zdown < -1.2*p.ilev and resvar.owntent[6] == False) or (g.zdown > 1.2*p.ilev and resvar.owntent[6] == True))
        and ((resvar.owntent[4] == False and (m.fabs(g.tposra - g.tlastnewra) < 1e-10 or (g.tcur - g.tposra) > p.tv1))
        or (resvar.owntent[4] == True and m.fabs(g.zdown) > 1.5*p.ilev))):
            if(itf.trtru > p.minrvstime and itf.ifirm == p.minfirm):
                resvar.thres_rz = resvar.thres_rz + p.crossthr/2
            else:
                if(itf.trtru > p.minrvstime and itf.ifirm == p.minfirm):
                    resvar.thres_rz = resvar.thres_rz + p.crossthr/4
            if((resvar.owntent[6] == False and itf.rz <= -resvar.thres_rz) or (resvar.owntent[6] == True and itf.rz >= resvar.thres_rz)):
                itf.reverse = True
                g.own_follow = False
                reversal_modeling(itf, g, p, resvar)
    resvar.zi25 = itf.zint + 2.5*itf.zdint
    resvar.zo25 = g.zown + 2.5*g.zdown
    if(itf.reverse == True and (itf.adot < -p.olev or m.fabs(itf.rz) > p.crossthr/4) and itf.trtru <= 1.25*p.minrvstime
    and ((resvar.owntent[6] == False and itf.rz < 0 and resvar.zo25 > resvar.zi25) or (resvar.owntent[6] == True and itf.rz > 0 and resvar.zo25 < resvar.zi25))):
        itf.reverse = False
"""VALID"""


"""VALID"""
def ra_monitoring(itf, g, p, resvar):
    g.bounded_ttf = min(max(10, g.ttofollow), 15)
    if(itf.eqp == TCAS):
        resvar.t_rz = max(m.fabs(g.zdown)/p.raccel, m.fabs(itf.zdint)/p.raccel) + p.quikreac
    else:
        resvar.t_rz = m.fabs(g.zdown)/p.raccel + p.quikreac
    resvar.z = g.zown + g.zdown*min(p.tvpetbl[itf.lev], itf.trtru)
    resvar.zi = itf.zint + itf.zdint*min(p.tvpetbl[itf.lev], itf.trtru)
    resvar.zi_in = itf.zint + itf.zdinr*min(p.tvpetbl[itf.lev], itf.trtru)
    resvar.zi_out = itf.zint + itf.zdoutr*min(p.tvpetbl[itf.lev], itf.trtru)
    resvar.delta_z_cpa = resvar.z - resvar.zi
    resvar.delta_z_min = min(resvar.z - resvar.zi_out, resvar.z - resvar.zi, resvar.z - resvar.zi_in)
    resvar.delta_z_max = max(resvar.z - resvar.zi_out, resvar.z - resvar.zi, resvar.z - resvar.zi_in)
    if(itf.eqp == TCAS):
        if(m.fabs(g.zdown) > 3*p.ilev and m.fabs(itf.zdint) > 3*p.ilev):
            resvar.fact_mult = 1.5
            resvar.delta_t_rz = 3.0
        else:
            if(m.fabs(g.zdown) > 2*p.ilev and m.fabs(itf.zdint) > 2*p.ilev):
                resvar.fact_mult = 1.25
                resvar.delta_t_rz = 3.0
            else:
                if(m.fabs(g.zdown) > 1.5*p.ilev and m.fabs(itf.zdint) > 1.5*p.ilev):
                    resvar.fact_mult = 1.1
                    resvar.delta_t_rz = 3.0
                else:
                    resvar.fact_mult = 1.0
                    resvar.delta_t_rz = 5.0
    else:
        resvar.fact_mult = 1.0
        resvar.delta_t_rz = 5.0
    if((g.tcur - itf.tcmd) <= p.tv1 and g.anyincrease == True):
        resvar.fact_mult = resvar.fact_mult/4
    if((itf.trtru >= (resvar.t_rz + resvar.delta_t_rz)) and (itf.rd < -5*p.rdthr) and (itf.trtru > p.minrvstime)):
        resvar.thres_rz = -resvar.fact_mult*p.crossthr
    else:
        if((itf.trtru >= (resvar.t_rz + resvar.delta_t_rz)) and (itf.rd < -5*p.rdthr)):
            resvar.thres_rz = -resvar.fact_mult*p.crossthr*0.25
        else:
            resvar.thres_rz = 0
    if(itf.trtru <= p.minrvstime and itf.ifirm < p.minfirm):
        resvar.thres_rz = resvar.thres_rz + p.crossthr
    else:
        if(itf.trtru <= p.minrvstime and itf.ifirm == p.minfirm):
            resvar.thres_rz = resvar.thres_rz + p.crossthr/2
    take_decision(itf, g, p, resvar)
"""VALID"""


"""VALID"""
def set_up_for_advisory(itf, tf, g, resvar):
    resvar.owntent[4] = False
    resvar.owntent[5] = False
    resvar.owntent[10] = False
    resvar.owntent[11] = False
    for i in range(len(tf.permtent)):
        tf.permtent[i] = resvar.owntent[i]
    itf.tcmd = g.tcur
"""VALID"""


"""VALID"""
def reversal_check(itf, tf, g, p, resvar):
    g.own_follow = True
    g.rev_consdrd = False
    g.consider_increase = False
    if(itf.rev_geom == False):
        if(itf.int_cross == True or itf.own_cross == True):
            if(itf.trtru > p.min_ri_time and itf.taurise < p.taurise_thr):
                resvar.proj_zint = itf.zint + (itf.zdint*min(p.tvpetbl[itf.lev], itf.trtru))
                reversal_proj_check(itf, g, p, resvar)
                if(itf.reverse == False and itf.trtru <= p.minrvstime and itf.eqp != TCAS):
                    resvar.consider_increase = True
        else:
            cross_through_check(itf, g, p, resvar)
        if(itf.cpt_rev > 3):
            itf.cpt_rev = itf.cpt_rev - 4
        itf.cpt_rev = 2*itf.cpt_rev
        if(itf.reverse == False and g.macflg == False and itf.trtru > p.min_ri_time and (g.tcur - g.tlastnewra) >= 10):
            ra_monitoring(itf, g, p, resvar)
    if(itf.valrevs > 3):
        itf.valrevs = itf.valrevs - 4
    itf.valrevs = 2*itf.valrevs
    if(itf.reverse == True):
        itf.valrevs += 1
        if(itf.eqp == TCAS and ((g.idown > itf.idint) or ((itf.valrevs not in (3,5,7)) and (itf.cpt_rev not in (3,5,7)) and (g.own_follow == True) and (itf.int_cross == True or itf.own_cross == True)))):
            itf.reverse = False
        else:
            if(itf.eqp == TCAS or g.macflg == False):
                itf.rev_geom = True
            itf.valrevs = 0
            itf.cpt_rev = 0
            resvar.owntent[6] = resvar.new_sense
            set_up_for_advisory(itf, tf, g, resvar)
            itf.increase = False
            itf.inctest = 0
    if(itf.eqp == TCAS):
        if(g.idown > itf.idint):
            if((tf.pothrar[0] == 1 and resvar.owntent[6] == True) or (tf.pothrar[0] == 2 and resvar.owntent[6] == False)):
                form_complement(tf, resvar)
                itf.tiebreaker_reversal = True
                itf.reverse = True
                set_up_for_advisory(itf, tf, g, resvar)
    if(itf.reverse == True):
        itf.rev_ra = True
        tf.ttlo = False
"""VALID"""


"""VALID"""
def check_projection(positn, thrhld, owntent):
    inthr = False
    if(owntent[6] == False):
        if(positn < thrhld):
            inthr = True
    else:
        if(positn > -thrhld):
            inthr = True
    return inthr
"""VALID"""


"""VALID"""
def eval_(arg):
    if(arg[3] == False):
        eval = 0
    elif(arg[5] == False):
        if(arg[4] == False):
            eval = 8
        else:
            eval = 4
    else:
        eval = 1
        if(arg[10] == False):
            eval += 2
        if(arg[11] == False):
            eval += 1
    return eval
"""VALID"""


"""VALID"""
def vsl_test(avsl, tauarg, hveq, zdi, itf, owntent, g, p, resvar):
    resvar.trtlim = min(tauarg, p.tvpetbl[itf.lev])
    if(owntent[6] == False):
        if(g.zdown >= -avsl):
            resvar.vvmd = itf.rz + (-avsl-zdi)*resvar.trtlim
        else:
            if(itf.wptr.status == CONT):
                resvar.t1 = max(p.backdelay, p.tv1 - (g.tcur - itf.tcmd))
            else:
                resvar.t1 = p.tv1
            resvar.vo, resvar.vdproj = project_vertical_given_zdgoal(resvar.trtlim, g.zown, g.zdown, -avsl, resvar.t1, p.vaccel, resvar)
            resvar.vvmd = (resvar.vo - itf.zint) - zdi*resvar.trtlim
    else:
        if(g.zdown <= avsl):
            resvar.vvmd = itf.rz + (avsl - zdi)*resvar.trtlim
        else:
            if(itf.wptr.status == CONT):
                resvar.t1 = max(p.backdelay, p.tv1 - (g.tcur - itf.tcmd))
            else:
                resvar.t1 = p.tv1
            resvar.vo, resvar.vdproj = project_vertical_given_zdgoal(resvar.trtlim, g.zown, g.zdown, avsl, resvar.t1, p.vaccel, resvar)
            resvar.vvmd = (resvar.vo - itf.zint) - zdi*resvar.trtlim
    resvar.inthr = check_projection(resvar.vvmd, g.alim - hveq, owntent)
    if(resvar.inthr == True):
        vslok = False
    else:
        vslok = True
    return vslok
"""VALID"""


"""VALID"""
def vsl_over_interval(varg, itf, owntent, g, p, resvar):
    resvar.alimod = 0
    resvar.zdi = itf.zdint
    if(itf.wptr.status == NEW and varg > 0):
        resvar.alimod = -p.newvsl
    elif(itf.wptr.status == NEW):
        pass
    else:
        resvar.oldgoal = p.desgoal[eval_(itf.tptr.permtent)]
        if(resvar.oldgoal < varg):
            resvar.alimod = -p.newvsl
    if(itf.wptr.status == NEW and itf.badfok != 0):
        if(owntent[6] == False):
            resvar.zdi = max(itf.zdinr, itf.zdoutr)
        else:
            resvar.zdi = min(itf.zdinr, itf.zdoutr)
    vslok = vsl_test(varg, itf.trtru, resvar.alimod, resvar.zdi, itf, owntent, g, p, resvar)
    if(vslok == True):
        vslok = vsl_test(varg, itf.taur, resvar.alimod, resvar.zdi, itf, owntent, g, p, resvar)
    return vslok
"""VALID"""


"""VALID"""
def try_vsl(itf, tf, wl, g, p, resvar):
    if(itf.rd > 0 and wl.status == NEW):
        resvar.owntent[4] = True
        resvar.owntent[5] = False
        resvar.owntent[10] = False
        resvar.owntent[11] = False
    elif(itf.rd > 0 and itf.rrd_count <= p.rrd_thr):
        for i in range(len(resvar.owntent)):
            resvar.owntent[i] = tf.permtent[i]
    else:
        resvar.vslok = vsl_over_interval(p.v2000, itf, resvar.owntent, g, p, resvar)
        if(resvar.vslok == True):
            resvar.owntent[4] = True
            resvar.owntent[5] = True
            resvar.owntent[10] = True
            resvar.owntent[11] = True
        else:
            resvar.vslok = vsl_over_interval(p.v1000, itf, resvar.owntent, g, p, resvar)
            if(resvar.vslok == True):
                resvar.owntent[4] = True
                resvar.owntent[5] = True
                resvar.owntent[10] = True
                resvar.owntent[11] = False
            else:
                resvar.vslok = vsl_over_interval(p.v500, itf, resvar.owntent, g, p, resvar)
                if(resvar.vslok == True):
                    resvar.owntent[4] = True
                    resvar.owntent[5] = True
                    resvar.owntent[10] = False
                    resvar.owntent[11] = True
                else:
                    resvar.vslok = vsl_over_interval(0, itf, resvar.owntent, g, p, resvar)
                    if(resvar.vslok == True):
                        resvar.owntent[4] = True
                        resvar.owntent[5] = False
                        resvar.owntent[10] = False
                        resvar.owntent[11] = False
                    else:
                        resvar.owntent[4] = False
                        resvar.owntent[5] = False
                        resvar.owntent[10] = False
                        resvar.owntent[11] = False
"""VALID"""


"""VALID"""
def altitude_alerter_logic(itf, tf, g, p, resvar):
    resvar.level_off_ok = True
    if((g.zdown > 0) and (g.alerter_alt > g.zowncor)):
        resvar.start_capture_alt = g.alerter_alt - g.zdown*p.quikreac - (g.zdown*g.zdown)/p.levoffaccx2
        if(g.zowncor < resvar.start_capture_alt):
            resvar.level_off_ok = False
    elif((g.zdown > 0) and (g.alerter_alt < g.zowncor)):
        resvar.start_capture_alt = g.alerter_alt - g.zdown*p.quikreac + (g.zdown*g.zdown)/p.levoffaccx2
        if(g.zowncor > resvar.start_capture_alt):
            resvar.level_off_ok = False
    if(resvar.level_off_ok == False):
        for i in range(len(resvar.owntent)):
            resvar.owntent[i] = tf.permtent[i]
    else:
        resvar.owntent[5] = False
        resvar.owntent[10] = False
        resvar.owntent[11] = False
        itf.rev_ra = False
"""VALID"""


"""VALID"""
def no_weaken_test(tf, wl, tempthr, itf, owntent, g, p, resvar):
    if(wl.status != NEW):
        if(itf.rev_ra == True):
            resvar.noweaken_time = p.trvsnoweak
        else:
            resvar.noweaken_time = p.tnoweak
        if(eval_(tf.permtent) < eval_(owntent)):
            if(itf.taur > p.strofir and itf.ifirm < p.minfirm):
                for i in range(len(owntent)):
                    owntent[i] = tf.permtent[i]
            elif(np.array_equal(tf.permtent[3:6], np.array([True, True, True]))):
                if(g.alerter_ok == True):
                    altitude_alerter_logic(itf, tf, g, p, resvar)
                else:
                    for i in range(len(owntent)):
                        owntent[i] = tf.permtent[i]
            elif((np.array_equal(tf.permtent[3:5], np.array([True, False]))) and (np.array_equal(owntent[3:5], np.array([True, True])))):
                resvar.inthr = check_projection(itf.rz, tempthr, owntent)
                if(resvar.inthr == True):
                    for i in range(len(owntent)):
                        owntent[i] = tf.permtent[i]
                else:
                    if((g.tcur - itf.tcmd) < resvar.noweaken_time or itf.ifirm < p.minfirm):
                        for i in range(len(owntent)):
                            owntent[i] = tf.permtent[i]
                    else:
                        if(g.alerter_ok == True):
                            altitude_alerter_logic(itf, tf, g, p, resvar)
                        else:
                            owntent[5] = False
                            owntent[10] = False
                            owntent[11] = False
                            if(g.macflg == False):
                                itf.rev_ra = False
            else:
                for i in range(len(owntent)):
                    owntent[i] = tf.permtent[i]
"""VALID"""


"""VALID"""
def level_off_test(itf, tf, wl, g, p, resvar):
    if(itf.eqp == TCAS and g.macflg == False):
        resvar.ttlozthr = p.ttlosep + m.fabs(g.zdown)*p.tv1 + 0.5*(g.zdown**2)/p.vaccel
        if(pm(itf.zdint) == pm(itf.rz)):
            resvar.ttlozthr = resvar.ttlozthr + m.fabs(itf.zdint)*p.tv1 + 0.5*(itf.zdint**2)/p.vaccel
        if(wl.status == NEW and itf.a > resvar.ttlozthr and m.fabs(g.zdown) > p.ttlorate and m.fabs(itf.zdint) < p.ilev
        and pm(g.zdown) != pm(itf.rz) and (not np.array_equal(resvar.owntent[4:6], np.array([True,True])))
        and ((resvar.owntent[6] == False and itf.rz > -p.crossthr) or (resvar.owntent[6] == True and itf.rz < p.crossthr))):
            resvar.owntent[4] = True
            resvar.owntent[5] = False
            tf.ttlo = True
            tf.treconf = g.tcur + p.tv1 + m.fabs(g.zdown)/p.vaccel - 1
            tf.initzdi = itf.zdint
            tf.initzdo = g.zdown
        else:
            if(wl.status == CONT and tf.ttlo == True):
                if(m.fabs(g.zdown) <= p.olev or g.tcur > tf.treconf or (resvar.owntent[6] == False and ((itf.zdint - tf.initzdi) > p.ttlozd
                or (tf.initzdo - g.zdown) > p.ttlozd)) or (resvar.owntent[6] == True and ((tf.initzdi - itf.zdint) > p.ttlozd
                or (g.zdown - tf.initzdo) > p.ttlozd))):
                    tf.ttlo = False
                else:
                    resvar.owntent[4] = True
                    resvar.owntent[5] = False
            else:
                tf.ttlo = False
    else:
        tf.ttlo = False
"""VALID"""


"""VALID"""
def choose_ra_strength(tf, wl, tempthr, itf, owntent, g, p, resvar):
    if(m.fabs(itf.zdint) < p.ilev):
        resvar.inthr = check_projection(itf.rz, tempthr, owntent)
        if(resvar.inthr == False):
            try_vsl(itf, tf, wl, g, p, resvar)
        else:
            resvar.inthr = check_projection(itf.vmd, tempthr, owntent)
            if(resvar.inthr == False or m.fabs(g.zdown) > p.olev):
                try_vsl(itf, tf, wl, g, p, resvar)
            else:
                owntent[4] = False
                owntent[5] = False
                owntent[10] = False
                owntent[11] = False
    else:
        resvar.inthr = check_projection(itf.vmd, tempthr, owntent)
        if (resvar.inthr == False or m.fabs(g.zdown) > p.olev):
            try_vsl(itf, tf, wl, g, p, resvar)
        else:
            owntent[4] = False
            owntent[5] = False
            owntent[10] = False
            owntent[11] = False
    no_weaken_test(tf, wl, tempthr, itf, owntent, g, p, resvar)
    level_off_test(itf, tf, wl, g, p, resvar)
"""VALID"""


"""VALID"""
def extreme_altitude_check(itf, g, resvar):
    g.extalt = False
    if(resvar.owntent[6] == False and resvar.owntent[4] == False):
        if((g.climbinhib == True) and (itf.rev_ra == False)):
            resvar.owntent[4] = True
            resvar.owntent[5] = False
            resvar.owntent[10] = False
            resvar.owntent[11] = False
    elif(resvar.owntent[6] == True and resvar.owntent[4] == False):
        if(g.nodescent == True):
            resvar.owntent[4] = True
            resvar.owntent[5] = False
            resvar.owntent[10] = False
            resvar.owntent[11] = False
            itf.rev_ra = False
            if(g.macflg == False):
                g.extalt = True
"""VALID"""


"""VALID"""
def select_advisory(itf, tf, wl, g, p, resvar):
    resvar.dmod = p.dmodtbl[itf.lev]
    if(itf.eqp == TCAS):
        resvar.trthr = p.trtetbl[itf.lev]
    else:
        resvar.trthr = p.trtutbl[itf.lev]
    if((itf.khit > 1) and (itf.rd > -resvar.dmod/resvar.trthr) and (np.array_equal(tf.permtent[3:5], np.array([True, False])))):
        if(itf.rd > p.rdthr):
            itf.trtru = itf.r/itf.rd
        if(itf.rd > 0):
            itf.vmd = vertical_miss_distance_calculation(itf.rz, itf.rzd, itf.trtru, itf.taur, p.tvpctbl[itf.lev])
        choose_ra_strength(tf, wl, g.zthr, itf, resvar.owntent, g, p, resvar)
        if(itf.rd > p.rdthr):
            itf.trtru = p.mintau
        if(itf.rd > 0):
            itf.vmd = itf.rz
    else:
        if((itf.khit == 1) or (wl.status == CONT and itf.trtru <= p.quikreac)):
            for i in range(len(resvar.owntent)):
                resvar.owntent[i] = tf.permtent[i]
        else:
            choose_ra_strength(tf, wl, g.alim, itf, resvar.owntent, g, p, resvar)
    if(itf.khit != 1):
        extreme_altitude_check(itf, g, resvar)
"""VALID"""


"""VALID2"""
def resolution_update(ind1, ind2, TF, g, resvar):
    delete_resolution_advisory(ind1, TF, g, resvar)
    if(m.fabs(ind2) > 1e-10):
        g.ra[ind2-1] = True
"""VALID2"""


"""VALID"""
def increase_modeling(itf, g, p, resvar):
    if(resvar.sense == False):
        if(g.clstrong == 0):
            resvar.zdgoal = min(g.zdown, p.maxdrate)
        else:
            resvar.zdgoal = max(min(g.zdown, p.maxdrate), p.climbgoal[g.clstrong])
    else:
        if(g.destrong == 0):
            resvar.zdgoal = max(g.zdown, p.mindrate)
        else:
            resvar.zdgoal = min(max(g.zdown, p.mindrate), p.desgoal[g.destrong])
    resvar.vproj, resvar.vdproj = project_vertical_given_zdgoal(max(resvar.delay, p.quikreac), resvar.z, resvar.zd, resvar.zdgoal, resvar.delay, p.vaccel, resvar)
    resvar.zi, resvar.zdi = project_vertical_given_zdgoal(max(resvar.delay, p.quikreac), itf.zint, itf.zdint, itf.zdint, resvar.delay, p.vaccel, resvar)
    if(resvar.sense == False):
        resvar.zdgoal = max(min(g.zdown, p.maxdrate), p.inc_clmrate)
    else:
        resvar.zdgoal = min(max(g.zdown, p.mindrate), p.inc_desrate)
    resvar.tauhold = itf.taur
    resvar.truhold = itf.trtru
    itf.taur = max((itf.taur - max(resvar.delay, p.quikreac)), 0)
    itf.trtru = max((itf.trtru - max(resvar.delay, p.quikreac)), 0)
    resvar.increase_sep = model_sep(0, resvar.zdgoal, resvar.vproj, resvar.vdproj, p.raccel, resvar.sense, resvar.zi, itf.zdint, itf, g, p, resvar)
    itf.taur = resvar.tauhold
    itf.trtru = resvar.truhold
"""VALID"""


"""VALID"""
def increase_proj_check(sense, accel, itf, g, p, resvar):
    resvar.cur_sense = sense
    resvar.delay = max(p.tv1 - (g.tcur - g.tposra), 0)
    if(g.clstrong < 8 and g.destrong < 8):
        resvar.delay = max(p.tv1 - (g.tcur - g.tlastnewra), p.quikreac)
    if((g.clstrong > 0 and sense == True) or (g.destrong > 0 and sense == False)):
        if(sense == True):
            resvar.cur_sense = False
        else:
            resvar.cur_sense = True
        resvar.delay = max(p.tv1 - (g.tcur - g.tlastnewra), p.quikreac)
    if(resvar.cur_sense == False):
        resvar.zdgoal = max(min(g.zdown, p.maxdrate), p.clmrt)
    else:
        resvar.zdgoal = min(max(g.zdown, p.mindrate), p.desrt)
    if(g.clstrong == 8 or g.destrong == 8):
        resvar.zproj, resvar.zdproj = project_vertical_given_zdgoal(g.tcur - g.tposra, g.ztv, g.zdtv, resvar.zdgoal, p.tv1, accel, resvar)
        if(((resvar.cur_sense == False and resvar.zproj > g.zown and (g.zdown >= g.zdtv - p.model_zd))
        or (resvar.cur_sense == True and resvar.zproj < g.zown and (g.zdown <= (g.zdtv + p.model_zd)))) and (g.tcur - g.tposra) < p.model_t):
            resvar.z = resvar.zproj
            resvar.zd = resvar.zdproj
        else:
            resvar.z = g.zown
            resvar.zd = g.zdown
    else:
        resvar.z = g.zown
        resvar.zd = g.zdown
    if(sense == False):
        resvar.zdgoal = max(min(g.zdown, p.maxdrate), p.clmrt)
    else:
        if(g.nodescent == True):
            resvar.zdgoal = 0
        else:
            resvar.zdgoal = min(max(g.zdown, p.mindrate), p.desrt)
    nominal_sep = model_sep(resvar.delay, resvar.zdgoal, resvar.z, resvar.zd, accel, sense, itf.zint, itf.zdint, itf, g, p, resvar)
    increase_modeling(itf, g, p, resvar)
    return nominal_sep, resvar.increase_sep
"""VALID"""


"""VALID"""
def increase_check(itf, g, p, resvar):
    resvar.inthr = False
    if((np.array_equal(resvar.owntent[4:7], np.array([False, False, False])) and g.clstrong == 8 and g.clstrold == 8)
    or (np.array_equal(resvar.owntent[4:7], np.array([False, False, True])) and g.destrong == 8 and g.destrold == 8)):
        if(itf.taurise < p.taurise_thr and ((itf.eqp == TCAS) or (resvar.consider_increase == True)
        or (itf.int_cross == False and itf.own_cross == False))):
            if(resvar.consider_increase == True):
                resvar.alt_diff = resvar.proj_zint - g.zown
                if(resvar.owntent[6] == True and resvar.alt_diff <= p.avevalt and resvar.alt_diff >= 0):
                    resvar.inthr = True
                elif(resvar.owntent[6] == False and resvar.alt_diff >= -p.avevalt and resvar.alt_diff <= 0):
                    resvar.inthr = True
            else:
                if(itf.inctest > 3):
                    itf.inctest = itf.inctest - 4
                itf.inctest = 2*itf.inctest
                if(itf.ifirm >= p.minfirm and itf.trtru <= p.avevtau[itf.lev]):
                    resvar.nominal_sep, resvar.increase_sep = increase_proj_check(resvar.owntent[6], p.vaccel, itf, g, p, resvar)
                    if(resvar.nominal_sep < p.avevalt):
                        if(itf.taur >= p.inc_tau_thr):
                            if(resvar.increase_sep >= resvar.nominal_sep + p.inc_add_sep):
                                itf.inctest +=1
                                if(itf.inctest in (3, 5, 7)):
                                    resvar.inthr = True
                        else:
                            if(itf.trtru >= p.inc_tau_thr):
                                resvar.inthr = True
        if(resvar.inthr == True and itf.increase == False and itf.trtru > p.min_ri_time):
            if((resvar.owntent[6] == True and g.inc_desinhib == True) or (resvar.owntent[6] == False and g.anyincrease == False
            and (g.climbinhib == True))):
                pass
            else:
                if((g.clstrong == 8 and g.zdown <= p.inc_clmrate and g.zdmodel <= p.inc_clmrate) or (g.destrong == 8 and g.zdown >= p.inc_desrate and g.zdmodel >= p.inc_desrate)):
                    itf.increase, g.anyincrease = True, True
                    itf.tcmd = g.tcur
                    if(g.clstrong == 8):
                        g.zdmodel = p.inc_clmrate
                    else:
                        g.zdmodel = p.inc_desrate
    else:
        itf.increase = False
        itf.inctest = 0
"""VALID"""


"""VALID"""
def process_new_or_continuing_threat(itf, tf, TF, wl, g, p, resvar, DIL):
    if(g.tcur < (g.tlastnewra + p.tv1)):
        g.ttofollow = 0
    else:
        if(m.fabs(g.ttofollow) < 1e-10):
            g.ttofollow = m.fabs(g.zdown - g.zdmodel)/p.vaccel + p.tv1
    if(wl.status == CONT and m.fabs(itf.khit - 3) < 1e-10):
        reversal_check(itf, tf, g, p, resvar)
    select_advisory(itf, tf, wl, g, p, resvar)
    if(g.macflg == True):
        if(not np.array_equal(resvar.owntent, itf.tptr.permtent)):
            for i in range(len(resvar.owntent)):
                itf.tptr.permtent[i] = resvar.owntent[i]
    else:
        update_threat_file_own(itf, tf, TF, wl, g, resvar, DIL)
        resolution_update(resvar.oldpoi, resvar.optr, TF, g, resvar)
    if(wl.status == CONT and m.fabs(itf.khit - 3) < 1e-10):
        increase_check(itf, g, p, resvar)
"""VALID"""


"""VALID"""
def resolution(ITF, TF, wl, g, p, realtime, DIL, detvar, resvar):
    itf = wl.iptr
    tf = itf.tptr
    time_lock_begin = time.time()
    while (g.colock == True):
        if ((time.time() - time_lock_begin) > p.tunlock):
            assert ()
        time.sleep(0.01)
    g.colock = True
    g.tlock = realtime.tclock
    if(wl.status == TERM):
        update_threat_file_own(itf, tf, TF, wl, g, resvar, DIL)
        delete_resolution_advisory(resvar.oldpoi, TF, g, resvar)
        itf.reverse, itf.increase, itf.rev_ra = False, False, False
        itf.rrd_count = 0
    elif(wl.status == NEW):
        for i in range(len(resvar.owntent)):
            resvar.owntent[i] = False
        resvar.owntent[3] = True
        new_threat_file_entry(itf, ITF, TF, g, p, resvar)
        tf = itf.tptr
        select_sense(itf, tf, g, p, detvar, resvar)
        g.tlastnewra = g.tcur
    else:
        for i in range(len(resvar.owntent)):
            resvar.owntent[i] = tf.permtent[i]
    if(wl.status == NEW or wl.status == CONT):
        process_new_or_continuing_threat(itf, tf, TF, wl, g, p, resvar, DIL)
    g.colock = False
"""VALID"""