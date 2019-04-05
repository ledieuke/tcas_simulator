import math as m
import time

from tcasClass import *

class Trackvar:
    def __init__(self):
        """Group range"""
        self.lowlevel = None #Ground site sensitivity level choice
        self.rp = None #Projected range at old rate
        self.sit = None #Local index for Mode S sites

        """Group vertical"""
        self.alt_above_gnd = None #Own aircraft's altitude above ground level
        self.beta1 = None #Weighting factor used to smooth expected bin cross time
        self.dbins = None #Number of bins crossed since last report
        self.delt = None #Actual minus expected time in previous bin
        self.delz = None #Difference between smoothed and reported altitudes
        self.dtown = None #Time difference between current and prev. alt. rpts
        self.dz = None #Difference between predicted and reported altitudes
        self.dzm = None #Difference between current & prev.alt.rpts
        self.init = None #Initial report flag
        self.isgn = None #Direction of change: +1 = up, –1 = down
        self.k = None #Index defining the level of alpha-beta smoothing
        self.maxbinsthiszd = None #Maximum of BINSTHISZD at the tracked rate
        self.modec_flag = None #Altitude reporting flag (TRUE = altitude reporting)
        self.ostoss = None #Spurious oscillation flag
        self.qsign = None #100 * ISGN
        self.quant = None #Indicator of the quantization level
        self.ratio = None #Ratio between TPREV and TBINSAVE
        self.t = None #Time
        self.tbinmod = None #Modified average of TBIN and TBINSAVE
        self.tbinsave = None #Pre-update value of TBIN (bin cross time)
        self.tbmax = None #Maximum between TBINMOD and TBINSAVE
        self.tbmin = None #Minimum between TBINMOD and TBINSAVE
        self.tn = None #-(time until next transition due); pos if overdue
        self.tprev = None #Time in previous bin
        self.trantime = None #Transition time adjusted for a possible coast
        self.zdchange = None #Change in the rate estimate since the previous cycle
        self.zdsgn = None #Sign of the rate estimate used in rate bound calculations
        self.zflg = None #Valid-report flag (TRUE = valid)
        self.zp = None #Projected altitude at old rate
        self.zprev = None #Previous value of the altitude estimate
        self.zrept = None #Altitude report

        """Group airdata"""
        self.inif = None #Initialization flag
        self.tdif = None #Time difference between two successive measurements
        self.tin = None #Time stamp of altitude datum
        self.zin = None #Value of altitude datum
        self.zdin = None #Initial altitude rate
        self.zok = None #Validity flag for altitude datum (TRUE = valid)
        self.zpd = None #Projected altitude at previously estimated rate
        self.zdif = None #Altitude difference between two successive measurements

        """Group horizontal"""
        self.alpha = None #Range smoothing parameter
        self.beta = None #Range rate smoothing parameter
        self.cosb = None #Cosine of measured bearing
        self.cov = np.full((2,2),0.,dtype=float) #Covariance matrix
        self.dp = None #Range residual for bearing based tracker
        self.dpx = None #Cross range residual for bearing based tracker
        self.dt = None #Time difference
        self.firm = None #Firmness
        self.gamma = None #Range acceleration smoothing parameter
        self.hmdsq = None #Square of predicted horizontal miss distance
        self.maneuver = None #Maneuver flag
        self.pcov = np.full((2,2),0.,dtype=float) #Predicted covariance matrix for bearing based tracker
        self.pr_noise = None #Process noise variance
        self.rddp = None #Predicted range acceleration: parabolic tracker
        self.rddp_l = None #Predicted range acceleration: Cartesian tracker
        self.rdp = None #Predicted range rate: parabolic tracker
        self.rdp_l = None #Predicted range rate: Cartesian tracker
        self.rdtemp = None #Temporary placeholder of range rate for TAUR calculation
        self.resid = None #Residual: parabolic tracker
        self.residual = None #Local residual value
        self.resid_l = None #Residual: Cartesian tracker
        self.ressd = None #Standard deviation of parabolic range tracker residual
        self.rhoddthr = None#Range acceleration threshold
        self.rp_l = None #Predicted range: Cartesian tracker
        self.sinb = None #Sine of measured bearing
        self.sr = None #Smoothed range
        self.srd = None #Smoothed range rate
        self.srdd = None #Smoothed range acceleration
        self.srp = None #Predicted range
        self.srdp = None #Predicted range rate
        self.srddp = None #Predicted range acceleration
        self.temp = None #A temporary variable
        self.varxrng = None #Cross-range measurement variance
        self.w1 = None #Cross-range positional smoothing constant: bearing tracker
        self.w2 = None #Cross-range velocity smoothing constant: bearing tracker
        self.x = None #Intruder position in cross-track direction: Cartesian tracker
        self.xm = None #Measured Cartesian intruder position in X direction
        self.xp = None #Predicted intruder position in cross-track direction: Cartesian tracker
        self.y = None #Intruder position in in-track direction: Cartesian tracker
        self.ydot = None #Intruder rate in in-track direction: Cartesian tracker
        self.ym = None #Measured Cartesian intruder position in Y direction
        self.yp = None #Predicted intruder position in in-track direction

        """Group sensitivity"""
        self.externalsl = None #SL input from pilot or Mode S sensor


"""VALID"""
def pm(arg):
    if(arg >=0):
        return 1
    else:
        return -1
"""VALID"""


"""VALID"""
def credible(nptr, t, dzm, pn):
    credib = False
    if(m.fabs(dzm) < 1e-10):
        credib = True
    elif((t-nptr.tstart) < pn.credmindt):
        if(m.fabs(dzm) <= (pn.credinit*(t-nptr.tdat))):
            credib = True
    elif(m.fabs(dzm - nptr.zd*(t-nptr.tdat)) <= (nptr.q + pn.credzderr*(t-nptr.tdat) + pn.credaccdiv2*m.pow(t-nptr.tdat,2))):
        credib = True
    return credib
"""VALID"""


"""VALID"""
def airdata_tracking(inif, zok, zin, tin, zdin, g, p, trackvar):
    if(inif == True):
        oat = Oat()
        oat.z = zin
        oat.zd = zdin
        oat.tdat = tin
        oat.tupd = tin
        oat.soft = p.maxsoft
        oat.alt_credible = True
        g.oatptr = oat
    else:
        trackvar.zpd = g.oatptr.z + g.oatptr.zd * (tin - g.oatptr.tupd)
        if(zok == True):
            if(m.fabs(zin - trackvar.zpd) <= p.credzadc*g.oatptr.soft):
                g.oatptr.alt_credible = True
                g.oatptr.z = trackvar.zpd + p.alfao*(zin - trackvar.zpd)
                g.oatptr.zd = g.oatptr.zd + p.betao*(zin - trackvar.zpd)/(tin - g.oatptr.tdat)
                g.oatptr.tdat = tin
                g.oatptr.soft = max(g.oatptr.soft-1,p.minsoft)
            else:
                g.oatptr.alt_credible = False
                g.oatptr.z = trackvar.zpd
                g.oatptr.soft = min(g.oatptr.soft+1,p.maxsoft)
        else:
            g.oatptr.alt_credible = False
            g.oatptr.z = trackvar.zpd
            g.oatptr.soft = min(g.oatptr.soft+1,p.maxsoft)
        g.oatptr.tupd = tin
"""VALID"""


"""VALID"""
def new_track_init(pn, trackvar, zdin):
    n = N()
    n.z = trackvar.zrept
    n.tdat = trackvar.t
    n.zsave = trackvar.zrept
    n.tupdt = n.tdat
    n.zdinner = -pn.zdlarge
    n.zdouter = pn.zdlarge
    n.tstart = trackvar.t
    n.usealphabeta = False
    n.z_ab = trackvar.zrept
    n.zdd_ab = 0
    if(trackvar.quant == ONEHUNDRED):
        n.q = 100
    else:
        n.q = 25
    if(m.fabs(zdin) > pn.guesrate):
        n.zd = zdin
        n.binsthiszd = pn.nbinsnl
        n.casfirm = 2
        n.tbin = n.q / m.fabs(n.zd)
        n.direc = pm(n.zd)
        n.ttran = trackvar.t - n.tbin/2
        n.resid = 0
        n.zd_ab = zdin
        n.initcompleted = True
        n.class_ = TREND
    else:
        n.zd = 0
        n.casfirm = 0
        n.direc = 0
        n.ttran = trackvar.t
        n.zd_ab = 0
        n.initcompleted = True
        n.class_ = NEW_TRACK
    n.stdptr = None
    n.std_num_pts = 0
    n.alt_credible = True
    return n
"""VALID"""


"""VALID"""
def level_track_init(nptr, trackvar):
    nptr.z = trackvar.zrept
    nptr.zd = 0
    nptr.zdinner = 0
    nptr.zdouter = nptr.direc*nptr.q/(trackvar.t - nptr.ttran)
    nptr.class_ = LEVEL
"""VALID"""


"""VALID"""
def no_transition_trend_update(nptr, pn, trackvar):
    trackvar.tn = trackvar.t - nptr.ttran - nptr.tbin
    if(trackvar.tn > pn.latelevel):
        level_track_init(nptr, trackvar)
    elif(trackvar.tn > pn.lateslack):
        nptr.zd = nptr.direc*(nptr.q/(trackvar.t - nptr.ttran + pn.dt))*(pn.latelevel + pn.dt/2 - trackvar.tn)/(pn.latelevel + pn.dt/2)
        nptr.binsthiszd = max(1, nptr.binsthiszd - 1)
        nptr.z = trackvar.zrept + nptr.direc*nptr.q/2
        nptr.zdinner = 0
        nptr.zdouter = nptr.direc*nptr.q/(trackvar.t - nptr.ttran)
        trackvar.delz = 0
    else:
        trackvar.zp = nptr.z + nptr.zd*(trackvar.t - nptr.tupdt)
        if((trackvar.zp > trackvar.zrept + nptr.q/2) or (trackvar.zp < trackvar.zrept - nptr.q/2)):
            nptr.z = trackvar.zrept + nptr.direc*nptr.q/2
            trackvar.delz = nptr.z - trackvar.zp
            nptr.zd = nptr.zd + trackvar.delz/max(trackvar.t - nptr.ttran, pn.delzdt)
            nptr.zdinner = nptr.direc*min(nptr.q/(trackvar.t - nptr.ttran + pn.dt), m.fabs(nptr.zdinner))
            nptr.binsthiszd = max(1,nptr.binsthiszd - 1)
        else:
            trackvar.delz = 0
            nptr.z = trackvar.zp
"""VALID"""


"""VALID"""
def no_transition_update(nptr, pn, trackvar):
    if((nptr.class_ != LEVEL) and (trackvar.t > pn.tgolev)):
        level_track_init(nptr, trackvar)
    else:
        if(nptr.class_ == NEW_TRACK):
            nptr.zdinner = -nptr.q/(trackvar.t - nptr.tstart)
            nptr.zdouter = - nptr.zdinner
        elif(nptr.class_ == LEVEL):
            nptr.zdinner = 0
            nptr.zdouter = nptr.direc*nptr.q/(trackvar.t - nptr.ttran)
        elif(nptr.class_ == GUESS):
            nptr.zd = pn.zddecay*nptr.zd
            nptr.zdinner = 0
            if(trackvar.t - nptr.tstart > pn.tinitzd):
                nptr.zdouter = nptr.direc * min(nptr.q/(trackvar.t - nptr.ttran), pn.zdlikely)
            else:
                nptr.zdouter = nptr.direc * nptr.q/(trackvar.t - nptr.ttran)
            if(nptr.zd > 0):
                nptr.z = min(nptr.z + nptr.zd*(trackvar.t - nptr.tupdt),trackvar.zrept + nptr.q/2)
            else:
                nptr.z = max(nptr.z + nptr.zd*(nptr.t - nptr.tupdt), trackvar.zrept - nptr.q/2)
        elif(nptr.class_):
            no_transition_trend_update(nptr, pn, trackvar)
"""VALID"""


"""VALID"""
def no_transition_firmness(nptr, pn, trackvar):
    if((nptr.class_ == NEW_TRACK) or (nptr.class_ == GUESS)):
        if(trackvar.t - nptr.ttran > pn.guesdu3):
            nptr.casfirm = 3
        elif(trackvar.t - nptr.ttran > pn.guesdu2):
            nptr.casfirm = 2
        elif(trackvar.t - nptr.ttran > pn.guesdu1):
            nptr.casfirm = 1
    elif(nptr.class_ == LEVEL):
        nptr.casfirm = 3
    elif(nptr.class_ == TREND):
        if(trackvar.tn > pn.overdue):
            nptr.casfirm = min(2,nptr.casfirm + 1)
        elif((trackvar.tn > pn.lateslack) or (m.fabs(trackvar.delz) > pn.delzthr)):
            nptr.casfirm = 1
            nptr.fipreco = 0
    elif(trackvar.t - nptr.toscil > pn.guesdu2):
        nptr.casfirm = 3
    if(nptr.tdat != nptr.tupdt):
        nptr.casfirm = max(nptr.fipreco, nptr.casfirm)
"""VALID"""


"""VALID"""
def guess_track_init(nptr, pn, trackvar):
    if((trackvar.t - nptr.tdat > pn.longcoast) and (m.fabs(trackvar.dzm) > nptr.q)):
        nptr.zd = (trackvar.dzm - trackvar.qsign)/(trackvar.t - nptr.tdat)
    else:
        nptr.zd = trackvar.isgn*pn.guesrate
    if(trackvar.t - nptr.tstart < pn.tinitzd):
        nptr.zdouter = (trackvar.dzm + trackvar.qsign)/(trackvar.t - nptr.tstart)
    else:
        nptr.zdouter = trackvar.isgn*pn.zdlikely
    nptr.z = trackvar.zrept - trackvar.qsign/2 + nptr.zd*pn.dt/2
    nptr.casfirm = 0
    nptr.zdinner = 0
    nptr.class_ = GUESS
"""VALID"""


"""VALID"""
def oscil_track_init(nptr, trackvar):
    nptr.z = trackvar.zrept - trackvar.qsign/3
    nptr.zd = 0
    nptr.toscil = nptr.ttran
    nptr.casfirm = 2
    nptr.zdinner = 0
    nptr.zdouter = 0
    nptr.class_ = OSCIL
"""VALID"""


"""VALID"""
def unexpected_transition(nptr, pn, trackvar):
    if(trackvar.dbins > 1):
        guess_track_init(nptr, pn, trackvar)
    else:
        if((nptr.class_ == NEW_TRACK) or (nptr.class_  == LEVEL)):
            guess_track_init(nptr, pn, trackvar)
        elif(nptr.class_ == GUESS):
            oscil_track_init(nptr, trackvar)
        elif(nptr.class_ == TREND):
            if(trackvar.tprev/nptr.tbin <= pn.zrjit):
                if(nptr.tdat == nptr.tupdt):
                    nptr.fipreco = nptr.casfirm
                nptr.z = nptr.z + nptr.zd*(trackvar.t - nptr.tupdt)
                nptr.zdinner = 0
                nptr.casfirm = 0
                trackvar.ostoss = True
            else:
                oscil_track_init(nptr, trackvar)
        else:
            nptr.z = trackvar.zrept - trackvar.qsign/3
            nptr.casfirm = 3
"""VALID"""


"""VALID"""
def trend_track_init(nptr, pn, trackvar):
    nptr.usealphabeta = False
    if((trackvar.t - nptr.tstart < pn.tinitzd) or (trackvar.t - nptr.tdat > pn.longcoast)):
        nptr.tbin = trackvar.tprev
    else:
        nptr.tbin = max(trackvar.tprev, pn.tbinmin)
    nptr.zd = trackvar.qsign/nptr.tbin
    if(nptr.tbin > 1):
        nptr.z = trackvar.zrept - trackvar.qsign/2 + nptr.zd*pn.dt/2
    else:
        nptr.z = trackvar.zrept
    nptr.resid = 0
    nptr.binsthiszd = 1
    if(trackvar.t - nptr.ttran > pn.ttrendmin):
        nptr.casfirm = 2
        nptr.zdinner = trackvar.dzm/(trackvar.t - nptr.ttran + pn.dt)
        nptr.zdouter = pn.zdfracc*trackvar.dzm/(trackvar.t - nptr.ttran - pn.dt)
    else:
        nptr.casfirm = 1
        nptr.zdinner = trackvar.dzm/(pn.ttrendmin + pn.dt)
        nptr.zdouter = (trackvar.dzm + trackvar.qsign)/(trackvar.t - nptr.ttran)
    nptr.class_ = TREND
"""VALID"""


"""VALID"""
def smoothing_method_selection(nptr, pn, trackvar):
    if(nptr.usealphabeta == True):
        if((nptr.tbin > pn.tbinlo) and (trackvar.tprev > pn.tbinhi) and (nptr.tdat == nptr.tupdt)):
            nptr.usealphabeta = False
            nptr.resid = 0
            nptr.binsthiszd = pn.nbinsnl
    elif((nptr.tbin < pn.tbinhi) and (trackvar.tprev < pn.tbinlo) and (nptr.tdat == nptr.tupdt)):
        nptr.usealphabeta = True
        nptr.casfirm = min(1, nptr.casfirm)
"""VALID"""


"""VALID"""
def alpha_beta_smoothing(nptr, pn, trackvar):
    trackvar.zd = nptr.z + nptr.zd*(trackvar.t - nptr.tupdt)
    trackvar.dz = trackvar.zrept - trackvar.zp
    trackvar.zprev = nptr.z
    nptr.z = trackvar.zp + pn.alphaz[1]*trackvar.dz
    nptr.zd = nptr.zd + pn.betaz[1]*trackvar.dz/(trackvar.t - nptr.tdat)
    trackvar.dz = trackvar.zrept - (trackvar.zprev + nptr.zd*(trackvar.t - nptr.tupdt))
    if(m.fabs(trackvar.dz) >= pn.dzthr_100):
        nptr.casfirm = max(0, nptr.casfirm - 2)
        nptr.binsthiszd = max(nptr.binsthiszd - 1, pn.minbins)
    else:
        nptr.casfirm = min(nptr.casfir + 1, 3)
        if(m.fabs(nptr.tdat - nptr.tupdt) < 1e-10):
            nptr.casfirm = max(nptr.casfirm, nptr.fipreco)
            if(trackvar.t - nptr.tdat > pn.dtcoast):
                nptr.casfirm = max(2,nptr.casfirm)
        nptr.binsthiszd = min(nptr.binsthiszd + trackvar.dbins, pn.maxbins)
    if(nptr.z < trackvar.zrept - nptr.q/2):
        nptr.z = trackvar.zrept - nptr.q/2
    elif(nptr.z > trackvar.zrept + nptr.q/2):
        nptr.z = trackvar.zrept + nptr.q/2
    nptr.tbin = trackvar.qsign/nptr.zd
"""VALID"""


"""VALID"""
def expected_transition(nptr, pn, trackvar):
    if(m.fabs(nptr.tdat - nptr.tupdt) < 1e-10):
        while((trackvar.trantime > nptr.tdat + nptr.tbin*(trackvar.dbins - 1) + 1.5*pn.dt) and (trackvar.trantime > nptr.ttran + nptr.tbin*trackvar.dbins + pn.dt)):
            trackvar.trantime = trackvar.trantime - pn.dt
        trackvar.tprev = (trackvar.trantime - nptr.ttran)/trackvar.dbins
    trackvar.delt = trackvar.trantime - nptr.ttran - nptr.tbin*trackvar.dbins
    if(m.fabs(trackvar.delt) > pn.earlylate):
        if(trackvar.tprev > pn.ttrendmin):
            nptr.binsthiszd = trackvar.dbins
        else:
            nptr.binsthiszd = trackvar.dbins + 1
        nptr.resid = 0
    else:
        nptr.resid = pn.residimin*nptr.resid + trackvar.delt
        if(m.fabs(nptr.resid) <= pn.sliteoff):
            if(trackvar.tprev >= pn.maxzdtime/2):
                nptr.binsthiszd = 1
            else:
                trackvar.maxbinsthiszd = min(pn.maxbins, m.trunc(pn.maxzdtime/trackvar.tprev))
                nptr.binsthiszd = min(nptr.binsthiszd + trackvar.dbins, trackvar.maxbinsthiszd)
        else:
            if(trackvar.tprev > pn.ttrendmin):
                nptr.binsthiszd = trackvar.dbins
            else:
                nptr.binsthiszd = trackvar.dbins + 1
            nptr.resid = nptr.resid*pn.residecay
    trackvar.beta1 = trackvar.dbins/nptr.binsthiszd
    nptr.tbin = nptr.tbin + trackvar.beta1*(trackvar.tprev - nptr.tbin)
    nptr.zd = trackvar.qsign/nptr.tbin
    nptr.z = nptr.z + nptr.zd*(trackvar.t - nptr.tupdt)
    if(nptr.z > trackvar.zrept + nptr.q/2):
        nptr.z = trackvar.zrept + nptr.q/2
    elif(nptr.z < trackvar.zrept - nptr.q/2):
        nptr.z = trackvar.zrept - nptr.q/2
"""VALID"""


"""VALID"""
def transition_set_casfirm(nptr, pn, trackvar):
    trackvar.ratio = trackvar.tprev/trackvar.tbinsave
    if((pn.lo3 <= trackvar.ratio) and (trackvar.ratio <= pn.hi3)):
        nptr.casfirm = 3
    elif((pn.lo2 <= trackvar.ratio) and (trackvar.ratio <= pn.hi2)):
        nptr.casfirm = 2
    elif((pn.lo1 <= trackvar.ratio) and (trackvar.ratio <= pn.hi1)):
        nptr.casfirm = 1
    else:
        nptr.casfirm = 0
    if(m.fabs(trackvar.delt) < pn.out3):
        nptr.casfirm = 3
    elif(m.fabs(trackvar.delt) < pn.out2):
        nptr.casfirm = max(2, nptr.casfirm)
    if(trackvar.tprev > pn.slacken2):
        nptr.casfirm = max(2,nptr.casfirm)
    elif(trackvar.tprev > pn.slacken1):
        nptr.casfirm = max(1,nptr.casfirm)
    if(trackvar.t - nptr.tstart < pn.tinitzd):
        nptr.casfirm = 1
"""VALID"""


"""VALID"""
def transition_set_rate_limits(nptr, pn, trackvar):
    if(nptr.usealphabeta == False):
        if((nptr.casfirm == 3) or (m.fabs(trackvar.delt) < pn.out2)):
            nptr.zdinner = nptr.zd*(nptr.binsthiszd*(trackvar.t - nptr.ttran) - pn.dt)/(nptr.binsthiszd*(trackvar.t - nptr.ttran))
            nptr.zdouter = nptr.zd*(nptr.binsthiszd*(trackvar.t - nptr.ttran) + pn.dt)/(nptr.binsthiszd*(trackvar.t - nptr.ttran))
        elif(trackvar.tprev/trackvar.tbinsave < 1):
            nptr.zdinner = trackvar.qsign/trackvar.tbinsave
            nptr.zdouter = pn.zdfracc*trackvar.dzm/max(trackvar.t - nptr.ttran - pn.dt, pn.dt)
        else:
            nptr.zdinner = 0
            nptr.zdouter = trackvar.isgn*max(nptr.q/trackvar.tprev, m.fabs(nptr.zdouter))
    else:
        trackvar.tbinmod = nptr.tbin + (nptr.tbin - trackvar.tbinsave)
        trackvar.tbmin = min(trackvar.tbinmod, nptr.tbin)
        trackvar.tbmax = max(trackvar.tbinmod, nptr.tbin)
        nptr.zdinner = trackvar.qsign*(nptr.binsthiszd - 0.5)/(nptr.binsthiszd*trackvar.tbmax)
        nptr.zdouter = trackvar.qsign*(nptr.binsthiszd + 0.5)/(nptr.binsthiszd*trackvar.tbmin)
"""VALID"""


"""VALID"""
def transition_update(nptr, pn, trackvar):
    trackvar.dbins = m.fabs(trackvar.dzm)/nptr.q
    trackvar.isgn = pm(trackvar.dzm)
    trackvar.qsign = nptr.q*trackvar.isgn
    trackvar.trantime = trackvar.t
    trackvar.tprev = (trackvar.trantime - nptr.ttran)/trackvar.dbins
    if((nptr.class_ == NEW_TRACK) or (nptr.class_==  LEVEL)):
        unexpected_transition(nptr, pn, trackvar)
    elif((nptr.class_ == GUESS) or (nptr.class_== OSCIL)):
        if(nptr.direc == trackvar.isgn):
            trend_track_init(nptr, pn, trackvar)
        else:
            unexpected_transition(nptr, pn, trackvar)
    else:
        if(m.fabs(nptr.direc - trackvar.isgn) < 1e-10):
            trackvar.tbinsave = nptr.tbin
            smoothing_method_selection(nptr, pn, trackvar)
            if(nptr.usealphabeta == True):
                alpha_beta_smoothing(nptr, pn, trackvar)
            else:
                expected_transition(nptr, pn, trackvar)
                transition_set_casfirm(nptr, pn, trackvar)
            transition_set_rate_limits(nptr, pn, trackvar)
        else:
            unexpected_transition(nptr, pn, trackvar)
    if(trackvar.ostoss == False):
        nptr.zsave = trackvar.zrept
        nptr.ttran = trackvar.trantime
        nptr.direc = trackvar.isgn
"""VALID"""


"""VALID"""
def track_coast(nptr, t):
    if(m.fabs(nptr.tdat - nptr.tupdt) < 1e-10):
        nptr.fipreco = nptr.casfirm
    nptr.casfirm = max(0, nptr.casfirm - 1)
    nptr.z = nptr.z + nptr.zd*(t - nptr.tupdt)
    if(nptr.q == 25):
        nptr.z_ab = nptr.z_ab + nptr.zd_ab*(t - nptr.tupdt)
"""VALID"""


"""VALID"""
def one_hundred_ft_tracking(zflg, zrept, t, nptr, pn, trackvar):
    if(zflg == True):
        trackvar.dzm = zrept - nptr.zsave
        if(credible(nptr, t, trackvar.dzm, pn) == True):
            nptr.alt_credible = True
            trackvar.ostoss = False
            if(trackvar.dzm == 0):
                no_transition_update(nptr, pn,trackvar)
                no_transition_firmness(nptr, pn, trackvar)
            else:
                transition_update(nptr, pn, trackvar)
            if(trackvar.ostoss == False):
                nptr.tdat = t
        else:
            nptr.alt_credible = False
            track_coast(nptr,t)
    else:
        nptr.alt_credible = False
        track_coast(nptr,t)
    nptr.tupdt = t
"""VALID"""


"""VALID"""
def rate_initialization(nptr, pn, trackvar):
    if(m.fabs(trackvar.zrept - nptr.z_ab) > 1e-10):
        nptr.ttran = trackvar.t
    nptr.z_ab = trackvar.zrept
    nptr.z = nptr.z_ab
    if((trackvar.t - nptr.tstart) > pn.dtstart):
        nptr.zd_ab = (trackvar.zrept - nptr.zsave)/(trackvar.t - nptr.tstart)
        nptr.zsave = trackvar.zrept
        nptr.zd = nptr.zd_ab
        nptr.casfirm = 1
        nptr.initcompleted = True
    nptr.tdat = trackvar.t
"""VALID"""


"""VALID"""
def level_track_update(nptr, trackvar):
    nptr.z_ab = trackvar.zrept
    nptr.zd_ab = 0.
    nptr.zdd_ab = 0.
    nptr.z = nptr.z_ab
    nptr.zd = 0.
    nptr.casfirm = 3
"""VALID"""


"""VALID"""
def track_smoothing(nptr, pn, trackvar):
    trackvar.zp = nptr.z_ab + nptr.zd_ab*(trackvar.t - nptr.tupdt)
    trackvar.dz = trackvar.zrept - trackvar.zp
    if(m.fabs(trackvar.dz) > pn.hugedz):
        nptr.z_ab = trackvar.zrept
        trackvar.zdchange = trackvar.dz/(trackvar.t - nptr.tdat)
        nptr.zd_ab = nptr.zd_ab + trackvar.zdchange
        nptr.casfirm = 0
    else:
        if(m.fabs(nptr.zd_ab) < pn.zdabthr):
            trackvar.k = 2
        elif(m.fabs(trackvar.dz) < pn.largedz):
            trackvar.k = 1
        else:
            trackvar.k = 0
        nptr.z_ab = trackvar.zp + pn.alphaz[trackvar.k]*trackvar.dz
        trackvar.zdchange = (pn.betaz[trackvar.k]*trackvar.dz)/(trackvar.t - nptr.tdat)
        nptr.zd_ab = nptr.zd_ab + trackvar.zdchange
        trackvar.dz = trackvar.zrept - (nptr.z + nptr.zd_ab*(trackvar.t - nptr.tupdt))
        if(m.fabs(trackvar.dz) >= pn.dzthr_25):
            nptr.casfirm = max(0, nptr.casfirm - 2)
        else:
            nptr.casfirm = min(nptr.casfirm + 1, 3)
            if(m.fabs(nptr.tdat - nptr.tupdt) > 1e-10):
                nptr.casfirm = max(nptr.casfirm, nptr.fipreco)
                if((trackvar.t - nptr.tdat) > pn.dtcoast):
                    nptr.casfirm = max(2, nptr.casfirm)
    nptr.z = nptr.z_ab
    if(nptr.z < trackvar.zrept - (nptr.q/2)):
        nptr.z = trackvar.zrept - (nptr.q/2)
    elif(nptr.z > trackvar.zrept + (nptr.q/2)):
        nptr.z = trackvar.zrept + (nptr.q/2)
    if((m.fabs(nptr.zd) < pn.tinyzd) and (m.fabs(nptr.zd_ab) < pn.smallzd)):
        nptr.zd = 0.
    else:
        nptr.zd = nptr.zd_ab
"""VALID"""


"""VALID"""
def rate_bound_update(nptr, pn, trackvar):
    if(m.fabs(nptr.tdat - trackvar.t) < 1e-10):
        nptr.zdd_ab = (1 - pn.gammaz)*nptr.zdd_ab + pn.gammaz*trackvar.zdchange
    if(m.fabs(nptr.zd_ab) < 1e-10):
        trackvar.zdsgn = pm(nptr.zdd_ab)
    else:
        trackvar.zdsgn = pm(nptr.zd_ab)
    nptr.zdouter = nptr.zd_ab + trackvar.zdsgn*pn.bndzd[nptr.casfirm]
    nptr.zdinner = nptr.zd_ab - trackvar.zdsgn*pn.bndzd[nptr.casfirm]
    if(m.fabs(nptr.zdd_ab) > pn.zddabthr):
        if(trackvar.zdsgn == pm(nptr.zdd_ab)):
            nptr.zdouter = nptr.zdouter + pm(nptr.zdd_ab)*pn.bndac[nptr.casfirm]
        else:
            nptr.zdinner = nptr.zdinner + pm(nptr.zdd_ab)*pn.bndac[nptr.casfirm]
"""VALID"""


"""VALID"""
def twenty_five_ft_tracking(zflg, zrept, t, nptr, pn, trackvar):
    if(nptr.initcompleted == False):
        if(zflg == True):
            if(credible(nptr, t, zrept - nptr.z, pn) == True):
                rate_initialization(nptr, pn, trackvar)
    else:
        trackvar.zdchange = 0.
        if(zflg == True):
            if(credible(nptr, t, zrept - nptr.zsave, pn) == True):
                if((m.fabs(zrept - nptr.zsave) < 1e-10) and ((t - nptr.ttran) > pn.dtlong)):
                    level_track_update(nptr, trackvar)
                else:
                    track_smoothing(nptr, pn, trackvar)
                    if(m.fabs(zrept - nptr.zsave) > 1e-10):
                        nptr.ttran = t
                        nptr.zsave = zrept
                if(m.fabs(nptr.zd) < 1e-10):
                    nptr.class_ = LEVEL
                else:
                    nptr.class_ = TREND
                nptr.tdat = t
            else:
                track_coast(nptr, t)
        else:
            track_coast(nptr, t)
        rate_bound_update(nptr, pn, trackvar)
    nptr.tupdt = t
"""VALID"""


"""VALID"""
def one_hundred_ft_track_initialization(zrept, t, nptr, pn):
    nptr.q = 100
    if(credible(nptr, t, zrept - nptr.zsave, pn) == True):
        nptr.tstart = t - pn.tinitzd + pn.dt/2
    else:
        nptr.tstart = t
    if(m.fabs(nptr.zd) > pn.smallzd):
        nptr.direc = pm(nptr.zd)
        nptr.tbin = nptr.q/m.fabs(nptr.zd)
        nptr.z = nptr.z + nptr.zd*(t - nptr.tupdt)
        if(nptr.z > zrept + nptr.q/2):
            nptr.z = zrept + nptr.q/2
        elif(nptr.z < zrept - nptr.q/2):
            nptr.z = zrept - nptr.q/2
        nptr.ttran = t - (nptr.z - (zrept - nptr.direc*nptr.q/2))/nptr.zd
        nptr.binsthiszd = pn.nbinsnl
        nptr.resid = 0
        nptr.zdinner = nptr.zdinner/pn.zdfracc
        nptr.zdouter = nptr.zdouter*pn.zdfracc
        nptr.class_ = TREND
    else:
        nptr.z = zrept
        nptr.zd = 0
        nptr.direc = 0
        nptr.ttran = nptr.tstart
        nptr.zdinner = - pn.zdlarge
        nptr.zdouter = pn.zdlarge
        nptr.class_ = NEW_TRACK
    nptr.zsave = zrept
    nptr.tdat = t
    nptr.tupdt = t
    nptr.usealphabeta = False
    nptr.casfirm = 0
"""VALID"""


"""VALID"""
def switch_to_one_hundred_ft_tracking(nptr, STD, p, pn, trackvar):
    twenty_five_ft_tracking(False, 0, trackvar.t, nptr, pn, trackvar)
    if(nptr.stdptr == None):
        STD.clear()
        nptr.stdptr = STD
        nptr.stdptr.append(Std(trackvar.t, trackvar.zrept))
        nptr.std_num_pts = 1
    else:
        nptr.stdptr.append(Std(trackvar.t, trackvar.zrept))
        nptr.std_num_pts = nptr.std_num_pts + 1
        if(nptr.std_num_pts >= p.min_pts_for_switch):
            """OK"""
            one_hundred_ft_track_initialization(STD[0].zdata, STD[0].tdata, nptr, pn)
            for std in STD[1:]:
                while(nptr.tupdt + 1.5*pn.dt < std.tdata):
                    one_hundred_ft_tracking(False, 0, nptr.tupdt + pn.dt, nptr, pn, trackvar)
                one_hundred_ft_tracking(True, std.zdata, std.tdata, nptr, pn, trackvar)
            STD.clear()
            nptr.stdptr = None
            nptr.std_num_pts = 0
"""VALID"""


"""VALID"""
def twenty_five_ft_track_initialization(zrept, t, nptr, pn):
    nptr.q = 25
    nptr.z = zrept
    nptr.z_ab = zrept
    nptr.zd_ab = nptr.zd
    nptr.zdd_ab = 0
    nptr.initcompleted = True
    if(m.fabs(nptr.zd) > pn.smallzd):
        nptr.zdinner = nptr.zd - pm(nptr.zd)*pn.bndzd[0]
        nptr.zdouter = nptr.zd + pm(nptr.zd)*pn.bndzd[0]
        nptr.class_ = TREND
    else:
        nptr.zdinner = -pn.bndzd[0]
        nptr.zdouter = pn.bndzd[0]
        nptr.class_ = LEVEL
    nptr.zsave = zrept
    nptr.tdat = t
    nptr.tupdt = t
    nptr.ttran = t
    nptr.casfirm = 0
"""VALID"""


"""VALID"""
def switch_to_twenty_five_ft_tracking(nptr, STD, p, pn, trackvar):
    one_hundred_ft_tracking(False, 0, trackvar.t, nptr, pn, trackvar)
    if(nptr.stdptr == None):
        STD.clear()
        nptr.stdptr = STD
        nptr.stdptr.append(Std(trackvar.t, trackvar.zrept))
        nptr.std_num_pts = 1
    else:
        nptr.stdptr.append(Std(trackvar.t, trackvar.zrept))
        nptr.std_num_pts += 1
        if(nptr.std_num_pts >= p.min_pts_for_switch):
            twenty_five_ft_track_initialization(STD[0].zdata, STD[0].tdata, nptr, pn)
            for std in STD[1:]:
                while(nptr.tupdt + 1.5*pn.dt < std.tdata):
                    twenty_five_ft_tracking(False, 0, nptr.tupdt + pn.dt, nptr, pn, trackvar)
                twenty_five_ft_tracking(True, std.zdata, std.tdata, nptr, pn, trackvar)
            STD.clear()
            nptr.stdptr = None
            nptr.std_num_pts = 0
"""VALID"""


"""VALID"""
def vertical_tracking(init, zflg, modec_flag, zrept, t, zdin, quant, nptr ,STD, itf_or_g, p, pn, trackvar):
    if(modec_flag == True):
        if(init == True or nptr == None):
            itf_or_g.nptr = new_track_init(pn, trackvar, zdin)
        else:
            if(zflg == True):
                if((quant == ONEHUNDRED) and (nptr.q == 100)):
                    one_hundred_ft_tracking(zflg, zrept, t, nptr, pn, trackvar)
                    if(nptr.stdptr != None):
                        STD.clear()
                        nptr.stdptr = None
                        nptr.std_num_pts = 0
                elif((quant == TWENTY_FIVE) and (nptr.q == 25)):
                    twenty_five_ft_tracking(zflg, zrept, t, nptr, pn, trackvar)
                    if(nptr.stdptr != None):
                        STD.clear()
                        nptr.stdptr = None
                        nptr.std_num_pts = 0
                elif((quant == ONEHUNDRED) and (nptr.q == 25)):
                    switch_to_one_hundred_ft_tracking(nptr, STD, p, pn, trackvar)
                elif((quant == TWENTY_FIVE) and (nptr.q == 100)):
                    switch_to_twenty_five_ft_tracking(nptr, STD, p, pn, trackvar)
            elif(nptr.q == 100):
                one_hundred_ft_tracking(zflg, zrept, t, nptr, pn, trackvar)
            else:
                twenty_five_ft_tracking(zflg, zrept, t, nptr, pn, trackvar)
"""VALID"""


"""VALID"""
def own_altitude_tracker_initialization(STD, g, o, p, pn, trackvar):
    if(g.airdata == True):
        g.zadc = o.zadc
        g.tadc = o.tadc
        airdata_tracking(True, True, g.zadc, g.tadc, 0, g, p, trackvar)
        g.tracking_airdata = True
    else:
        g.zrown = float(o.zrown)
        g.trown = o.trown
        vertical_tracking(True, True, True, g.zrown, g.trown, 0, ONEHUNDRED, g.nptr, STD, g, p, pn, trackvar)
        g.tracking_airdata = False
    STD.clear()
    g.stdptr = None
    g.std_num_pts = 0
"""VALID"""


"""VALID"""
def switch_from_vertical_to_airdata(STD, g, p, pn, trackvar):
    vertical_tracking(False, False, True, 0, g.tcur, 0, ONEHUNDRED, g.nptr, STD, g, p, pn, trackvar)
    if(g.stdptr == None):
        STD.clear()
        g.stdptr = STD
        g.stdptr.append(Std(g.tadc, g.zadc))
        g.std_num_pts = 1
    else:
        g.stdptr.append(Std(g.tadc, g.zadc))
        g.std_num_pts += 1
        if(g.std_num_pts >= p.min_pts_for_switch):
            trackvar.zdif = STD[1].zdata - STD[0].zdata
            trackvar.tdif = STD[1].tdata - STD[0].tdata
            if(m.fabs(trackvar.zdif - g.zdown*trackvar.tdif) <= p.credzadc*p.maxsoft):
                g.nptr = None
                airdata_tracking(True, True, STD[0].zdata, STD[0].tdata, g.zdown, g.oatptr, p, trackvar)
                for std in g.stdptr[1:]:
                    airdata_tracking(False, True, std.zdata, std.tdata, g.zdown, g.oatptr, p, trackvar)
                g.tracking_airdata = True
                STD.clear()
                g.stdptr = None
                g.std_num_pts = 0
            else:
                STD_copy = STD[1:]
                STD.clear()
                STD.extend(STD_copy)
                g.std_num_pts = g.std_num_pts - 1
"""VALID"""


"""VALID"""
def switch_from_airdata_to_vertical(STD, g, p, pn, trackvar):
    airdata_tracking(False, False, 0, g.tcur, 0, g.oatptr, p, trackvar)
    if(g.stdptr == None):
        STD.clear()
        g.stdptr = STD
        g.stdptr.append(Std(g.trown, g.zrown))
        g.std_num_pts = 1
    else:
        g.stdptr.append(Std(g.trown, g.zrown))
        g.std_num_pts += 1
        if(g.std_num_pts >= p.min_pts_for_switch):
            trackvar.zdif = STD[1].zdata - STD[0].zdata
            trackvar.tdif = STD[1].tdata - STD[0].tdata
            if(m.fabs(trackvar.zdif - g.zdown*trackvar.tdif) <= pn.credinit*trackvar.tdif):
                g.oatptr = None
                vertical_tracking(True, True, True, STD[0].zdata, STD[0].tdata, g.zdown, ONEHUNDRED, g.nptr, STD, g, p, pn, trackvar)
                for std in STD[1:]:
                    vertical_tracking(False, True, True, std.zdata, std.tdata, 0, ONEHUNDRED, g.nptr, STD, g, p, pn, trackvar)
                g.tracking_airdata = False
                STD.clear()
                g.stdptr = None
                g.std_num_pts = 0
            else:
                STD_copy = STD[1:]
                STD.clear()
                STD.extend(STD_copy)
                g.std_num_pts -= 1
"""VALID"""


"""VALID"""
def own_altitude_tracking(STD, g, o, p, pn, cas_to_monitor, trackvar):
    if(g.initflg == True):
        g.initflg = False
        own_altitude_tracker_initialization(STD, g, o, p, pn, trackvar)
    else:
        if(g.airdata == True):
            g.zadc = o.zadc
            g.tadc = o.tadc
            if(g.tracking_airdata == True):
                airdata_tracking(False, True, g.zadc, g.tadc, 0, g, p, trackvar)
                if(g.stdptr != None):
                    STD.clear()
                    g.stdptr = None
                    g.std_num_pts = 0
            else:
                switch_from_vertical_to_airdata(STD, g, p, pn, trackvar)
        else:
            g.zrown = float(o.zrown)
            g.trown = o.trown
            if(g.tracking_airdata == False):
                vertical_tracking(False, True, True, g.zrown, g.trown, 0, ONEHUNDRED, g.nptr, STD, g, p, pn, trackvar)
                if(g.stdptr != None):
                    STD.clear()
                    g.stdptr = None
                    g.std_num_pts = 0
            else:
                switch_from_airdata_to_vertical(STD, g, p, pn, trackvar)
    if(g.tracking_airdata == True):
        g.zown = g.oatptr.z
        g.zdown = g.oatptr.zd
        cas_to_monitor.alt_credible = g.oatptr.alt_credible
    else:
        g.zown = g.nptr.z
        g.zdown = g.nptr.zd
        cas_to_monitor.alt_credible = g.nptr.alt_credible
"""VALID"""


"""VALID"""
def climb_evaluation(g):
    """No physical limit for the aircraft to climb"""
    if(False in g.ra[:10]):
        g.climbinhib = False
        if(g.zadc > 16000*0.3048):
            g.climbinhib = True
"""VALID"""


"""VALID"""
def auto_sl4to7(g, p):
    if(g.index == 4):
        if(g.radarout == 0 and g.zradar <= p.zsl4to3):
            g.index = 3
        else:
            if(g.radarout > p.radarlost):
                if(g.zown <= p.zsl4to3):
                    g.index = 3
                else:
                    if(g.zown >= p.zsl4to5):
                        g.index = 5
    if(g.index == 5):
        if(g.radarout == 0 and g.zradar <= p.zsl5to4):
            g.index = 4
        else:
            if(g.radarout > p.radarlost):
                if(g.zown <= p.zsl5to4):
                    g.index = 4
                else:
                    if(g.zown >= p.zsl5to6):
                        g.index = 6
    if(g.index == 6):
        if(g.radarout == 0 and g.zradar <= p.zsl6to5):
            g.index = 5
        else:
            if(g.radarout > p.radarlost):
                if(g.zown <= p.zsl6to5):
                    g.index = 5
                else:
                    if(g.zown >= p.zsl6to7):
                        g.index = 7
    if(g.index == 7):
        if(g.zown <= p.zsl7to6):
            g.index = 6
"""VALID"""


"""VALID"""
def auto_sl(g, o, p):
    g.ground_mode = o.ground_mode
    if(g.oogroun == True):
        if(g.ground_mode == True):
            g.index = 2
        else:
            g.index = 1
    else:
        if(g.nodescent == True and g.climbinhib == True):
            g.index = 2
        else:
            if(g.index <= 2):
                if(g.radarout == 0):
                    if(g.zradar >= p.zsl2to3):
                        g.index = 3
                    else:
                        g.index = 2
                else:
                    if(g.radarout > p.radarlost):
                        g.index = 3
            if(g.index == 3):
                if(g.radarout == 0):
                    if(g.zradar <= p.zsl3to2):
                        g.index = 2
                    else:
                        if(g.zradar >= p.zsl3to4):
                            g.index = 4
                else:
                    if(g.radarout > p.radarlost):
                        if(g.zown >= p.zsl3to4):
                            g.index = 4
            auto_sl4to7(g, p)
"""VALID"""


"""VALID"""
def set_index(g, o, p, trackvar):
    if(g.opflg == False and g.ramode == False):
        g.index = 1
    else:
        auto_sl(g, o, p)
        trackvar.externalsl = o.manual
        if(trackvar.externalsl == p.automatic):
            trackvar.externalsl = g.index
        trackvar.lowlevel = p.largeint
        trackvar.sit = 0
        while(trackvar.sit <= p.sitmax):
            if((g.levelsit[trackvar.sit] > 1 and g.levelsit[trackvar.sit] < trackvar.lowlevel) and (g.levelsit[trackvar.sit] >= 3 or (False in g.ra[:10]))):
                trackvar.lowlevel = g.levelsit[trackvar.sit]
            trackvar.sit += 1
        trackvar.externalsl = min(trackvar.externalsl, trackvar.lowlevel)
        if(trackvar.externalsl != p.ta_only):
            g.index = min(g.index, trackvar.externalsl)
"""VALID"""


"""VALID"""
def set_layer_dependent_parameters(g, p):
    if(g.layer == 1):
        if(g.zown >= p.top[1]):
            g.layer = 2
    if(g.layer == 2):
        if(g.zown <= p.bot[2]):
            g.layer = 1
        else:
            if(g.zown >= p.top[2]):
                g.layer = 3
    if(g.layer == 3):
        if(g.zown <= p.bot[3]):
            g.layer = 2
        else:
            if(g.zown >= p.top[3]):
                g.layer = 4
    if(g.layer == 4):
        if(g.zown <= p.bot[4]):
            g.layer = 3
        else:
            if(g.zown >= p.top[4]):
                g.layer = 5
    if(g.layer == 5):
        if(g.zown <= p.bot[5]):
            g.layer = 4
        else:
            if(g.zown >= p.top[5]):
                g.layer = 6
    if(g.layer == 6):
        if(g.zown <= p.bot[6]):
            g.layer = 5
    g.alim = p.al[g.layer]
    g.zthr = p.zt[g.layer]
    g.sensfirm = p.sf[g.layer]
    g.zthr_ta = p.zt_ta[g.layer]
"""VALID"""


"""VALID"""
def update_interrogation_mode(g):
    """g.opflg = True and g.index > 1 => no else needed"""
    if(g.opflg == True and g.index > 1):
        g.intmode = True
#     else:
#         if(g.intmode == True and g.ramode == False):
#             g.intmode = False
#             while(g.colock == True):
#                 pass
#             g.colock = True
#             g.tlock = realtime.tclock
#             for tf in itf.tptr:
#                 tf.iptr = None
#             itf = None
#         g.crefptr = None
#         coordination_unlock()
"""VALID"""


"""VALID"""
def update_advisory_mode(ITF, TF, WL, g, realtime, trackvar):
    g.tamode = False
    if(g.opflg == True):
        if(g.index >= 2):
            g.tamode = True
            if((trackvar.externalsl > 2) and (g.index > 2)):
                if(g.ramode == False):
                    g.ramode_on = realtime.tclock
                    g.ramode = True
    if((g.opflg == False) or (g.index <= 2) or (trackvar.externalsl <= 2)):
        if(g.ramode == True):
            g.ramode = False
            g.macflg = False
            time_lock_begin = time.time()
            while (g.colock == True):
                if ((time.time() - time_lock_begin) > p.tunlock):
                    assert ()
                time.sleep(0.01)
            g.colock = True
            g.tlock = realtime.tclock
            for tf in TF:
                if(tf.poowrar != 0):
                    WL.append(Wl(tf.iptr, TERM))
            for itf in ITF:
                itf.levelwait, itf.khit = 0, 0
                if(itf.tacode == RA):
                    itf.tacode = TAMC
                itf.taucap = False
            g.colock = False

"""VALID"""



def track_own(ITF, TF, WL, STD, g, o, realtime, groundalt, p, pn, owndata_to_surv, cas_to_monitor, trackvar):
    g.tcur = realtime.tclock
    g.opflg = o.tcasop
    g.radarvalid = o.radarvalid
    g.idown = o.idown
    g.transvi = o.transvi
    owndata_to_surv.radarvalid = o.radarvalid
    owndata_to_surv.zradar = o.zradar
    own_altitude_tracking(STD, g, o, p, pn, cas_to_monitor, trackvar)
    owndata_to_surv.zown = g.zown
    climb_evaluation(g)
    if(g.radarvalid == True):
        g.radarout = 0
        g.zradar = o.zradar
        if(g.oogroun == False):
            if(g.zradar < p.zlimitl):
                g.oogroun = True
        else:
            if(g.zradar > p.zlimitu):
                g.oogroun = False
    else:
        g.radarout += 1
        if(g.radarout > 2):
            g.oogroun = False
    owndata_to_surv.oogroun = g.oogroun
    if(groundalt.zvalid == True):
        g.zground = groundalt.zground
    else:
        g.zground = -p.zlarge
    """Altitude always available => altitude_alerter_check no needed"""
    # altitude_alerter_check(g, o, p)
    """Aircraft never on the ground => ground_proximity_check no needed"""
    # ground_proximity_check(g, p)
    set_index(g, o, p, trackvar)
    set_layer_dependent_parameters(g, p)
    update_interrogation_mode(g)
    owndata_to_surv.intmode = g.intmode
    update_advisory_mode(ITF, TF, WL, g, realtime, trackvar)
    """Our TCAS uses ADS-B"""
    # send_owndata_to_trans()