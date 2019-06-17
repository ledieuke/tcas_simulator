from util import *

from tracking import *
from tracking_intruders import *
from detect import *
from resolution import *
from multiaircraft import *
from tcasEmitter import *
from tcasReceiver import *
from display import *
from housekeeping import *


class Tcas:
    def __init__(self, aircraft):
        self.aircraft = aircraft

        self.tcasEmitter = TcasEmitter()
        self.tcasReceiver = TcasReceiver()

        self.g = None
        self.o = None
        self.realtime = None
        self.groundalt = None
        self.p = None
        self.pn = None
        self.owndata_to_surv = None
        self.to_disp_aurl = None
        self.ra_to_trans = None
        self.to_ground_station = None
        self.cas_to_monitor = None
        self.brdcst_data = None
        self.intent_to_threat = None
        self.to_ground_station = None
        self.snd_var = None
        self.ITF = None
        self.TF = None
        self.WL = None
        self.STD = None
        self.SList = None
        self.DIL = None
        self.trackvar = None
        self.detvar = None
        self.resvar = None
        self.macvar = None
        self.snd_var = None
        self.dispvar = None


    """OK"""
    def initialize(self, g, realtime, p):
        g.ra = np.full(14,False,dtype=bool)
        g.prevra = np.full(14,False,dtype=bool)
        g.prevmte = False
        g.crefptr = np.full(100, None, dtype=Itf)
        g.initflg = True
        g.radarout = 5
        g.index = 3
        g.layer = 1
        g.initcycle = 0
        g.oogroun = False
        g.levelsit = np.full(16, 0, dtype=int)
        g.intmode = False
        g.ramode = False
        g.corrective_clm, g.corrective_des = False, False
        g.zdmodel = 0
        g.clstrong, g.destrong = 0, 0
        g.clstrold, g.destrold = 0, 0
        g.intent = np.full(4,False,dtype=bool)
        g.previncrease = False
        g.anyincrease = False
        g.nodescent, g.inc_desinhib = False, False
        g.mac_new = 0
        g.mac_reverse, g.maneuver_reversal = False, False
        g.turn_off_aurals = True
        g.colock = False
        g.tposra, g.tlastnewra = 0, 0
        g.brdcst, g.brngvalid, g.rngvalid, g.crossing_ra, g.reversal_ra = False, False, False, False, False
        g.aid = np.full(13,False,dtype=bool)
        g.cac = np.full(13,False,dtype=bool)
        g.active, g.id, g.transvi = 0, 0, 0
        g.altnew, g.brngnew, g.rngnew = 0, 0, 0
        g.pointer = None
        g.ncycle = p.rabrdcst
        g.alerter_alt = -p.zlarge
        g.alerter_time = realtime.tclock
    """OK"""


    """OK"""
    def periodic_data_processing(self, g, o, realtime):
        if(self.aircraft.geoaltitude != None):
            g.airdata = True
        else:
            g.airdata = False
        if(g.airdata == True):
            o.zadc = self.aircraft.geoaltitude*0.3048
            o.tadc = realtime.tclock
            o.zradar = self.aircraft.geoaltitude * 0.3048
            o.radarvalid = True
        else:
            o.zrown = self.aircraft.baroaltitude*0.3048
            o.trown = realtime.tclock
            o.zradar = self.aircraft.baroaltitude * 0.3048
            o.radarvalid = False
        o.idown = self.aircraft.icaoAdress
        o.transvi = 0
        o.manual = 0
        # o.aid = []
        o.ground_mode = False
        o.tcasop = True
        o.alerter_avail = False
    """OK"""


    # Return range between aircrafts at any time t
    def rangeBetweenAircrafts(self, s, t, v):
        return m.sqrt(np.dot(s, s) + 2 * t * np.dot(s, v) + (t ** 2) * np.dot(v, v))


    def update_range(self, ai):
        s = findRelativeHorizontalPosition(self.aircraft, ai)
        v = findRelativeHorizontalVelocity(self.aircraft, ai)
        r = self.rangeBetweenAircrafts(s, 0, v)
        return r


    def init_groundalt(self, groundalt):
        groundalt.zvalid = False


    def update_g(self, g):
        g.zdown = (self.aircraft.verticalRate*0.3048)/60


    def update_realtime(self, realtime, currentTime):
        realtime.tclock = currentTime

    def update_S(self, SList, currentTime):
        SList.clear()
        for icaoAdress in self.aircraft.aircraftIntruders:
            ai = self.aircraft.aircraftIntruders[icaoAdress]
            s = S()
            if(ai.tcasStatus):
                s.eqp = TCAS
            else:
                s.eqp = ATCRBS
            s.idintr = ai.icaoAdress
            s.modc = True
            s.plint = ai.level
            s.survmode = NORMAL
            s.survno = len(SList)
            s.bear = m.radians(ai.heading - self.aircraft.heading)
            s.bearok = True
            s.bear_meas = m.radians(ai.heading)
            s.bear_meas_ok = True
            s.rflg = True
            s.rq = TWENTY_FIVE
            r = self.update_range(ai)*1852
            s.rr = r
            s.rrtime = currentTime
            s.zflg = True
            if(ai.geoaltitude == None):
                s.zrint = int(ai.baroaltitude*0.3048)
            else:
                s.zrint = int(ai.geoaltitude*0.3048)
            SList.append(s)


    def run(self, currentTime):
        # print("icaoAdress = ", self.aircraft.icaoAdress)
        self.WL.clear()
        self.update_g(self.g)
        self.update_realtime(self.realtime, currentTime)
        self.update_S(self.SList, currentTime)
        self.periodic_data_processing(self.g, self.o, self.realtime)
        track_own(self.ITF, self.TF, self.WL, self.STD, self.g, self.o, self.realtime, self.groundalt, self.p, self.pn, self.owndata_to_surv, self.cas_to_monitor, self.trackvar)
        self.aircraft.level = self.g.index
        if(self.g.intmode == True):
            track_intruders(self.ITF, self.STD, self.g, self.realtime, self.SList, self.p, self.pn, self.trackvar)
            if(self.g.ramode == True):
                self.detvar.rdtemp = self.trackvar.rdtemp
                detect_conflicts(self.ITF,self.TF, self.WL, self.g, self.realtime, self.p, self.pn, self.detvar, self.resvar)
        self.resvar.sit = self.trackvar.sit
        self.resvar.dmod = self.detvar.dmod
        self.resvar.trthr = self.detvar.trthr
        self.resvar.t1 = self.detvar.t1
        self.resvar.zdgoal = self.detvar.zdgoal
        self.resvar.zmpclm = self.detvar.zmpclm
        self.resvar.zmpdes = self.detvar.zmpdes
        self.resvar.z = self.detvar.z
        self.resvar.zd = self.detvar.zd
        self.resvar.zdi = self.detvar.zdi
        self.resvar.zi = self.detvar.zi
        for wl in self.WL:
            resolution(self.ITF, self.TF, wl, self.g, self.p, self.realtime, self.DIL, self.detvar, self.resvar)
        self.macvar.altdiff = self.detvar.altdiff
        self.macvar.zdgoal = self.resvar.zdgoal
        self.macvar.increase_sep = self.resvar.increase_sep
        self.macvar.nominal_sep = self.resvar.nominal_sep
        self.macvar.sense = self.resvar.sense
        for i in range((len(self.resvar.owntent))):
            self.macvar.owntent[i] = self.resvar.owntent[i]
        if(self.g.macflg == True):
            self.g.mac_new = 0
            self.g.mac_reverse = False
            for wl in self.WL:
                if(wl.status != TERM):
                    multiaircraft_processing(self.TF, wl, self.g, self.p, self.realtime, self.macvar, self.resvar)
        if(self.g.opflg == True):
            for wl in self.WL:
                self.tcasEmitter.send_initial_intent(wl, self.g, self.realtime, self.p,self.intent_to_threat, self.snd_var)
        self.dispvar.raind = self.resvar.raind
        self.dispvar.proj_zint = self.resvar.proj_zint
        display_advisories(self.ITF, self.TF, self.g, self.o, self.p, self.realtime, self.to_disp_aurl, self.ra_to_trans, self.to_ground_station, self.brdcst_data, self.dispvar)
        housekeeping(self.TF, self.g, self.realtime, self.p, self.DIL, self.resvar)
        if(self.to_disp_aurl.down_advisory == DESCEND):
            self.aircraft.verticalRate = (self.to_disp_aurl.rate*60)/0.3048
            self.aircraft.onRa = True
        if(self.to_disp_aurl.up_advisory == CLIMB):
            self.aircraft.verticalRate = (self.to_disp_aurl.rate*60)/0.3048
            self.aircraft.onRa = True
        if(self.to_disp_aurl.down_advisory == DOWN_ADVISORY_NONE and self.to_disp_aurl.up_advisory == UP_ADVISORY_NONE and self.aircraft.onRa == True):
            self.aircraft.verticalRate = 0
            self.aircraft.onRa = False


    def initTcas(self):
        self.g = G()
        self.o = O()
        self.realtime = Realtime()
        self.groundalt = Groundalt()
        self.p = P()
        self.pn = Pn()
        self.owndata_to_surv = Owndata_to_surv()
        self.to_disp_aurl = To_disp_aural()
        self.ra_to_trans = Ra_to_trans()
        self.to_ground_station = To_ground_station()
        self.intent_to_threat = Intent_to_threat()
        self.cas_to_monitor = Cas_to_monitor()
        self.brdcst_data = Brdcst_data()
        self.ITF = []
        self.TF = []
        self.STD = []
        self.SList = []
        self.DIL = []
        self.WL = []
        self.initialize(self.g, self.realtime, self.p)
        self.init_groundalt(self.groundalt)
        self.tcasReceiver.TF = self.TF
        self.tcasReceiver.g = self.g
        self.tcasReceiver.p = self.p
        self.tcasReceiver.realtime = self.realtime
        self.trackvar = Trackvar()
        self.detvar = Detvar()
        self.resvar = Resvar()
        self.resvar.accel = self.p.vaccel
        self.macvar = Macvar()
        self.snd_var = Snd_var()
        self.dispvar = Dispvar()
