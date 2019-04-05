import numpy as np
import math as m
import time
import copy

from tcasClass import *
from tcasConstant import *

from tracking import pm
from detect import model_sep
from resolution import increase_proj_check, ramap, resolution_update

class Macvar:
    def __init__(self):
        """Group multiaircraft"""
        self.above = None #TRUE = intruder to pass above own (DESC sense)
        self.altdiff = None #Diff. between intruder's projected and own's current alt.
        self.below = None #TRUE = intruder to pass below own (CLIMB sense)
        self.can_reverse = None #Reversal possible during multiaircraft conflict
        self.clm_lev = None #Climb and then level-off modeling separation
        self.consider_reverse = None #Consider reversal during multiaircraft conflict
        self.cont_reverse = None #Consider reversal for a continuing threat
        self.converge_sep = None #Modeling separation against a maneuvering threat
        self.current_sense = None #Current RA sense against a threat
        self.des_lev = None #Descend and then level-off modeling separation
        self.descent_inhibited = None #Descend inhibited indicator
        self.dual_neg_ra = None #TRUE = RA should change from positive to negative
        self.increase_inhibited = None #Increase inhibited indicator
        self.increase_sep = None #Separation given increase RA
        self.increase_sep1 = None #Separation given increase RA for first threat
        self.increase_sep2 = None #Separation given increase RA for second threat
        self.lev_sep = None #Level-off separation
        self.level_off = None #Dual negative RA selection indicator
        self.macnptr = np.full(20, 0, dtype=int) #Pointer to new entry to add to RA array, TF.POOWRAR
        self.macoptr = np.full(20, 0, dtype=int) #Pointer to old entry to delete from RA array TF.POOWRAR
        self.malt1 = None #Separation given level-off sense versus one threat
        self.malt2 = None #Separation given level-off sense versus another threat
        self.min_nom_sep = None #Minimum separation given nominal RA
        self.min_rev_sep = None #Minimum separation given reversal RA
        self.n = None #Counter to NUMBPOI
        self.no_dual_negative = None #Indicates a dual negative sense is not selected
        self.nom_sep = None #Separation given nominal RA
        self.nominal_sep = None #Separation given nominal RA
        self.nominal_sep1 = None #Separation given nominal climb RA for first threat
        self.nominal_sep2 = None #Separation given nominal climb RA for second threat
        self.nominal_sep3 = None #Separation given nominal descend RA for first threat
        self.nominal_sep4 = None #Separation given nominal descend RA for second threat
        self.numbpoi = None #Number of advisory changes due to multiaircraft logic
        self.owntent = np.full(12, False, dtype=bool) #Advisory for WL (input) threat
        self.retain_end = None #End defer dual negative processing loop
        self.rev_sep = None #Reversal separation
        self.reverse = None #Reverse condition for a multiaircraft conflict
        self.rev1_sep = None #Reversal separation against one threat
        self.rev2_sep = None #Reversal separation against another threat
        self.rz_copy = None #Relative altitude
        self.sense = None #Sense of own versus threat
        self.true_tau = None #Value of true tau
        self.undo = None #Undo reversal condition indicator
        self.undo_sep = None #Modeling separation undone reversal
        self.zdgoal = None #Goal vertical rate


"""VALID"""
def dual_negative_sense_processing(wl, tf, itf, g, p, macvar, resvar):
    level_off = False
    macvar.clm_lev = model_sep(p.quikreac, 0, g.zown, g.zdown, p.vaccel, False, itf.zint, itf.zdint, itf, g, p, resvar)
    macvar.des_lev = model_sep(p.quikreac, 0, g.zown, g.zdown, p.vaccel, True, itf.zint, itf.zdint, itf, g, p, resvar)
    malt1 = min(m.fabs(macvar.clm_lev), m.fabs(macvar.des_lev))
    macvar.clm_lev = model_sep(p.quikreac, 0, g.zown, g.zdown, p.vaccel, False, tf.iptr.zint, tf.iptr.zdint, tf.iptr, g, p, resvar)
    macvar.des_lev = model_sep(p.quikreac, 0, g.zown, g.zdown, p.vaccel, True, tf.iptr.zint, tf.iptr.zdint, tf.iptr, g, p, resvar)
    malt2 = min(m.fabs(macvar.clm_lev), m.fabs(macvar.des_lev))
    if(malt1 >= p.lev_rev[g.layer] and malt2 >= p.lev_rev[g.layer]):
        level_off = True
        itf.retention = False
    return malt1, malt2, level_off
"""VALID"""


"""VALID"""
def multiaircraft_increase_inhib_test(sense, g):
    if((sense == True and g.inc_desinhib == True) or (sense == False and g.anyincrease == False and False)):
        increase_inhibited = True
    else:
        increase_inhibited = False
    return increase_inhibited
"""VALID"""


"""VALID"""
def increase_and_level_off_modeling(sense, malt1, malt2, level_off, itf, g, p, macvar):
    macvar.nominal_sep, macvar.increase_sep = increase_proj_check(sense, p.vaccel, itf, g, p, macvar)
    macvar.increase_inhibited = multiaircraft_increase_inhib_test(sense, g)
    if((macvar.increase_sep > malt1 or macvar.increase_sep > (malt1 + malt2)/2 or (macvar.increase_sep <= malt1
    and malt1 < p.lev_rev[g.layer]) or (macvar.increase_sep <= (malt1 + malt2)/2 and (malt1 + malt2)/2 < p.lev_rev[g.layer]))
    and macvar.increase_sep >= p.mac_inc[g.layer] and macvar.increase_inhibited == False):
        if((g.clstrold == 8 and g.clstrong == 8) or (g.destrold == 8 and g.destrong == 8)):
            itf.tcmd = g.tcur
            itf.mac_increase = True
        else:
            itf.increase_pending = True
    else:
        if(level_off == True and malt1 >= g.alim and malt2 >= g.alim):
            itf.retention =  False
        else:
            if(malt1 > malt2 and (malt1 + malt2)/2 >= p.lev_rev[g.layer]):
                itf.retention = True
    if(g.clstrong == 0 and g.destrong == 0):
        if(level_off == False and itf.retention == False and itf.increase_pending == False):
            itf.retention = True
"""VALID"""


"""VALID"""
def evaluate_displayed_resolution(itf, tf, wl, g, p, macvar, resvar):
    if(itf.sech >= p.mac_inc[g.layer]):
        for i in range(len(macvar.owntent)):
            macvar.owntent[i] = tf.permtent[i]
            itf.tptr.permtent[i] = tf.permtent[i]
        itf.tcmd = g.tcur
    else:
        macvar.malt1, macvar.malt2, macvar.level_off = dual_negative_sense_processing(wl, tf, itf, g, p, macvar, resvar)
        increase_and_level_off_modeling(tf.permtent[6], macvar.malt1, macvar.malt2, macvar.level_off, itf, g, p, macvar)
        if(itf.mac_increase == True):
            for i in range(len(macvar.owntent)):
                macvar.owntent[i] = tf.permtent[i]
                itf.tptr.permtent[i] = tf.permtent[i]
        if(macvar.level_off == False and itf.increase_pending == False and itf.retention == False and itf.mac_increase == False):
            itf.retention = True
            if(tf.iptr.eqp != TCAS):
                macvar.nominal_sep, macvar.increase_sep = increase_proj_check(macvar.owntent[6], p.raccel, tf.iptr, g, p, macvar)
                if(macvar.nominal_sep >= p.lev_rev[g.layer]):
                    for i in range(len(tf.permtent)):
                        tf.permtent[i] = macvar.owntent[i]
                    tf.iptr.tcmd = g.tcur
                    g.mac_reverse = True
                    g.maneuver_reversal = True
                    tf.iptr.rev_ra = True
                    itf.retention = False
            if(itf.retention == True and macvar.malt1 <= macvar.malt2):
                itf.retention = False
"""VALID"""


"""VALID2"""
def optimize_with_displayed_resolution(itf, TF, wl, g, p, macvar, resvar):
    if(((True in g.ra[:5]) and macvar.owntent[6] == True) or ((True in g.ra[5:10]) and macvar.owntent[6] == False)):
        for tf in TF:
            if(tf.permtent[3] == True and tf.permtent[6] != macvar.owntent[6]):
                evaluate_displayed_resolution(itf, tf, wl, g, p, macvar, resvar)
"""VALID2"""


"""VALID"""
def evaluate_simultaneous_threats(itf, tf, wl, g, p, macvar, resvar):
    if(itf.sech >= tf.iptr.sech or (tf.iptr.eqp == TCAS and g.idown > tf.iptr.idint)):
        if(itf.sech >= p.mac_inc[g.layer]):
            for i in range(len(macvar.owntent)):
                macvar.owntent[i] = tf.permtent[i]
                itf.tptr.permtent[i] = tf.permtent[i]
            itf.tcmd = g.tcur
        else:
            macvar.malt1, macvar.malt2, macvar.level_off = dual_negative_sense_processing(wl, tf, itf, g, p, macvar, resvar)
            increase_and_level_off_modeling(tf.permtent[6], macvar.malt1, macvar.malt2, macvar.level_off, itf, g, p, macvar)
    else:
        if(tf.iptr.sech >= p.mac_inc[g.layer]):
            for i in range(len(tf.permtent)):
                tf.permtent[i] = macvar.owntent[i]
            tf.iptr.tcmd = g.tcur
        else:
            macvar.malt1, macvar.malt2, macvar.level_off = dual_negative_sense_processing(wl, tf, itf, g, p, macvar, resvar)
            if(tf.iptr.eqp != TCAS):
                increase_and_level_off_modeling(macvar.owntent[6], macvar.malt1, macvar.malt2, macvar.level_off, tf.iptr, g, p, macvar)
"""VALID"""


"""VALID"""
def optimize_with_simultaneous_threats(itf, TF, wl, g, p, macvar, resvar):
    for tf in TF:
        if(tf.permtent[3] == True and tf.permtent[6] != macvar.owntent[6] and g.mac_new > 0):
            evaluate_simultaneous_threats(itf, tf, wl, g, p, macvar, resvar)
            if(tf.iptr.retention == True):
                itf.retention = True
                tf.iptr.retention = False
            if(itf.retention == True):
                if(itf.sech > tf.iptr.sech):
                    if(tf.iptr.eqp != TCAS or (tf.iptr.eqp == TCAS and g.idown < tf.iptr.idint)):
                        itf.retention = False
                        tf.iptr.retention = True
"""VALID"""


"""VALID"""
def resolution_retention_processing(itf, TF, wl, g, p, macvar, resvar):
    macvar.retain_end = False
    for tf in TF:
        if(macvar.retain_end != False):
            break
        if(tf.permtent[3] == True and tf.permtent[6] != macvar.owntent[6]):
            macvar.nominal_sep, macvar.increase_sep = increase_proj_check(tf.permtent[6], p.vaccel, itf, g, p, macvar)
            if(macvar.nominal_sep >= p.mac_inc[g.layer]):
                for i in range(len(macvar.owntent)):
                    macvar.owntent[i] = tf.permtent[i]
                    itf.tptr.permtent[i] = tf.permtent[i]
                itf.tcmd = g.tcur
                itf.increase_pending, itf.retention = False, False
            else:
                macvar.malt1, macvar.malt2, macvar.level_off = dual_negative_sense_processing(wl, tf, itf, g, p, macvar, resvar)
                macvar.increase_inhibited = multiaircraft_increase_inhib_test(tf.permtent[6], g)
                if((macvar.increase_sep > macvar.malt1 or macvar.increase_sep > (macvar.malt1 + macvar.malt2)/2
                or (macvar.increase_sep <= macvar.malt1 and macvar.malt1 < p.lev_rev[g.layer]) or (macvar.increase_sep <= (macvar.malt1 + macvar.malt2)/2
                and (macvar.malt1 + macvar.malt2)/2 < p.lev_rev[g.layer])) and macvar.increase_sep >= p.mac_inc[g.layer] and macvar.increase_inhibited == False):
                    if((g.clstrold == 8 and g.clstrong == 8)  or (g.destrold == 8 and g.destrong == 8)):
                        for i in range(len(macvar.owntent)):
                            macvar.owntent[i] = tf.permtent[i]
                            itf.tptr.permtent[i] = tf.permtent[i]
                        itf.tcmd = g.tcur
                        itf.mac_increase = True
                        itf.increase_pending = False
                        itf.retention = False
                    else:
                        itf.increase_pending = True
                        itf.retention = False
                else:
                    itf.increase_pending = False
                    if(macvar.malt1 <= macvar.malt2):
                        itf.retention = False
                    else:
                        itf.retention = True
            macvar.retain_end = True
"""VALID"""


"""VALID"""
def descend_inhib_test(sense, g):
    if(sense == True and g.nodescent == True):
        descent_inhibited = True
    else:
        descent_inhibited = False
    return descent_inhibited
"""VALID"""


"""VALID"""
def multiaircraft_reversal_test(sense, rz_copy, true_tau, itf, g, p, macvar, resvar):
    can_reverse = False
    nom_sep, rev_sep = 0, 0
    macvar.descent_inhibited = descend_inhib_test(sense, g)
    if(macvar.descent_inhibited == True):
        macvar.zdgoal = 0
    else:
        macvar.zdgoal = min(p.desrt, g.zdown)
    if(g.ra[0] == True and sense == False and (rz_copy <= -p.avevalt or (true_tau > p.minrvstime and rz_copy <= -p.crossthr))):
        nom_sep = model_sep(p.quikreac, max(p.clmrt, g.zdown), g.zown, g.zdown, p.vaccel, False, itf.zint, itf.zdint, itf, g, p, resvar)
        rev_sep = model_sep(p.quikreac, macvar.zdgoal, g.zown, g.zdown, p.raccel, True, itf.zint, itf.zdint, itf, g, p, resvar)
        can_reverse = True
    else:
        if(g.ra[5] == True and sense == True and (rz_copy >= p.avevalt or (true_tau > p.minrvstime and rz_copy >= p.crossthr))):
            nom_sep = model_sep(p.quikreac, macvar.zdgoal, g.zown, g.zdown, p.vaccel, True, itf.zint, itf.zdint, itf, g, p, resvar)
            rev_sep = model_sep(p.quikreac, max(p.clmrt, g.zdown), g.zown, g.zdown, p.raccel, False, itf.zint, itf.zdint, itf, g, p, resvar)
            can_reverse = True
    return nom_sep, rev_sep, can_reverse
"""VALID"""


"""VALID"""
def multiaircraft_avoidance_reversal_check(itf, TF, g, p, macvar, resvar):
    if(g.ra[0] == True or g.ra[5] == True):
        macvar.consider_reverse = True
        macvar.min_nom_sep = p.largeint
        macvar.min_rev_sep = p.largeint
        for tf in TF:
            if(macvar.consider_reverse != True):
                break
            if(tf.permtent[3] == True):
                if(tf.iptr.eqp != TCAS or (tf.iptr.eqp == TCAS and g.idown < tf.iptr.idint)):
                    macvar.nom_sep, macvar.rev_sep, macvar.can_reverse = multiaircraft_reversal_test(tf.permtent[6], tf.iptr.rz, tf.iptr.trtru, tf.iptr, g, p, macvar, resvar)
                    if(macvar.can_reverse == True):
                        macvar.min_nom_sep = min(macvar.min_nom_sep, macvar.nom_sep)
                        macvar.min_rev_sep = min(macvar.min_rev_sep, macvar.rev_sep)
                    else:
                        macvar.consider_reverse = False
        if(macvar.consider_reverse == True):
            if(macvar.min_rev_sep > macvar.min_nom_sep and macvar.min_rev_sep >= g.alim):
                pass
            else:
                if(macvar.min_nom_sep >= p.mac_inc[g.layer]):
                    macvar.consider_reverse = False
                else:
                    if(macvar.min_rev_sep >= (macvar.min_nom_sep + p.mac_hist1[g.layer])):
                        pass
                    else:
                        macvar.consider_reverse = False
        if(macvar.consider_reverse == True):
            for tf in TF:
                if(tf.permtent[3] == True):
                    if(tf.permtent[6]  == True):
                        tf.permtent[6] = False
                        tf.owntent[6] = False
                    else:
                        tf.permtent[6] = True
                        tf.owntent[6] = True
                    itf.tcmd = g.tcur
                    tf.iptr.tcmd = g.tcur
                    if(tf.iptr.eqp == TCAS):
                        tf.iptr.rev_geom = True
                    tf.iptr.rev_ra = True
                    tf.iptr.increase = False
                    tf.iptr.mac_increase = False
            g.mac_reverse = True
            g.maneuver_reversal = True
"""VALID"""


"""VALID"""
def maneuver_negative_selection(undo_sep, lev_sep, rev_sep, increase_inhibited, itf, tf, owntent, g, p, macvar):
    macvar.reverse = False
    if((undo_sep + p.mac_hist1[g.layer]) >= lev_sep and (undo_sep + p.mac_hist2[g.layer]) >= rev_sep):
        if(itf.rev_geom == True or itf.eqp != TCAS):
            if(owntent[6] == True):
                owntent[6], itf.tptr.permtent[6] = False, False
            else:
                owntent[6], itf.tptr.permtent[6] = True, True
            if(increase_inhibited == False):
                itf.mac_increase = True
            itf.reverse = False
            itf.rev_geom = False
            if(g.maneuver_reversal == False):
                itf.rev_ra = False
        else:
            if(m.fabs(rev_sep) > 1e-10 and rev_sep > (lev_sep + p.mac_hist1[g.layer])):
                macvar.reverse = True
            else:
                itf.tcmd = g.tcur
    else:
        if(m.fabs(rev_sep) > 1e-10 and rev_sep > (lev_sep + p.mac_hist1[g.layer])):
            macvar.reverse = True
        else:
            itf.tcmd = g.tcur
    if(macvar.reverse == True):
        for i in range(len(tf.permtent)):
            tf.permtent[i] = owntent[i]
        itf.tcmd = g.tcur
        tf.iptr.tcmd = g.tcur
        g.maneuver_reversal = True
        g.mac_reverse = True
        itf.rev_ra = True
        tf.iptr.rev_ra = True
        itf.reverse = False
        tf.iptr.reverse = False
        itf.increase, itf.mac_increase = False, False
        tf.iptr.increase, tf.iptr.mac_increase = False, False
        if(tf.iptr.eqp == TCAS):
            tf.iptr.rev_geom = True
"""VALID"""


"""VALID"""
def multiaircraft_level_off_maneuver(wl, itf, tf, owntent, g, p, macvar, resvar):
    macvar.sense = False
    macvar.malt1, macvar.malt2, macvar.level_off = dual_negative_sense_processing(wl, tf, itf, g, p, macvar, resvar)
    itf.retention = False
    macvar.lev_sep = min(macvar.malt1, macvar.malt2)
    if(tf.iptr.reverse == True):
        if(tf.permtent[6] == True):
            macvar.sense = False
        else:
            macvar.sense = True
    else:
        macvar.sense = tf.permtent[6]
    macvar.increase_inhibited = multiaircraft_increase_inhib_test(macvar.sense, g)
    macvar.nominal_sep1, macvar.increase_sep1 = increase_proj_check(macvar.sense, p.vaccel, tf.iptr, g, p, macvar)
    macvar.nominal_sep2, macvar.increase_sep2 = increase_proj_check(macvar.sense, p.vaccel, itf, g, p, macvar)
    if(macvar.increase_inhibited == True):
        macvar.undo_sep = min(macvar.nominal_sep1, macvar.nominal_sep2)
    else:
        macvar.undo_sep = min(macvar.increase_sep1, macvar.increase_sep2)
    if(tf.iptr.eqp != TCAS or (tf.iptr.eqp == TCAS and g.idown < tf.iptr.idint)):
        macvar.nominal_sep1, macvar.increase_sep = increase_proj_check(owntent[6], p.raccel, tf.iptr, g, p, macvar)
        macvar.nominal_sep2, macvar.increase_sep = increase_proj_check(owntent[6], p.raccel, itf, g, p, macvar)
        if(itf.eqp == TCAS and g.idown > itf.idint):
            macvar.rev_sep = macvar.nominal_sep1
        else:
            macvar.rev_sep = min(macvar.nominal_sep1, macvar.nominal_sep2)
    else:
        macvar.rev_sep = 0
    maneuver_negative_selection(macvar.undo_sep, macvar.lev_sep, macvar.rev_sep, macvar.increase_inhibited, itf, tf, owntent, g, p, macvar)
"""VALID"""


"""VALID"""
def maneuver_positive_selection(lev_sep, rev1_sep, rev2_sep, owntent, itf, tf, g, p, macvar):
    macvar.undo = False
    if(itf.rev_geom == True or itf.eqp != TCAS):
        if(rev2_sep != 0):
            if((lev_sep + p.mac_hist1[g.layer]) >= rev1_sep and (lev_sep + p.mac_hist1[g.layer]) >= rev2_sep):
                macvar.undo = True
            else:
                if(rev2_sep > rev1_sep):
                    if(tf.iptr.reverse == True):
                        for i in range(len(owntent)):
                            owntent[i] = tf.permtent[i]
                            itf.tptr.permtent[i] = tf.permtent[i]
                    else:
                        if(tf.permtent[6] == True):
                            tf.permtent[6], owntent[6], itf.tptr.permtent[6] = False, False, False
                        else:
                            tf.permtent[6], owntent[6], itf.tptr.permtent[6] = True, True, True
                        tf.iptr.reverse = True
                        tf.iptr.rev_ra = True
                        if(tf.iptr.eqp == TCAS):
                            tf.iptr.rev_geom = True
                        itf.reverse = False
                        itf.rev_ra = False
                        itf.rev_geom = False
                    tf.iptr.tcmd = g.tcur
                else:
                    itf.tcmd = g.tcur
        else:
            if((lev_sep + p.mac_hist1[g.layer]) >= rev1_sep):
                macvar.undo = True
            else:
                itf.tcmd = g.tcur
    else:
        itf.tcmd = g.tcur
    if(macvar.undo == True):
        if(owntent[6] == True):
            owntent[6], itf.tptr.permtent[6] = False, False
        else:
            owntent[6], itf.tptr.permtent[6] = True, True
        itf.reverse, itf.rev_geom, itf.rev_ra = False, False, False
    else:
        g.maneuver_reversal = True
"""VALID"""


"""VALID"""
def multiaircraft_positive_maneuver(wl, itf, tf, owntent, g, p, macvar, resvar):
    macvar.sense = False
    macvar.malt1, macvar.malt2, macvar.level_off = dual_negative_sense_processing(wl, tf, itf, g, p, macvar, resvar)
    itf.retention = False
    macvar.lev_sep = min(macvar.malt1, macvar.malt2)
    macvar.nominal_sep1, macvar.increase_sep = increase_proj_check(owntent[6], p.raccel, itf, g, p, macvar)
    macvar.nominal_sep2, macvar.increase_sep = increase_proj_check(owntent[6], p.raccel, tf.iptr, g, p, macvar)
    macvar.rev1_sep = min(macvar.nominal_sep1, macvar.nominal_sep2)
    if(tf.iptr.eqp != TCAS or (tf.iptr.eqp == TCAS and g.idown < tf.iptr.idint)):
        if(tf.iptr.reverse == False):
            if(tf.permtent[6] == True):
                macvar.sense = False
            else:
                macvar.sense = True
        else:
            macvar.sense = tf.permtent[6]
        macvar.nominal_sep3, macvar.increase_sep = increase_proj_check(macvar.sense, p.raccel, tf.iptr, g, p, macvar)
        macvar.nominal_sep4, macvar.increase_sep = increase_proj_check(macvar.sense, p.raccel, itf, g, p, macvar)
        macvar.rev2_sep = min(macvar.nominal_sep3, macvar.nominal_sep4)
    else:
        macvar.rev2_sep = 0
    maneuver_positive_selection(macvar.lev_sep, macvar.rev1_sep, macvar.rev2_sep, owntent, itf, tf, g, p, macvar)
"""VALID"""


"""VALID"""
def multiaircraft_converging_test(converge_sep, current_sense, tf, owntent, itf, wl, g, p, macvar, resvar):
    if(itf.valconvs > 3):
        itf.valconvs = itf.valconvs - 4
    itf.valconvs = 2*itf.valconvs
    macvar.altdiff = p.maxaltdiff
    if(m.fabs(g.zdown) > p.olev and m.fabs(itf.zdint) > p.olev and pm(g.zdown) != pm(itf.zdint)):
        macvar.altdiff = p.maxaltdiff2
    if(m.fabs(itf.rz) < m.fabs(itf.previous_rz) and (m.fabs(converge_sep) < (p.mac_inc[g.layer] - p.crossthr))
    and itf.ifirm >= p.minfirm and itf.trtru > p.min_ri_time and itf.a < macvar.altdiff):
        itf.valconvs += 1
        if(itf.valconvs in (3, 5, 7)):
            itf.reverse = True
            if(g.maneuver_reversal == False and itf.rev_ra == False):
                itf.rev_ra = True
    if(itf.reverse == True):
        itf.valconvs = 0
        itf.mac_increase = False
        itf.increase = False
        if(owntent[6] == True):
            owntent[6], itf.tptr.permtent[6] = False, False
        else:
            owntent[6], itf.tptr.permtent[6] = True, True
        tf.iptr.retention = False
        tf.iptr.increase_pending = False
        if(current_sense == True):
            multiaircraft_level_off_maneuver(wl, itf, tf, owntent, g, p, macvar, resvar)
        else:
            multiaircraft_positive_maneuver(wl, itf, tf, owntent, g, p, macvar, resvar)
    itf.previous_rz = itf.rz
"""VALID"""



"""VALID"""
def multiaircraft_converging_check(itf, TF, wl, g, p, macvar, resvar):
    macvar.can_reverse, macvar.current_sense = False, False
    for tf in TF:
        if(macvar.can_reverse != False):
            break
        if((g.ra[0] == True and macvar.owntent[6] == False) or (g.ra[5] == True and macvar.owntent[6] == True)):
            if(tf.permtent[3] == True and tf.permtent[6] == macvar.owntent[6] and wl.iptr != tf.iptr):
                macvar.descent_inhibited = descend_inhib_test(macvar.owntent[6], g)
                if(macvar.descent_inhibited == True):
                    macvar.zdgoal = 0
                else:
                    if(macvar.owntent[6] == False):
                        if(g.zdmodel >= p.inc_clmrate):
                            macvar.zdgoal = p.inc_clmrate
                        else:
                            macvar.zdgoal = max(g.zdown, p.clmrt)
                    else:
                        if(g.zdmodel <= p.inc_desrate):
                            macvar.zdgoal = p.inc_desrate
                        else:
                            macvar.zdgoal = min(g.zdown, p.desrt)
                macvar.clm_lev = model_sep(p.quikreac, macvar.zdgoal, g.zown, g.zdown, p.vaccel, False, itf.zint, itf.zdint, itf, g, p, resvar)
                macvar.des_lev = model_sep(p.quikreac, macvar.zdgoal, g.zown, g.zdown, p.vaccel, True, itf.zint, itf.zdint, itf, g, p, resvar)
                macvar.converge_sep = min(m.fabs(macvar.clm_lev), m.fabs(macvar.des_lev))
                macvar.current_sense = True
                multiaircraft_converging_test(macvar.converge_sep, macvar.current_sense, tf, macvar.owntent, itf, wl, g, p, macvar, resvar)
                macvar.can_reverse = True
        else:
            if(tf.permtent[3] == True and tf.permtent[6] != macvar.owntent[6] and wl.iptr != tf.iptr):
                macvar.clm_lev = model_sep(p.quikreac, 0, g.zown, g.zdown, p.vaccel, False, itf.zint, itf.zdint, itf, g, p, resvar)
                macvar.des_lev = model_sep(p.quikreac, 0, g.zown, g.zdown, p.vaccel, True, itf.zint, itf.zdint, itf, g, p, resvar)
                macvar.converge_sep = min(m.fabs(macvar.clm_lev), m.fabs(macvar.des_lev))
                macvar.current_sense = False
                multiaircraft_converging_test(macvar.converge_sep, macvar.current_sense, tf, macvar.owntent, itf, wl, g, p, macvar, resvar)
                macvar.can_reverse = True
"""VALID"""


"""VALID"""
def multiaircraft_reversal_maneuver_check(itf, TF, wl, g, p, macvar, resvar):
    for tf in TF:
        if(tf.permtent[3] == True):
            tf.iptr.retention = False
            tf.iptr.increase_pending = False
    macvar.can_reverse = False
    for tf in TF:
        if(macvar.can_reverse != False):
            break
        if((g.ra[0] == True and macvar.owntent[6] == True) or (g.ra[5] == True and macvar.owntent[6] == False)):
            if(tf.permtent[3] == True and tf.permtent[6] != macvar.owntent[6] and wl.iptr != tf.iptr):
                multiaircraft_level_off_maneuver(wl, itf, tf, macvar.owntent, g, p, macvar, resvar)
                macvar.can_reverse = True
        else:
            if(tf.permtent[3] == True and tf.permtent[6] == macvar.owntent[6] and wl.iptr != tf.iptr):
                multiaircraft_positive_maneuver(wl, itf, tf, macvar.owntent, g, p, macvar, resvar)
                macvar.can_reverse = True
"""VALID"""


"""VALID"""
def process_continuing_threats(itf, TF, wl, g, p, macvar, resvar):
    if((itf.increase_pending == True or itf.retention == True) and itf.reverse == False):
        resolution_retention_processing(itf, TF, wl, g, p, macvar, resvar)
    else:
        if(itf.reverse == False):
            multiaircraft_avoidance_reversal_check(itf, TF, g, p, macvar, resvar)
            multiaircraft_converging_check(itf, TF, wl, g, p, macvar, resvar)
        else:
            multiaircraft_reversal_maneuver_check(itf, TF, wl, g, p, macvar, resvar)
"""VALID"""


"""VALID"""
def evaluate_reversal_with_tcas_threat(itf, tf, wl, g, p, macvar, resvar):
    if(g.idown < itf.idint and itf.sech >= p.mac_inc[g.layer]):
        for i in range(len(macvar.owntent)):
            macvar.owntent[i] = tf.permtent[i]
            itf.tptr.permtent[i] = tf.permtent[i]
        itf.tcmd = g.tcur
    else:
        macvar.malt1, macvar.malt2, macvar.level_off = dual_negative_sense_processing(wl, tf, itf, g, p, macvar, resvar)
        if(macvar.level_off == False):
            macvar.no_dual_negative = True
"""VALID"""


"""VALID2"""
def multiaircraft_reversal_with_tcas_threat(itf, TF, wl, g, p, macvar, resvar):
    macvar.no_dual_negative = False
    if(((True in g.ra[:6]) and macvar.owntent[6] == True) or ((True in g.ra[5:11]) and macvar.owntent[6] == False)):
        for tf in TF:
            if(tf.permtent[3] == True and tf.permtent[6] != macvar.owntent[6]):
                evaluate_reversal_with_tcas_threat(itf, tf, wl, g, p, macvar, resvar)
            if(macvar.no_dual_negative == True):
                macvar.no_dual_negative = False
                itf.retention = True
                if(tf.iptr.eqp != TCAS):
                    macvar.nominal_sep, macvar.increase_sep = increase_proj_check(macvar.owntent[6], p.raccel, tf.iptr, g, p, macvar)
                    if(macvar.nominal_sep >= p.lev_rev[g.layer]):
                        for i in range(len(tf.permtent)):
                            tf.permtent[i] = macvar.owntent[i]
                        tf.iptr.tcmd = g.tcur
                        g.mac_reverse = True
                        g.maneuver_reversal = True
                        tf.iptr.rev_ra = True
                        itf.retention = False
                if(itf.retention == True and (macvar.malt1 <= macvar.malt2 or macvar.malt2 >= p.lev_rev[g.layer])):
                    itf.retention = False
"""VALID2"""


"""VALID"""
def evaluate_with_tcas_threat(itf, tf, wl, g, p, macvar, resvar):
    if(g.idown < itf.idint and (itf.sech >= tf.iptr.sech or (tf.iptr.eqp == TCAS and g.idown > tf.iptr.idint))):
        if(itf.sech >= p.mac_inc[g.layer]):
            for i in range(len(macvar.owntent)):
                macvar.owntent[i] = tf.permtent[i]
                itf.tptr.permtent[i] = tf.permtent[i]
            itf.tcmd = g.tcur
        else:
            macvar.malt1, macvar.malt2, macvar.level_off = dual_negative_sense_processing(wl, tf, itf, g, p, macvar, resvar)
    else:
        if(tf.iptr.eqp != TCAS or (tf.iptr.eqp == TCAS and g.idown < tf.iptr.idint)):
            if(tf.iptr.sech >= p.mac_inc[g.layer]):
                for i in range(len(tf.permtent)):
                    tf.permtent[i] = macvar.owntent[i]
                tf.iptr.tcmd = g.tcur
            else:
                macvar.malt1, macvar.malt2, macvar.level_off = dual_negative_sense_processing(wl, tf, itf, g, p, macvar, resvar)
                if(tf.iptr.eqp != TCAS):
                    increase_and_level_off_modeling(macvar.owntent[6], macvar.malt1, macvar.malt2, macvar.level_off, tf.iptr, g, p, macvar)
"""VALID"""


"""VALID"""
def multiaircraft_processing_with_tcas_threat(itf, TF, wl, g, p, macvar, resvar):
    for tf in TF:
        if(tf.permtent[3] == True and tf.permtent[6] != macvar.owntent[6] and g.mac_new > 0):
            evaluate_with_tcas_threat(itf, tf, wl, g, p, macvar, resvar)
            if(tf.iptr.retention == True and g.idown < itf.idint):
                itf.retention = True
                tf.iptr.retention = False
            if(itf.retention == True):
                if(itf.sech > tf.iptr.sech):
                    if(tf.iptr.eqp != TCAS or (tf.iptr.eqp == TCAS and g.idown < tf.iptr.idint)):
                        itf.retention = False
                        tf.iptr.retention = True
                else:
                    if(g.idown < itf.idint):
                        tf.iptr.retention = False
                        itf.retention = True
"""VALID"""


"""VALID"""
def evaluate_retention(itf, tf, wl, g, p, macvar, resvar):
    macvar.nominal_sep, macvar.increase_sep = increase_proj_check(tf.permtent[6], p.vaccel, itf, g, p, macvar)
    if((itf.eqp == TCAS and g.idown < itf.idint) and macvar.nominal_sep >= p.mac_inc[g.layer]):
        for i in range(len(macvar.owntent)):
            macvar.owntent[i] = tf.permtent[i]
            itf.tptr.permtent[i] = tf.permtent[i]
        itf.tcmd = g.tcur
        itf.rev_geom = True
        itf.retention = False
    else:
        macvar.malt1, macvar.malt2, macvar.level_off = dual_negative_sense_processing(wl, tf, itf, g, p, macvar, resvar)
"""VALID"""



"""VALID"""
def tcas_retention_processing(itf, TF, wl, g, p, macvar, resvar):
    macvar.level_off = False
    macvar.retain_end = False
    for tf in TF:
        if(macvar.retain_end != False):
            break
        evaluate_retention(itf, tf, wl, g, p, macvar, resvar)
        if(macvar.level_off == False):
            if(tf.iptr.eqp != TCAS):
                macvar.nominal_sep, macvar.increase_sep = increase_proj_check(macvar.owntent[6], p.raccel, tf.iptr, g, p, macvar)
                if(macvar.nominal_sep >= p.lev_rev[g.layer]):
                    for i in range(len(tf.permtent)):
                        tf.permtent[i] = macvar.owntent[i]
                    tf.iptr.tcmd = g.tcur
                    g.mac_reverse = True
                    g.maneuver_reversal = True
                    tf.iptr.rev_ra = True
                    itf.retention = False
            if(itf.retention == True and macvar.malt1 <= macvar.malt2):
                itf.retention = False
        macvar.retain_end = True
"""VALID"""


"""VALID2"""
def process_tcas_equipped_threat(itf, TF, wl, g, p, macvar, resvar):
    if(wl.status == NEW):
        if(g.clstrong != 0 or g.destrong != 0):
            multiaircraft_reversal_with_tcas_threat(itf, TF, wl, g, p, macvar, resvar)
        else:
            multiaircraft_processing_with_tcas_threat(itf, TF, wl, g, p, macvar, resvar)
    else:
        if(itf.retention == True and itf.reverse == False):
            tcas_retention_processing(itf, TF, wl, g, p, macvar, resvar)
        else:
            if(itf.reverse == True):
                multiaircraft_reversal_maneuver_check(itf, TF, wl, g, p, macvar, resvar)
"""VALID2"""


"""VALID2"""
def multiaircraft_modeling_and_evaluation(itf, TF, wl, g, p, macvar, resvar):
    if(wl.status == NEW and itf.eqp != TCAS):
        if(g.clstrong != 0 or g.destrong != 0):
            optimize_with_displayed_resolution(itf, TF, wl, g, p, macvar, resvar)
        else:
            optimize_with_simultaneous_threats(itf, TF, wl, g, p, macvar, resvar)
    else:
        if(itf.eqp != TCAS):
            process_continuing_threats(itf, TF, wl, g, p, macvar, resvar)
        else:
            process_tcas_equipped_threat(itf, TF, wl, g, p, macvar, resvar)
    g.mac_new += 1
"""VALID2"""


"""VALID"""
def multiaircraft_loop_on_threat_file(TF, g, macvar):
    for tf in TF:
        if(tf.permtent[3] == True):
            if(macvar.dual_neg_ra != tf.permtent[4]):
                tf.permtent[4] = macvar.dual_neg_ra
                tf.permtent[5] = False
                tf.permtent[10] = False
                tf.permtent[11] = False
            if(macvar.dual_neg_ra == True):
                tf.iptr.mac_increase = False
                tf.iptr.increase = False
                if(g.mac_new == g.threat_count):
                    tf.iptr.rev_ra = False
            if(tf.iptr.retention == True or tf.iptr.increase_pending == True):
                tf.poowrar = ramap(tf.permtent)
            else:
                if(tf.poowrar != ramap(tf.permtent)):
                    if(g.mac_new < g.threat_count and ((g.clstrong == 0 and g.destrong == 0) or g.man_reverse == True or tf.iptr.retention == False or tf.iptr.increase_pending == False)):
                        pass
                    else:
                        macvar.numbpoi += 1
                        macvar.macoptr[macvar.numbpoi-1] = tf.poowrar
                        tf.poowrar = ramap(tf.permtent)
                        macvar.macnptr[macvar.numbpoi-1] = tf.poowrar
                        tf.iptr.tcmd = g.tcur
    if(macvar.dual_neg_ra == True and g.mac_new == g.threat_count):
        g.maneuver_reversal = False
"""VALID"""


"""VALID2"""
def multiaircraft_resolution_optimization(itf, tf_c, TF, wl, g, p, macvar):
    macvar.above, macvar.below = False, False
    for tf in TF:
        if(tf.permtent[3] == True and tf.iptr.retention == False and tf.iptr.increase_pending == False):
            if(wl.iptr == tf.iptr):
                if(macvar.owntent[6] == True):
                    macvar.above = True
                else:
                    macvar.below = True
            else:
                if(tf.permtent[6] == True):
                    macvar.above = True
                else:
                    macvar.below = True
    macvar.cont_reverse = False
    for tf in TF:
        if(tf.permtent[3] == True):
            if(tf.iptr.mac_increase == True):
                tf.iptr.increase = True
                g.anyincrease = True
                if(g.previncrease == False):
                    itf.tcmd = g.tcur
                if(g.clstrong == 8):
                    g.zdmodel = p.inc_clmrate
                else:
                    g.zdmodel = p.inc_desrate
            if(tf.iptr.reverse == True):
                g.man_reverse = True
                if(wl.status == NEW and wl.iptr != tf.iptr):
                    macvar.cont_reverse = True
    if(g.mac_reverse == True):
        g.man_reverse = True
    for i in range(len(tf_c.permtent)):
        tf_c.permtent[i] = macvar.owntent[i]
    macvar.numbpoi = 0
    if(macvar.above == True and macvar.below == True):
        macvar.dual_neg_ra = True
    else:
        if(macvar.above == True and g.nodescent == True):
            macvar.dual_neg_ra = True
        else:
            macvar.dual_neg_ra = False
    multiaircraft_loop_on_threat_file(TF, g, macvar)
    for i in range(len(macvar.owntent)):
        macvar.owntent[i] = tf_c.permtent[i]
"""VALID2"""


"""VALID2"""
def multiaircraft_processing(TF, wl, g, p, realtime, macvar, resvar):
    itf = wl.iptr
    tf = itf.tptr
    time_lock_begin = time.time()
    while(g.colock == True):
        if ((time.time() - time_lock_begin) > p.tunlock):
            assert ()
        time.sleep(0.01)
    g.colock = True
    g.tlock = realtime.tclock
    for i in range(len(macvar.owntent)):
        macvar.owntent[i] = itf.tptr.permtent[i]
    multiaircraft_modeling_and_evaluation(itf, TF, wl, g, p, macvar, resvar)
    multiaircraft_resolution_optimization(itf,tf, TF, wl, g, p, macvar)
    if((wl.status == NEW and (g.clstrong != 0 or g.destrong != 0) and macvar.cont_reverse == False) or (g.mac_new == g.threat_count)):
        macvar.n = 1
        while(macvar.n <= macvar.numbpoi):
            resolution_update(macvar.macoptr[macvar.n-1], macvar.macnptr[macvar.n-1], TF, g, macvar)
            macvar.n += 1
    g.colock = False
"""VALID2"""