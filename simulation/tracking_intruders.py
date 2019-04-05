import math as m
import time
import sys

from tracking import vertical_tracking, pm
from tcasClass import *


"""VALID"""
def itf_entry_creation(ITF, g, s, p):
    itf = Itf()
    itf.irow = len(ITF)
    g.crefptr[s.survno] = itf.irow
    itf.crefno = s.survno
    itf.survmode = s.survmode
    itf.tptr, itf.wptr = None, None
    itf.idint = s.idintr
    itf.modc = s.modc
    itf.zrint = s.zrint
    itf.rrti = s.rrtime
    itf.dt = 0
    itf.r = s.rr
    itf.rd, itf.rdd, itf.rddd = 0, 0, 0
    itf.manct = 0
    itf.mdf_hit_count = 0
    itf.rl = s.rr
    itf.rdl = 0
    itf.rddl = 0
    itf.hfirm = 0
    if(s.bear_meas_ok == True):
        itf.hfirmb = 0
    else:
        itf.hfirmb = -1
    itf.dtb = 0
    itf.smoressq = p.ressd_n*p.ressd_n
    itf.init = False
    itf.initb = False
    itf.sgndpx = 1
    itf.numdpx = 0
    itf.xs = s.rr*m.sin(s.bear_meas)
    itf.ys = s.rr*m.cos(s.bear_meas)
    itf.xds, itf.yds = 0, 0
    itf.hmd, itf.hmdrb = 0, 0
    itf.khit, itf.arrow = 0, 0
    itf.ditf, itf.taucap = False, False
    itf.tatime = 0
    itf.reverse, itf.increase, itf.rev_ra = False, False, False
    itf.int_cross, itf.own_cross = False, False
    itf.increase_pending, itf.retention, itf.mac_increase = False, False, False
    for i in range(len(itf.permtent_copy)):
        itf.permtent_copy[i] = False
    itf.valconvs, itf.previous_rz = 0, 0
    itf.levelwait = 0
    itf.tacode = NOTAPA
    itf.valrep = 0
    itf.inctest = 0
    itf.clear_conflict, itf.altitude_lost = False, False
    itf.rrd_count = 0
    ITF.append(itf)
"""VALID"""


"""VALID"""
def update_range(sr, srd, srdd, dt):
    srp = sr + (srd*dt) + 0.5*(srdd*dt*dt)
    srdp = srd + srdd*dt
    srddp = srdd
    return srp, srdp, srddp
"""VALID"""


"""VALID"""
def project_hmd(sr, srd, srdd):
    hmdsq = sr**2 - (sr**2)*(srd**2)/(sr*srdd + srd**2)
    return hmdsq
"""VALID"""


"""VALID"""
def linear_extrap(itf, trackvar):
    trackvar.x = m.sqrt(trackvar.hmdsq)
    trackvar.ydot = m.sqrt(itf.rl * itf.rddl + (itf.rdl**2))
    trackvar.y = (itf.rl*itf.rddl)/trackvar.ydot + trackvar.ydot*itf.dt
    trackvar.rp_l = m.sqrt(trackvar.x**2 + trackvar.y**2)
    trackvar.rdp_l = (trackvar.y*trackvar.ydot)/trackvar.rp_l
    trackvar.rddp_l = (trackvar.x*trackvar.x*(trackvar.ydot**2))/(trackvar.rp_l**3)
"""VALID"""


"""VALID"""
def update_firmness(itf, p, trackvar):
    itf.hfirm = min(itf.hfirm + 1, p.maxf)
    trackvar.firm = itf.hfirm
    if((itf.init == False) and (trackvar.firm == p.maxf)):
        itf.init = True
"""VALID"""


"""VALID"""
def smoother(srp, srdp, srddp, dt, residual, alpha, beta, gamma, init):
    sr = srp + alpha*residual
    srd = srdp + (beta*residual)/dt
    if(init == True):
        srdd = srddp + (gamma*residual)/(dt**2)
    else:
        srdd = 0.
    return sr, srd, srdd
"""VALID"""


"""VALID"""
def calc_acc_thresh(itf, p, trackvar):
    if(itf.init == False):
        trackvar.rhoddthr = p.inithoddthr
        itf.smoressq = p.ressd_n*p.ressd_n
    else:
        itf.smoressq = p.alpharessq*(trackvar.resid**2) + (1-p.alpharessq)*itf.smoressq
        trackvar.ressd = m.sqrt(itf.smoressq)
        trackvar.rhoddthr = max(p.accthr, (p.accthr*trackvar.ressd)/p.ressd_n)
"""VALID"""


"""VALID"""
def smooth_range_third_derivative(itf, p, trackvar):
    if(m.fabs(itf.rddd) < 1e-10):
        trackvar.rddp = 0.
    itf.rddd =(1-p.alpha3d)*itf.rddd + p.alpha3d*(itf.rdd - trackvar.rddp)
"""VALID"""


"""VALID"""
def predict_covar(pr_noise, dt, cov):
    pcov = np.full((2,2),0.,dtype=float)
    pcov[(0,0)] = dt*dt*cov[(1,1)] + 2*dt*cov[(0,1)] + cov[(0,0)] + 0.25*pr_noise*dt**4
    pcov[(0,1)] = cov[(0,1)] + dt*cov[(1,1)]+ 0.5*pr_noise*dt**3
    pcov[(1,0)] = pcov[(0,1)]
    pcov[(1,1)] = cov[(1,1)] + pr_noise*dt**2
    return pcov
"""VALID"""


"""VALID"""
def predict_b_track_state_covar(itf, s, p, trackvar):
    trackvar.xp = itf.xs + itf.xds*itf.dtb
    trackvar.yp = itf.ys + itf.yds*itf.dtb
    if(s.bear_meas_ok == True):
        trackvar.sinb = m.sin(s.bear_meas)
        trackvar.cosb = m.cos(s.bear_meas)
    else:
        trackvar.temp = m.sqrt(trackvar.xp*trackvar.xp + trackvar.yp*trackvar.yp)
        trackvar.sinb = trackvar.xp/trackvar.temp
        trackvar.cosb = trackvar.yp/trackvar.temp
    trackvar.xm = s.rr*trackvar.sinb
    trackvar.ym = s.rr*trackvar.cosb
    trackvar.dp = s.rr - (trackvar.xp*trackvar.xm - trackvar.yp*trackvar.ym)/s.rr
    trackvar.dpx = (trackvar.xp*trackvar.ym - trackvar.yp*trackvar.xm)/s.rr
    trackvar.pcov = predict_covar(p.procnoivar, itf.dtb, itf.cov)
    trackvar.varxrng = s.rr*s.rr*p.vrbrng
    trackvar.temp = trackvar.pcov[(0,0)] + trackvar.varxrng
"""VALID"""


"""VALID"""
def bearing_track_maneuver_det(itf, s, p, trackvar):
    if(itf.initb == True):
        if((s.bear_meas_ok == True) and (itf.sgndpx*trackvar.dpx > 0) and m.fabs(trackvar.dpx) > (p.nsgsnct*m.sqrt(trackvar.pcov[(0,0)] + trackvar.varxrng))):
            itf.numdpx += 1
        else:
            if(trackvar.dpx < 0):
                itf.sgndpx = -1.
            else:
                itf.sgndpx = 1.
            itf.numdpx = 0
            if(m.fabs(trackvar.dpx) <= (p.nsgsnct*m.sqrt(trackvar.pcov[(0,0)] + trackvar.varxrng))):
                itf.sgndpx = 1.
        if((s.bear_meas_ok == True) and ((m.fabs(trackvar.dpx) > (p.mxsigdpx*m.sqrt(trackvar.temp))) or ((itf.numdpx > p.dpxconsec) and (m.fabs(trackvar.dpx) > (p.mnsigdpx*m.sqrt(trackvar.temp)))))):
            itf.initb = False
            itf.hfirmb = 0
        else:
            if((trackvar.maneuver == True) or (m.fabs(trackvar.dp) > p.maxrangeresid)):
                trackvar.pcov = predict_covar(p.procnoivar*p.p_noise_factor, itf.dtb, itf.cov)
                trackvar.temp = trackvar.pcov[(0,0)] + trackvar.varxrng
                itf.hfirmb = min(itf.hfirmb, p.bear_firm_sm_man)
"""VALID"""


"""VALID"""
def calc_b_track_gains(itf, s, p, trackvar):
    if(s.bear_meas_ok == False):
        trackvar.w1 = 0.
        trackvar.w2 = 0.
    else:
        if((itf.hfirmb == 0) and (itf.initb == False)):
            trackvar.w1 = 1.
            trackvar.w2 = 0.
        else:
            if((itf.hfirmb == 1) and (itf.initb == False)):
                trackvar.w1 = 1
                trackvar.w2 = 1
            else:
                trackvar.w1 = trackvar.pcov[(0,0)]/trackvar.temp
                trackvar.w2 = trackvar.pcov[(1,0)]/trackvar.temp
                if((trackvar.w1 > 1) or (trackvar.w2 > 1)):
                    trackvar.w1 = 1
                    trackvar.w2 = 1
    trackvar.alpha = p.alpharb[itf.hfirmb]
    trackvar.beta = p.betarb[itf.hfirmb]
"""VALID"""


"""VALID"""
def smooth_bearing_track(itf, s, trackvar):
    itf.xs = trackvar.xp + trackvar.alpha*trackvar.dp*trackvar.sinb - trackvar.w1*trackvar.dpx*trackvar.cosb
    itf.ys = trackvar.yp + trackvar.alpha*trackvar.dp*trackvar.cosb + trackvar.w1*trackvar.dpx*trackvar.sinb
    itf.xds = itf.xds + (trackvar.beta/itf.dtb)*trackvar.dp*trackvar.sinb - trackvar.w2*trackvar.dpx*trackvar.cosb
    itf.yds = itf.yds + (trackvar.beta/itf.dtb)*trackvar.dp*trackvar.cosb + trackvar.w2*trackvar.dpx*trackvar.sinb
    if(itf.hfirmb == 0):
        itf.xs = s.rr*m.sin(s.bear_meas)
        itf.ys = s.rr*m.cos(s.bear_meas)
        itf.xds = 0.
        itf.yds = 0.
    itf.cov[(0,0)] = (1 - trackvar.w1)*trackvar.pcov[(0,0)]
    itf.cov[(0,1)] = (1 - trackvar.w1)*trackvar.pcov[(0,1)]
    itf.cov[(1,0)] = itf.cov[(0,1)]
    itf.cov[(1,1)] = trackvar.pcov[(1,1)] - trackvar.w2*trackvar.pcov[(0,1)]
    if((itf.hfirmb == 1) and (itf.initb == False)):
        itf.cov[(0,0)] = trackvar.varxrng
        itf.cov[(1,1)] = (2*trackvar.varxrng)/(itf.dtb**2)
        itf.cov[(0,1)] = trackvar.varxrng/itf.dtb
        itf.cov[(1,0)] = itf.cov[(0,1)]
"""VALID"""


"""VALID"""
def rbtracker(itf, s, p, trackvar):
    predict_b_track_state_covar(itf, s, p, trackvar)
    bearing_track_maneuver_det(itf, s, p, trackvar)
    calc_b_track_gains(itf, s, p, trackvar)
    smooth_bearing_track(itf, s, trackvar)
    trackvar.temp = m.sqrt(itf.xds**2 + itf.yds**2)
    if(trackvar.temp > 0):
        itf.hmdrb = m.fabs(itf.xs*itf.yds - itf.ys*itf.xds)/trackvar.temp
    else:
        itf.hmdrb = m.sqrt(itf.xs**2 + itf.ys**2)
"""VALID"""


"""VALID"""
def detect_maneuvers(itf, s, p, trackvar):
    trackvar.maneuver = False
    if(itf.init == True):
        if((itf.rddd < 0) or (trackvar.resid_l < (-p.resdl_sigmas*max(p.ressd_c_exp_fact*p.ressd_n, trackvar.ressd)))
                or (itf.rdd < -trackvar.rhoddthr)):
            trackvar.maneuver = True
    if(s.bear_meas_ok == True):
        itf.hfirmb = min(itf.hfirmb + 1, p.maxf)
        if(itf.initb == False and itf.hfirmb == p.maxf):
            itf.initb = True
            itf.sgndpx = 1.
            itf.numdpx = 0.
    else:
        itf.hfirmb = max(itf.hfirmb - 1, -1)
        if(itf.hfirmb < p.mininithfirm):
            itf.initb = False
    if(s.bear_meas_ok == True or itf.initb == True):
        rbtracker(itf, s, p, trackvar)
    else:
        itf.hmdrb = p.bbcc_disable_val
        itf.hfirmb = -1
    if((itf.initb == True) and ((p.rbratio*itf.hmdrb) < itf.hmd)):
        trackvar.maneuver = True
    if(trackvar.maneuver == True):
        itf.manct = p.mnvr_shtdwn_tm
    else:
        itf.manct = max(0,itf.manct-1)
    if((itf.manct > 0) or (itf.init == False)):
        itf.hmd = p.hmd_disable_val
    else:
        if(itf.initb == True):
            itf.hmd = min(itf.hmd, itf.hmdrb)
    itf.hmd_last = itf.hmd
"""VALID"""


"""VALID"""
def miss_distance_calculations(itf, s, p, trackvar):
    calc_acc_thresh(itf, p, trackvar)
    itf.hmd = p.hmd_disable_val
    if(itf.rdd > trackvar.rhoddthr):
        trackvar.hmdsq = project_hmd(itf.r, itf.rd, itf.rdd)
        smooth_range_third_derivative(itf, p, trackvar)
        if(trackvar.hmdsq > 0):
            itf.hmd = m.sqrt(trackvar.hmdsq)
    else:
        itf.rddd = 0.
    detect_maneuvers(itf, s, p, trackvar)
"""VALID"""


"""VALID"""
def coast_horizontal_track(itf, p, trackvar):
    itf.hfirm -= 1
    itf.hfirm = max(0, itf.hfirm)
    itf.hfirmb -= 1
    itf.hfirmb = max(-1, itf.hfirmb)
    itf.hmd = itf.hmd_last - 0.5*p.coast_accel*(itf.dtb**2)
    if(itf.hfirm < p.mininithfirm):
        itf.init = False
    if(itf.hfirmb < p.mininithfirm):
        itf.initb = False
    itf.r = trackvar.rp
    itf.rd = trackvar.rdp
    itf.rl = trackvar.rp_l
    itf.rdl = trackvar.rdp_l
    itf.rddl = trackvar.rddp_l
"""VALID"""


"""VALID"""
def valid_report_test(itf):
    if(itf.valrep > 3):
        itf.valrep = itf.valrep - 4
    itf.valrep = 2*itf.valrep
    if(itf.rflg == True):
        itf.valrep = itf.valrep + 1
"""VALID"""


"""VALID"""
def horizontal_tracking(itf, s, p, trackvar):
    itf.dt = s.rrtime - itf.rrti
    itf.rrti = s.rrtime
    itf.dtb = itf.dtb + itf.dt
    trackvar.rp, trackvar.rdp, trackvar.rddp = update_range(itf.r, itf.rd, itf.rdd, itf.dt)
    trackvar.rp_l, trackvar.rdp_l, trackvar.rddp_l = update_range(itf.rl, itf.rdl, itf.rddl, itf.dt)
    trackvar.ressd = m.sqrt(itf.smoressq)
    trackvar.rhoddthr = max(p.accthr, (p.accthr*trackvar.ressd)/p.ressd_n)
    if((s.survmode == NORMAL) and (itf.rddl >= trackvar.rhoddthr)):
        trackvar.hmdsq = project_hmd(itf.rl, itf.rdl, itf.rddl)
        if(trackvar.hmdsq > 0.):
            linear_extrap(itf, trackvar)
    if(s.rflg == True):
        update_firmness(itf, p, trackvar)
        trackvar.resid = s.rr - trackvar.rp
        if(trackvar.firm >= 2):
            trackvar.dt = itf.dt
        else:
            trackvar.dt = itf.dtb
        itf.r, itf.rd, itf.rdd = smoother(trackvar.rp, trackvar.rdp, trackvar.rddp, trackvar.dt, trackvar.resid,
                                          p.alphap[trackvar.firm], p.betap[trackvar.firm], p.gammap[trackvar.firm],
                                          itf.init)
        trackvar.resid_l = s.rr - trackvar.rp_l
        itf.rl, itf.rdl, itf.rddl = smoother(trackvar.rp_l, trackvar.rdp_l, trackvar.rddp_l, trackvar.dt,
                                             trackvar.resid_l, p.alphal[trackvar.firm], p.betal[trackvar.firm],
                                             p.gammal[trackvar.firm], itf.init)
        trackvar.rdtemp = itf.rd
        if(itf.rd > -p.rdthr):
            trackvar.rdtemp = -p.rdthr
        trackvar.temp = -(itf.r - ((p.dmod_mdf*p.dmod_mdf)/itf.r))/trackvar.rdtemp
        if(s.survmode == NORMAL and (trackvar.temp < p.rb_tau_thresh or itf.r < p.dmod_mdf)):
            miss_distance_calculations(itf, s, p, trackvar)
        else:
            itf.hmd = p.hmd_disable_val
            itf.hfirmb = -1
            itf.initb = False
            if(s.survmode != NORMAL):
                itf.hfirm = 0
                itf.rdd = 0.
                itf.rddl = 0.
            itf.init = False
        itf.dtb = 0.
    else:
        coast_horizontal_track(itf, p, trackvar)
    if(itf.r < 0):
        itf.r = 0.
        itf.rd = max(0., itf.rd)
    itf.rflg = s.rflg
    valid_report_test(itf)
"""VALID"""


"""VALID"""
def set_arrow(itf):
    n = itf.nptr
    if(itf.modc == False):
        itf.arrow = 0
    elif(n.class_ == NEW_TRACK or n.class_ == OSCIL or n.class_ == LEVEL):
        itf.arrow = 0
    elif(n.class_ == TREND):
        itf.arrow = pm(itf.zdint)
"""VALID"""


def update_trackvar(trackvar, g, realtime, s):
    trackvar.zrept = float(s.zrint)
    trackvar.t = realtime.tclock


"""VALID"""
def itf_update(itf, g, s):
    if(s.modc == True):
        n = itf.nptr
        itf.ifirm = n.casfirm
        itf.badfok = 0
        itf.zint = n.z
        itf.zdint = n.zd
        itf.zdinr = n.zdinner
        itf.zdoutr = n.zdouter
        itf.rz = g.zown - itf.zint
        itf.a = m.fabs(itf.rz)
        if(s.zflg == True):
            itf.zrint = s.zrint
    else:
        if(itf.modc == True):
            if(itf.khit > 0 and itf.tacode == RA):
                itf.altitude_lost = True
            if(itf.tacode == TAMC or itf.tacode == RA):
                itf.tacode = TANMC
        itf.nptr = None
    itf.bearing = s.bear
    itf.bearok = s.bearok
    itf.modc = s.modc
    itf.survmode = s.survmode
    set_arrow(itf)
    itf.eqp = s.eqp
    itf.plint = s.plint
    itf.tdatai = g.tcur
"""VALID"""


"""VALID"""
def drop_tracks(ITF, g, realtime, p):
    time_lock_begin = time.time()
    while(g.colock == True):
        if((time.time() - time_lock_begin) > p.tunlock):
            assert()
        time.sleep(0.01)
    g.colock = True
    g.tlock = realtime.tclock
    for itf in ITF:
        if(m.fabs(g.tcur - itf.tdatai) > 1e-10):
            if(itf.tptr == None):
                g.crefptr[itf.crefno] = None
            else:
                if(itf.tptr.poowrar == 0):
                    g.crefptr[itf.crefno] = None
                    itf.tptr.iptr = None
            if(g.crefptr[itf.crefno] == None):
                itf.nptr = None
                ITF.remove(itf)
            else:
                itf.ditf = True
    g.colock = False
"""VALID"""


"""VALID"""
def track_intruders(ITF, STD, g, realtime, SList, p, pn, trackvar):
    for s in SList:
        update_trackvar(trackvar, g, realtime, s)
        if(g.crefptr[s.survno] == None):
            itf_entry_creation(ITF, g, s, p)
            itf = ITF[-1]
            vertical_tracking(True, s.zflg, itf.modc, float(s.zrint), s.rrtime, 0, s.rq, itf.nptr, STD, itf, p, pn, trackvar)
        else:
            itf = ITF[g.crefptr[s.survno]]
            vertical_tracking(False, s.zflg, s.modc, float(s.zrint), s.rrtime, 0, s.rq, itf.nptr, STD, itf, p, pn, trackvar)
            horizontal_tracking(itf, s, p, trackvar)
        itf_update(itf, g, s)
    drop_tracks(ITF, g, realtime, p)
"""VALID"""
