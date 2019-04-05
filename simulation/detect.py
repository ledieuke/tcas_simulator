import math as m
import time

from tcasClass import *
from tcasConstant import *

class Detvar:
    def __init__(self):
        """Group settable"""
        self.altdiff = None #Local copy of threshold used in Alt_separation_test
        self.dmod = None #Incremental range protection
        self.h1 = None #Range-range rate hyperbola threshold
        self.hmdthr = None #Horizontal miss distance threshold to be applied this cycle
        self.trthr = None #Range tau threshold
        self.tvpcmd = None #Max tau for VMD computation
        self.tvthr = None #Time-to-coaltitude threshold

        """Group flags"""
        self.hitflg = None #Hit/miss flag
        self.rhit = None #Range hit flag
        self.success = None #Set if matching Threat File entry is found for the intruder being processed
        self.zhit = None #Altitude hit flag

        """Group calaculated"""
        self.vertical_intent = None #Local copy of TCAS threat's vertical intent
        self.rdtemp = None #Temporary variable holding range rate or a range rate threshold
        self.taur_i = None #Integer floor of TAUR
        self.t1 = None #Intermediate value of modified range tau
        self.t3 = None #Intermediate value of true range tau
        self.zdgoal = None #Goal rate associated with RA

        """Group badfirm_model"""
        self.zdihi = None #Upper vertical rate limit
        self.zdilo = None #Lower vertical rate limit
        self.zmpclm = None #Separation resulting from climb
        self.zmpdes = None #Separation resulting from descend

        """Group modeling"""
        self.z = None #Own altitude
        self.zd = None #Own altitude rate
        self.zdi = None #Intruder rate bound
        self.zi = None #Intruder altitude

        """Group vmd_calc"""
        self.clip = None #Ceiling on taus
        self.relz = None #Relative altitude
        self.relzd = None #Relative altitude rate
        self.tau1 = None #Tau at end of critical interval
        self.tau2 = None #Tau at beginning of critical interval
        self.vmd = None #Vertical miss distance
        self.vmd1 = None #Vertical miss distance at end of critical interval
        self.vmd2 = None #Vertical miss distance at beginning of critical interval


"""VALID"""
def pm(arg):
    if(arg >=0):
        return 1
    else:
        return -1
"""VALID"""


"""VALID2"""
def set_detection_parameters(itf, g, p, detvar):
    if(itf.khit == 0):
        itf.lev = max(g.index, itf.plint)
    else:
        itf.lev = max(max(g.index, itf.plint), itf.lev)
    detvar.dmod = p.dmodtbl[itf.lev]
    detvar.tvpcmd = p.tvpctbl[itf.lev]
    detvar.h1 = p.h1tbl[itf.lev]
    if(itf.eqp == TCAS):
        detvar.trthr = p.trtetbl[itf.lev]
    else:
        detvar.trthr = p.trtutbl[itf.lev]
    if(m.fabs(g.zdown) <= p.olev):
        detvar.tvthr = p.tvvtt_tbl[itf.lev]
    else:
        if(((g.zdown*itf.zdint) >= 0) and (m.fabs(g.zdown) < m.fabs(itf.zdint))):
            detvar.tvthr = p.tvvtt_tbl[itf.lev]
        else:
            if(itf.eqp == TCAS):
                detvar.tvthr = p.tvtetbl[itf.lev]
            else:
                detvar.tvthr = p.tvtutbl[itf.lev]
    detvar.altdiff = p.maxaltdiff
    if(m.fabs(g.zdown) > p.olev and m.fabs(itf.zdint) > p.olev and pm(g.zdown) != pm(itf.zdint)):
        detvar.altdiff = p.maxaltdiff2
"""VALID2"""


"""VALID2"""
def tau_calculation(itf, g, p, detvar):
    if(itf.r > detvar.dmod):
        detvar.t1 = -(itf.r-((detvar.dmod**2)/itf.r))/detvar.rdtemp
    else:
        detvar.t1 = p.mintau
    detvar.t3 = -itf.r/detvar.rdtemp
    if(itf.taucap == True):
        if(detvar.t3 < itf.trtun):
            itf.taurise = 0
        else:
            if(itf.r > p.nafrange or (g.clstrong == 8 and g.clstrold == 8) or (g.destrong == 8 and g.destrold == 8)):
                itf.taurise += 1
        itf.taur = min(detvar.t1,itf.taur)
        itf.trtru = min(detvar.t3,itf.trtru)
    else:
        itf.taur = detvar.t1
        itf.trtru = detvar.t3
        itf.taurise = 0
    itf.taur = max(p.mintau, itf.taur)
    itf.trtru = max(p.mintau, itf.trtru)
    itf.trtun = detvar.t3
    if(itf.hfirm >= p.mininithfirm):
        itf.taucap = True
"""VALID2"""


"""VALID2"""
def range_test(itf, g, p, detvar):
    if(itf.rd > p.rdthr):
        itf.taur = p.mintau
        itf.trtru = p.mintau
        itf.tauv = p.mintau
        itf.taucap = False
        if((itf.r*itf.rd > detvar.h1 or itf.r > detvar.dmod) and ((itf.khit == 0) or itf.init == True)):
            detvar.rhit = False
            if(itf.khit == 0):
                itf.levelwait = 0
        else:
            detvar.rhit = True
    else:
        if(itf.rd >= -p.rdthr):
            detvar.rdtemp = -p.rdthr
        tau_calculation(itf, g, p, detvar)
        if(itf.taur < detvar.trthr and itf.r <= p.rmax):
            detvar.rhit = True
        else:
            detvar.rhit = False
    if(detvar.rhit == True and itf.khit == 0 and itf.taurise >= p.taurise_thr and itf.r >= detvar.dmod):
        detvar.rhit = False
    detvar.taur_i = m.floor(itf.taur)
    detvar.taur_i = max(detvar.taur_i,0)
    if(detvar.taur_i < p.trtetbl[7]):
        if(itf.khit > 0):
            detvar.hmdthr = p.hmdmult*detvar.dmod
        else:
            detvar.hmdthr = p.hmdthr[itf.lev][detvar.taur_i + 1]
        if(itf.hmd > detvar.hmdthr):
            itf.mdf_hit_count += 1
        else:
            itf.mdf_hit_count = 0
        if(((itf.khit > 0) and (itf.mdf_hit_count > p.tmin_mdf[g.index])) or ((itf.khit == 0) and (itf.mdf_hit_count > 0))):
            detvar.rhit = False
    if(detvar.rhit == True and itf.khit > 1 and itf.rd > 0 and ((itf.r*itf.rd) <= detvar.h1) and itf.r <= detvar.dmod):
        itf.rrd_count += 1
    else:
        itf.rrd_count = 0
"""VALID2"""


"""VALID2"""
def vertical_miss_distance_calculation(relz, relzd, tau1, tau2, clip):
    vmd1 = relz + relzd*min(clip,tau1)
    vmd2 = relz + relzd*min(clip,tau2)
    if(vmd1*vmd2 <= 0):
        vmd = 0
    elif(vmd1 > 0):
        vmd = min(vmd1, vmd2)
    else:
        vmd = max(vmd1, vmd2)
    return vmd
"""VALID2"""


"""VALID"""
def altitude_test(itf, g, p, detvar):
    if(itf.a < g.zthr):
        if(m.fabs(itf.vmd) < g.zthr):
            detvar.zhit = True
        else:
            detvar.zhit = False
    else:
        if(itf.adot >= p.zdthr):
            detvar.zhit = False
        else:
            itf.tauv = -itf.a/itf.adot
            if(itf.tauv < detvar.tvthr and ((m.fabs(itf.vmd) < g.zthr) or (itf.tauv < itf.trtru))):
                detvar.zhit = True
            else:
                detvar.zhit = False
    if(detvar.zhit == True and m.fabs(itf.zdint) > p.maxzdint):
        detvar.zhit = False
"""VALID"""


"""VALID"""
def project_vertical_given_zdgoal(tproj, z, zd, zdgoal, delay, accel, resvar):
    resvar.tdgr = m.fabs(zdgoal - zd)/accel
    resvar.tacc = max(0, min(tproj - delay, resvar.tdgr))
    resvar.tagr = max(0, tproj - delay - resvar.tdgr)
    if(zd < zdgoal):
        direction = 1
    else:
        direction = -1
    vproj = z + zd*min(delay, tproj) + (zd + 0.5*direction*accel*resvar.tacc)*resvar.tacc + zdgoal*resvar.tagr
    vdproj = zd + direction*accel*resvar.tacc
    return vproj, vdproj
"""VALID"""


"""VALID"""
def project_over_interval(z, zd, zdgoal, delay, trtlim, taulim, accel, resvar):
    zpr1, resvar.zdproj = project_vertical_given_zdgoal(trtlim, z, zd, zdgoal, delay, accel, resvar)
    zpr2, resvar.zdproj = project_vertical_given_zdgoal(taulim, z, zd, zdgoal, delay, accel, resvar)
    return zpr1, zpr2
"""VALID"""


"""VALID"""
def model_sep(delay, zdgoal, z ,zd, accel, sense, zi, mzdint, itf, g, p, resvar):
    resvar.trtlim = min(itf.trtru, p.tvpetbl[itf.lev])
    resvar.taulim = min(itf.taur, p.tvpetbl[itf.lev])
    resvar.zown1, resvar.zown2 = project_over_interval(z, zd, zdgoal, delay, resvar.trtlim, resvar.taulim, accel, resvar)
    resvar.zint1, resvar.zint2 = project_over_interval(zi, mzdint, mzdint, 0, resvar.trtlim, resvar.taulim, accel, resvar)
    resvar.zint1 = max(resvar.zint1, g.zground)
    resvar.zint2 = max(resvar.zint2, g.zground)
    if(sense == False):
        zmp = min(resvar.zown1 - resvar.zint1, resvar.zown2 - resvar.zint2)
    else:
        if(g.nodescent == False):
            resvar.zown1 = max(resvar.zown1, g.zground + p.zdesbot)
            resvar.zown2 = max(resvar.zown2, g.zground + p.zdesbot)
        zmp = min(resvar.zint1 - resvar.zown1, resvar.zint2 - resvar.zown2)
    if(zd < zdgoal):
        resvar.direction = 1
    else:
        resvar.direction = -1
    resvar.tm = delay - resvar.direction * (zd - mzdint)/accel
    resvar.tdgr = m.fabs(zdgoal - zd)/accel
    if(delay <= resvar.tm and resvar.tm <= (delay + resvar.tdgr)):
        if(resvar.taulim <= resvar.tm and resvar.tm <= resvar.trtlim):
            resvar.zmptm = z - zi + (zd - mzdint)*delay - (resvar.direction*(zd - mzdint)*(zd - mzdint))/(2*accel)
            if(sense == True):
                resvar.zmptm = -resvar.zmptm
            zmp = min(zmp, resvar.zmptm)
    return zmp
"""VALID"""


"""VALID"""
def model_maneuvers(itf, g, p, detvar, resvar):
    resvar.delay = p.tv1
    if((True in g.ra[:10]) and (itf.own_cross == False)):
        resvar.delay = max(p.tv1 - (g.tcur - g.tlastnewra), p.quikreac)
    if((g.climbinhib == True) or ((True in g.ra[5:10]) and (itf.own_cross == False))):
        detvar.zdgoal = 0
    else:
        detvar.zdgoal = max(min(g.zdown, p.maxdrate), p.clmrt)
    zmpclm = model_sep(resvar.delay, detvar.zdgoal, g.zown, g.zdown, p.vaccel, False, itf.zint, itf.zdint, itf, g, p, resvar)
    if((g.nodescent == True) or ((True in g.ra[:5]) and (itf.own_cross == False))):
        detvar.zdgoal = 0
    else:
        detvar.zdgoal = min(max(g.zdown, p.mindrate), p.desrt)
    zmpdes = model_sep(resvar.delay, detvar.zdgoal, g.zown, g.zdown, p.vaccel, True, itf.zint, itf.zdint, itf, g, p, resvar)
    return zmpclm, zmpdes
"""VALID"""


"""VALID"""
def avoid_tcas_tcas_crossings(itf, g, p, detvar):
    if((m.fabs(itf.zdint) > p.olev) and (m.fabs(g.zdown) <= p.olev)):
        if(itf.levelwait <= p.wtthr):
            itf.levelwait += 1
            detvar.hitflg = False
"""VALID"""


"""VALID"""
def alt_separation_test(itf, g, p, detvar, resvar):
    detvar.z, detvar.zd = project_vertical_given_zdgoal(p.tv1 + m.fabs(g.zdown/p.vaccel), g.zown, g.zdown, 0, p.tv1, p.vaccel, resvar)
    detvar.zi, detvar.zdi = project_vertical_given_zdgoal(p.tv1 + m.fabs(g.zdown/p.vaccel), itf.zint, itf.zdint, itf.zdint, p.tv1, p.vaccel, resvar)
    detvar.zmpclm, detvar.zmpdes = model_maneuvers(itf, g, p, detvar, resvar)
    if(detvar.zmpclm > detvar.zmpdes):
        if((itf.rz <= -p.crossthr) and ((g.zdown > 0 and detvar.z > (detvar.zi - p.crossthr)) or (detvar.zmpdes < g.alim))):
            if(itf.a > detvar.altdiff):
                detvar.hitflg = False
            if(itf.eqp == TCAS):
                avoid_tcas_tcas_crossings(itf, g, p, detvar)
    else:
        if((itf.rz >= p.crossthr) and ((g.zdown < 0 and detvar.z < (detvar.zi + p.crossthr)) or (detvar.zmpclm < g.alim))):
            if(itf.a > detvar.altdiff):
                detvar.hitflg = False
            if(itf.eqp == TCAS):
                avoid_tcas_tcas_crossings(itf, g, p, detvar)
"""VALID"""


"""VALID"""
def model_worst_rate_errors(itf, g, p, detvar, resvar):
    detvar.zdihi = max(itf.zdinr, itf.zdoutr)
    detvar.zdilo = min(itf.zdinr, itf.zdoutr)
    if(g.climbinhib == True or (True in g.ra[5:10])):
        detvar.zdgoal = 0
    else:
        detvar.zdgoal = max(min(g.zdown, p.maxdrate), p.clmrt)
    detvar.zmpclm = model_sep(p.tv1, detvar.zdgoal, g.zown, g.zdown, p.vaccel, False, itf.zint, detvar.zdihi, itf, g, p, resvar)
    if(g.nodescent == True or (True in g.ra[:5])):
        detvar.zdgoal = 0
    else:
        detvar.zdgoal = min(max(g.zdown, p.mindrate), p.desrt)
    detvar.zmpdes = model_sep(p.tv1, detvar.zdgoal, g.zown, g.zdown, p.vaccel, True, itf.zint, detvar.zdilo, itf, g, p, resvar)
"""VALID"""


"""VALID"""
def evaluate_low_firmness_separation(itf, g, p, detvar):
    if(max(detvar.zmpclm, detvar.zmpdes) > g.sensfirm):
        detvar.hitflg = True
        if(detvar.zmpclm > detvar.zmpdes):
            itf.badfok += 1
            itf.sech = detvar.zmpdes
        else:
            if(g.climbinhib == True and itf.rz >= -p.crossthr and (detvar.zmpclm + p.nozcross) > detvar.zmpdes):
                itf.badfok += 1
                itf.sech = detvar.zmpdes
            else:
                itf.badfok += 1
                itf.sech = detvar.zmpclm
        if(((itf.badfok == 1) and (itf.rz < -p.lowfirmrz)) or ((itf.badfok == -1) and (itf.rz > p.lowfirmrz))):
            if(itf.sech > g.sensfirm):
                itf.badfok = -itf.badfok
                if(itf.badfok == 1):
                    itf.sech = detvar.zmpdes
                else:
                    itf.sech = detvar.zmpclm
            else:
                detvar.hitflg = False
                itf.badfok = 0
                itf.sech = 0
"""VALID"""


"""VALID"""
def track_firmness_test(itf, ITF, TF, g, realtime, p, detvar, resvar):
    detvar.hitflg = False
    altitude_test(itf, g, p, detvar)
    if(itf.eqp == TCAS):
        detvar.vertical_intent = 0
        time_lock_begin = time.time()
        while(g.colock == True):
            if((time.time() - time_lock_begin) > p.tunlock):
                assert()
            time.sleep(0.01)
        g.colock = True
        g.tlock = realtime.tclock
        if(itf.tptr == None):
            detvar.success = False
            for tf in TF:
                if(detvar.success != False):
                    break
                elif(itf.idint == tf.id):
                    tf.iptr = ITF[itf.irow]
                    itf.tptr = tf
                    detvar.success = True
        if(itf.tptr != None):
            detvar.vertical_intent = itf.tptr.pothrar[0]
        g.colock = False
        if(detvar.vertical_intent != 0):
            if(((detvar.vertical_intent == 1 and itf.rz <= -p.crossthr) or (detvar.vertical_intent == 2 and itf.rz >= p.crossthr)) or (detvar.zhit == True)):
                detvar.hitflg = True
    if(detvar.hitflg == False and detvar.zhit == True):
        if((itf.eqp == TCAS) and (itf.valrep not in (3, 5, 7))):
            if(itf.levelwait > 0 and itf.levelwait <= p.wtthr):
                itf.levelwait += 1
        else:
            if(itf.ifirm >= p.minfirm):
                detvar.hitflg = True
                alt_separation_test(itf, g, p, detvar, resvar)
            else:
                model_worst_rate_errors(itf, g, p, detvar, resvar)
                evaluate_low_firmness_separation(itf, g, p, detvar)
                if((detvar.hitflg == False) and (itf.eqp == TCAS) and (itf.levelwait > 0) and (itf.levelwait <= p.wtthr)):
                    itf.levelwait += 1
            if(((itf.eqp == TCAS) and (g.tcur - g.ramode_on <= p.tiethr)) or (itf.hfirm < p.mininithfirm)):
                detvar.hitflg = False
    if(detvar.hitflg == True):
        itf.levelwait = 0
"""VALID"""


"""VALID2"""
def hit_or_miss_test(itf, ITF, TF, g, realtime, p, detvar, resvar):
    itf.rzd = g.zdown - itf.zdint
    detvar.rdtemp = itf.rd
    itf.adot = itf.rzd * pm(itf.rz)
    range_test(itf, g, p, detvar)
    if(itf.rd > 0):
        itf.vmd = itf.rz
    else:
        itf.vmd = vertical_miss_distance_calculation(itf.rz, itf.rzd, itf.trtru, itf.taur, detvar.tvpcmd)
    if(detvar.rhit == False):
        detvar.hitflg = False
        if(itf.khit == 1 and itf.tacode == RA):
            itf.clear_conflict = True
    else:
        if(itf.khit == 0):
            track_firmness_test(itf, ITF, TF, g, realtime, p, detvar, resvar)
        else:
            detvar.hitflg = True
            if(itf.r < 5):
                track_firmness_test(itf, ITF, TF, g, realtime, p, detvar, resvar)

"""VALID2"""


"""VALID2"""
def set_up_working_list(itf, WL, g, p, detvar):
    if(detvar.hitflg == True):
        itf.tacode = RA
        if(itf.khit == 0):
            WL.append(Wl(itf,NEW))
            itf.wptr = WL[-1]
        else:
            WL.append(Wl(itf,CONT))
            itf.wptr = WL[-1]
        itf.khit = 3
    else:
        itf.tacode = min(itf.tacode, TAMC)
        if(itf.khit > 0):
            if(itf.khit == 1):
                if((g.tcur - itf.tcmd) > p.tmin):
                    WL.append(Wl(itf, TERM))
                    itf.wptr = WL[-1]
                    itf.khit = 0
                else:
                    WL.append(Wl(itf, CONT))
                    itf.wptr = WL[-1]
                    itf.tacode = RA
                    itf.clear_conflict = False
            else:
                WL.append(Wl(itf, CONT))
                itf.wptr = WL[-1]
                itf.khit = 1
                itf.tacode = RA
    term, new, cont = [], [], []
    for wl in WL:
        if(wl.status == TERM):
            term.append(wl)
        elif(wl.status == NEW):
            new.append(wl)
        else:
            cont.append(wl)
    WL.clear()
    WL.extend(term)
    WL.extend(new)
    WL.extend(cont)
"""VALID2"""


"""VALID2"""
def test_for_multiaircraft_conflict(WL, g):
    g.macflg = False
    g.threat_count = 0
    for wl in WL:
        if(wl.status == NEW or wl.status == CONT):
            g.threat_count += 1
    if(g.threat_count > 1):
        g.macflg = True
    else:
        g.maneuver_reversal = False
"""VALID2"""


"""VALID2"""
def detect_conflicts(ITF,TF, WL, g, realtime, p, pm, detvar, resvar):
    for itf in ITF:
        if(itf.survmode == NORMAL):
            if(itf.ditf == True or (itf.altitude_lost == True and itf.khit > 0)):
                WL.append(Wl(itf,TERM))
                itf.wptr = WL[-1]
                itf.khit = 0
            else:
                if(itf.modc == True):
                    set_detection_parameters(itf, g, p, detvar)
                    hit_or_miss_test(itf, ITF, TF, g, realtime, p, detvar, resvar)
                    set_up_working_list(itf, WL, g, p, detvar)
        else:
            if(itf.tacode == RA):
                WL.append(Wl(itf,TERM))
                itf.wptr = WL[-1]
                itf.khit = 0
                itf.tacode = NOTAPA
    test_for_multiaircraft_conflict(WL, g)
"""VALID2"""