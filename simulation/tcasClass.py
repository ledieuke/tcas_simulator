import numpy as np

from tcasConstant import *

""""INTRUDER TRACK FILE ENTRY"""
class Itf:
    def __init__(self):
        """Group identity"""
        self.crefno = None #Cross-reference to surveillance buffer
        self.idint = None #ICAO 24-bit aircraft address, if any
        self.irow = None #Track file row number
        self.nptr = None #Nonlinear track file entry
        self.survmode = None #Surveillance mode (normal, reduced)
        self.tptr = None #Threat File entry
        self.wptr = None #Working list entry

        """Group capability"""
        self.eqp = None #CAS equipage
        self.lev = None #Index to SL-dependent parameters
        self.modc = None #Mode-C type track
        self.plint = None #Intruder sensitivity level

        """Group position"""
        self.a = None #Abs. value of relative altitude
        self.adot = None #Signed value of relative altitude rate
        self.arrow = None #Vertical rate arrow for display
        self.bearing = None #Bearing relative to own airframe
        self.bearok = None #Valid data contained in BEARING
        self.previous_rz = None #Relative altitude of previous cycle
        self.r = None #Tracked range
        self.rd = None #Tracked range rate
        self.rflg = None #Valid data in S.RR (range report); 0=coast
        self.rz = None #Relative altitude
        self.rzd = None #Relative altitude rate
        self.valrep = None #Valid surveillance report indicator
        self.zdint = None #Tracked altitude rate
        self.zint = None #Tracked altitude
        self.zrint = None #Raw altitude of Mode-C intruder

        """Group detection"""
        self.altitude_lost = None #Mode C threat has become non-altitude reporting
        self.clear_conflict = None #Clear of conflict with this threat
        self.ditf = None #Track needs to be dropped
        self.khit = 0 #Detection hit counter
        self.rrd_count = 0 #Range-range rate product counter

        """Group projection"""
        self.increase_pending = None #Defer increase during multiaircraft encounter
        self.retention = None #Defer negative during multiaircraft encounter
        self.sech = 0 #Separation for second-choice sense
        self.taucap = None #Tau not allowed to rise
        self.taur = None #modified tau
        self.taurise = None #Counter - number of scans TRTUN has been rising
        self.tauv = None #Time to co-altitude
        self.trtru = None #True tau
        self.trtun = None #Uncapped value of true tau
        self.vmd = None #Vertical miss distance at closest approach

        """Group reversal"""
        self.cpt_rev = None #SA01 reversal flag

        """Group evaluation"""
        self.increase = None #Increase rate RA current for this threat
        self.inctest = None #Increase rate RA counter
        self.int_cross = None #Intruder causing alt-crossing RA to be selected
        self.mac_increase = None #Multi-threat increase rate RA
        self.own_cross = None #Own causing alt-crossing RA to be selected
        self.permtent_copy = np.full(12, False, dtype=bool) #Sense used to send intent by a $TERM threat
        self.reverse = None #Reversal RA issued for this threat on current cycle
        self.rev_geom = None #Geometric reversal in effect
        self.rev_ra = None #Reversal RA currently in effect
        self.tiebreaker_reversal = None #Own must reverse due to lost tiebreaker
        self.valconvs = None #Valid multiaircraft converging indicator
        self.valrevs = None #Valid reversal modeling indicator

        """Group delay"""
        self.badfok = None #Sense chosen despite low firmness
        self.ifirm = None #Firmness of vertical track
        self.levelwait = None #No. of cycles own TCAS has waited for intent
        self.zdinr = None #Slacker bound of rate uncertainty
        self.zdoutr = None #Steeper bound of rate uncertainty

        """Group mdf"""
        self.cov = np.zeros((2,2)) #Covariance matrix
        self.dtb = None #Time increment for bearing based tracker
        self.hfirm = None #Horizontal firmness for range based trackers
        self.hfirmb = None #Horizontal firmness used for bearing based tracker
        self.hmd = None #Predicted HMD from parabolic range tracker
        self.hmd_last = None #Last HMD projection before coast
        self.hmdrb = None #Predicted HMD from bearing based tracker
        self.init = None #Initialization flag for range based trackers
        self.initb = None #Initialization flag for bearing based tracker
        self.manct = None #Maneuver count
        self.mdf_hit_count = 0 #Count of consecutive HMD predictions above threshold
        self.numdpx = None #Count of consecutive same sign cross-range residuals from bearing based tracker
        self.rdd = None #Tracked range acceleration
        self.rddd = None #Tracked change rate of range acceleration
        self.rddl = None #Cartesian range tracker: range acceleration
        self.rdl = None #Cartesian range tracker: range rate
        self.rl = None #Cartesian range tracker: range
        self.sgndpx = None #Sign of cross-range residual for bearing tracker
        self.smoressq = None #Smoothed value of the residual squared
        self.xds = None #Bearing based tracker: x-speed
        self.xs = None #Bearing based tracker: x-position
        self.yds = None #Bearing based tracker: y-speed
        self.ys = None #Bearing based tracker: y-position

        """Group traffic"""
        self.tacode = None #Status for display
        self.tascore = None #Priority relative to entries with same TACODE
        self.tatime = None #Time set to enforce min TA display time

        """Group timer"""
        self.dt = None #Time difference of 2 latest repts
        self.rrti = None #Time of latest range/alt. report
        self.tcmd = None #Time RA issued/changed for this intruder
        self.tdatai = None #Cycle time (TCUR) of last update


"""THREAT FILE ENTRY"""
class Tf:
    def __init__(self):
        """Group identity"""
        self.id = None #ICAO 24-bit aircraft address
        self.iptr = None #Track file row number

        """Group advisory"""
        self.permtent = np.full(12, False, dtype=bool) #Advisory saved for this threat
        self.poowrar = None #Index to own Res. Adv. array
        self.pothrar = np.full(2, 0, dtype=int) #Index to Res. Adv. Complements received from threat

        """Group level_off"""
        self.initzdi = None #Intruder’s vertical rate at time of initial RA
        self.initzdo = None #Own vertical rate at time of initial RA
        self.treconf = None #Time to reconfirm strength selection
        self.ttlo = None #Trying level-off against TCAS-equipped threat

        """Group timer"""
        self.new = None #New entry due to own Res. Adv.
        self.t_intent = None #Time intent first received from this threat
        self.tthlrcm = None #Time threat adv. refreshed


"""WORKING LIST ENTRY"""
class Wl:
    def __init__(self,iptr,status):
        """Group entry"""
        self.iptr = iptr #Index to ITF entry
        self.status = status #Entry type


"""OWN ALTITUDE TRACK FILE ENTRY"""
class Oat:
    def __init__(self):
        """Group track"""
        self.alt_credible = None #Altitude measurement found credible
        self.soft = None #Track softness factor
        self.tdat = None #Timing of last altitude measurement
        self.tupd = None #Timing of last track update
        self.z = None #Altitude estimate
        self.zd = None #Altitude rate estimate


"""STORED TRACK DATA LIST ENTRY"""
class Std:
    def __init__(self, tdata, zdata):
        """Group entry"""
        self.tdata = tdata #Stored time stamp of the altitude measurement or report, G.TADC, G.TROWN, or T depending on the source of the altitude data
        self.zdata = zdata #Stored altitude measurement or report, G.ZADC, G.ZROWN, or ZREPT depending on the source of the altitude data


"""NONLINEAR TRACK FILE ENTRY"""
class N:
    def __init__(self):
        """Group output"""
        self.alt_credible = None #Altitude measurement found credible
        self.z = None #Tracked altitude, old Z1
        self.zd = None #Tracked altitude rate, old Z2

        """Group geometry"""
        self.direc = None #Direction of previously established trend
        self.resid = None #Residual, old Z10
        self.tbin = None #Estimated time to cross alt. bin, old Z7
        self.zdinner = None #Slacker bound of rate uncertainty
        self.zdouter = None #Steeper bound of rate uncertainty
        self.zsave = None #Previous altitude report, old Z4

        """Group firmness"""
        self.binsthiszd = None #Bins crossed at current rate, old Z8
        self.casfirm = None #Firmness indicator
        self.fipreco = None #Firmness prior to coast sequence

        """Group timer"""
        self.tdat = None #Time of last altitude report, old Z3
        self.toscil = None #Time oscillation state entered
        self.tstart = None #Startup time
        self.ttran = None #Time of last transition, old Z5
        self.tupdt = None #Time of last track update, old Z6

        """Group general"""
        self.class_ = None #Track classification
        self.q = None #Track quantization>
        self.stdptr = [] #Stored Track Data (STD) object
        self.std_num_pts = None #Number of data points stored in STD structure

        """Group alpha_beta"""
        self.initcompleted = None #Indicator of completion of initialization
        self.usealphabeta = None #Indicator to use alpha-beta smoothing
        self.z_ab = None #Alpha-beta tracked altitude
        self.zd_ab = None #Alpha-beta tracked altitude rate
        self.zdd_ab = None #Alpha-beta tracked altitude acceleration


"""GLOBAL VARIABLES"""
class G:
    def __init__(self):
        """Group status"""
        self.airdata = None #Fine altitude data available
        self.ground_mode = None #'1' = Traffic display permitted on ground
        self.initcycle = None #Counted up to P.INITCOUNT cycles after initialization; during this count-up, descend and increase descend RAs are inhibited
        self.initflg = None #System initializing
        self.intmode = None #Interrogation enabled
        self.macflg = None #Multiple threats
        self.nptr = None #Own nonlinear track file, if mode-C tracking used
        self.oatptr = None #own altitude track object used by the AIRDATA_TRACKER
        self.opflg = None #System operational
        self.radarout = None #Number of cycles without radar alt. data
        self.radarvalid = None #'1' = Valid and credible radar altitude data this cycle
        self.ramode = None #Resolution advisories enabled
        self.ramode_on = None #Time that RA mode was enabled
        self.stdptr = None #Stored Track Data (STD) object
        self.std_num_pts = None #Number of data points stored in STD structure
        self.tadc = None #Time of fine altitude report
        self.tamode = None #Traffic advisories enabled
        self.tcur = None #Time of current processing cycle
        self.tracking_airdata = None #‘1’ = AIRDATA_TRACKER is used for own; ‘0’ = VERTICAL_TRACKER is used for own
        self.trown = None #Time of Mode C altitude report
        self.zadc = None #Own fine altitude
        self.zrown = None #Own Mode C altitude report

        """Group sensitivity"""
        self.index = None #Own sensitivity level
        self.layer = None #Altitude-related sensitivity level
        self.levelsit = np.full(16, 0, dtype=int) #Sens. levels sent from ground sites
        self.leveltim = np.zeros(16) #Time each level refreshed

        """Group position"""
        self.climbinhib = None #Own aircraft cannot climb at 1500 fpm
        self.inc_desinhib = None #Increase Descent RAs inhibited
        self.nodescent = None #Own near ground; descend RAs inhibited
        self.oogroun = None #Own aircraft on ground
        self.zground = None #Ground elevation estimate
        self.zown = None #Own tracked altitude
        self.zowncor = None #Own corrected barometric altitude
        self.zdown = None #Own tracked altitude rate
        self.zdtv = None #Saved tracked altitude rate
        self.zradar = None #Own radar altimeter report
        self.ztv = None #Saved tracked altitude

        """Group settable"""
        self.alim = None #Positive advisory alt. threshold
        self.sensfirm = None #Required separation assuming no vert. tracking error
        self.zthr = None #Detection alt. threshold
        self.zthr_ta = None #Traffic advisory detection altitude threshold

        """Group altitude_alerter"""
        self.alerter_alt = None #Altitude indicated by the altitude alerter
        self.alerter_ok = None #Indicates if alterter information can be used
        self.alerter_time = None #Time the alerter altitude last changed

        """Group resolution"""
        self.colock = None #Coordination Lock
        self.idown = None #Own aircraft's ICAO 24-bit aircraft address
        self.intent = np.full(4,False,dtype=bool) #Threat Resolution Advisory Complement array
        self.mac_new = None #New threat counter
        self.mac_reverse = None #Reversal indication for multiaircraft encounter
        self.man_reverse = None #Reversal indication for threat maneuver
        self.maneuver_reversal = None #Converging reversal indication
        self.ra = np.full(14,False,dtype=bool) #Resolution Advisory Array
        self.threat_count = None #Threat counter
        self.tlastnewra = None #Time of last RA issued for a new threat
        self.tlock = None #Time Lock State initiated
        self.tposra = None #Time positive RA first issued

        """Group display"""
        self.alarm = None #Sound aural alarm
        self.allclear = None #Announce "clear of conflict" message
        self.anycorchang = None #Changed RA is corrective
        self.anycross = None #Encounter is an altitude cross
        self.anyincrease = None #Increase rate RA issued
        self.anynewthr = None #RA due to new threat
        self.anyprecor = None #RA changed from preventive to corrective
        self.anyreverse = None #RA reversal issued
        self.clstrold = None #Previous value of CLSTRONG
        self.clstrong = None #Strongest climb sense RA
        self.corrective_clm = None #Climb sense RA is corrective
        self.corrective_des = None #Descend sense RA is corrective
        self.destrold = None #Previous value of DESTRONG
        self.destrong = None #Strongest descend sense RA
        self.maintain = None #Positive RA is preventive
        self.previncrease = None #Increase rate RA issued previous scan
        self.turn_off_aurals = None #If set, aural annunciations are inhibited
        self.zdmodel = None #Escape rate to maintain for safe separation
        self.extalt = None #Indicate an extreme altitude condition

        """Group cross_reference"""
        self.crefptr = np.full(100, None, dtype=Itf) #Array of pointers to ITF entries indexed on surveillance buffer numbers

        """Group reversal"""
        self.own_follow = None #Indication of own following RAs or not
        self.rev_consdrd = None #Indication of a vertical chase, low VMD geometry detected
        self.ttofollow = None #Time to follow RA
        self.bounded_ttf = None #Bounded time to follow initial RA

        """Group broadcast"""
        self.active = None #Indicates if active information is being stored for a threat 0= no threat info, 1= Mode S info, 2= Mode C info
        self.aid = np.full(13,False,dtype=bool) #Mode A identity code
        self.altnew = None #Reported altitude of the newest Mode C threat
        self.brdcst = None #Indication that broadcast is being performed
        self.brngnew = None #Bearing of the newest Mode C threat
        self.brngvalid = None #Bearing validity indicator of the newest Mode C threat
        self.cac = np.full(13,False,dtype=bool) #Mode C altitude code
        self.crossing_ra = None #RA is altitude crossing—set each cycle RA is crossing
        self.id = None #ICAO 24-bit aircraft address of the newest threat
        self.ncycle = None #Number of cycles since RA was broadcast
        self.pointer = None #newest threat object
        self.prevmte = None #"Multiple Threat Encounter" flag from the previous cycle
        self.prevra = np.full(14,False,dtype=bool) #Resolution advisory array from the previous cycle
        self.reversal_ra = None #RA sense has reversed—stays set for duration of RA
        self.rngnew = None #Range of the newest Mode C threat
        self.rngvalid = None #Range validity indicator of the newest Mode C threat
        self.transvi = None #Own transponder version indicator


"""OWN AIRCRAFT DATA INPUT"""
class O:
    def __init__(self):
        """Group status"""
        self.aid = np.full(13,False,dtype=bool) #Mode A identity code
        self.alerter_avail = None #Indicates if altitude alerter information is available
        self.ground_mode = None #'1' = Traffic display permitted on ground
        self.idown = None #Own aircraft's ICAO 24-bit aircraft address
        self.manual = None #Manual sensitivity level selection
        self.radarvalid = None #'1' = Valid and credible radar altitude data this cycle
        self.tcasop = None #TCAS operational status
        self.transvi = None #Own transponder version indicator

        """Group geometry"""
        self.alerter_value = None #Altitude indicated by the altitude alerter in 1 ft
        self.tadc = None #Time of fine altitude report
        self.trown = None  # Time of Mode C alt. report
        self.zadc = None  # Own fine altitude
        self.zowncor = None #Own corrected barometric altitude
        self.zrown = None  # Own Mode C altitude report
        self.zradar = None #Radar altimeter report


"""REALTIME CLOCK DATA"""
class Realtime:
    def __init__(self):
        """Group data"""
        self.tclock = None #Onboard realtime clock


"""INTRUDER SURVEILLANCE BUFFER DATA"""
class S:
    def __init__(self):
        """Group identity"""
        self.eqp = None #Equipage
        self.idintr = None #Mode-S discrete address, if any
        self.modc = None #Intruder is reporting altitude
        self.plint = None #Sensitivity level (=0 for non-TCAS II)
        self.survmode = None #Surveillance mode (normal, reduced)
        self.survno = None #Surveillance buffer number

        """Group geometry"""
        self.bear = None #Intruder bearing relative to own heading. Used for display (may be tracked in surveillance).
        self.bearok = None #Valid data in BEAR
        self.bear_meas = None #Surveillance bearing measurement (untracked). Used for horizontal miss distance filtering.
        self.bear_meas_ok = None #Valid data in BEAR_MEAS
        self.rflg = None #Valid data in RR. 0=coast
        self.rq = None #Quantization bit of the alt report
        self.rr = None #Range report
        self.rrtime = None #Time stamp for range/alt report
        self.zflg = None #Valid data in ZRINT
        self.zrint = None #Mode-C altitude report


"""GROUND ALTITUDE DATA"""
class Groundalt:
    def __init__(self):
        """Group data"""
        self.zground = None #Ground altitude. Note: This datum is supplied to the CAS logic every cycle, whether or not any intruder is under surveillance.
        self.zvalid = None #Valid data in ZGROUND; 1=valid, 0=invalid


"""SYSTEM PARAMETERS"""
class P:
    def __init__(self):
        """Group track"""
        self.alfao = ALFAO #Own fine altitude smoothing
        self.betao = BETAO #Own fine alt. rate smoothing
        self.credzadc = CREDZADC #Credibility window parameter for ADC altitude data
        self.maxsoft = MAXSOFT #Maximum softness factor for ADC track
        self.min_pts_for_switch = 3 #Minimum number of consecutive altitude data from alternate source to switch altitude tracker
        self.minsoft = 3 #Minimum softness factor for ADC track

        """Group sensitiviy"""
        self.automatic = 0 #TCAS is in automatic mode; SL selected basedon alt.
        self.bot = BOT #Lower hysteresis bounds for alt.-sensitive parameters
        self.top = TOP #Upper hysteresis bounds for alt.-sensitive parameters
        self.radarlost = RADARLOST #No. cycles without radar alt. to invoke default
        self.sitmax = 15 #Number of ground sites that can set sensitivity
        self.stimout = STIMOUT #Timeout for ground SL command
        self.ta_only = 2 #TCAS is in TA-only mode; no RAs permitted
        self.zlarge = ZLARGE #Large positive altitude
        self.zlimitl = ZLIMITL #Radar altitude lower limit to declare own on ground
        self.zlimitu = ZLIMITU #Radar altitude upper limit to declare own on ground
        self.zsl2to3 = ZSL2TO3 #Upper SL 2/3 boundary
        self.zsl3to2 = ZSL3TO2 #Lower SL 2/3 boundary
        self.zsl3to4 = ZSL3TO4 #Upper SL 3/4 boundary
        self.zsl4to3 = ZSL4TO3 #Lower SL 3/4 boundary
        self.zsl4to5 = ZSL4TO5 #Upper SL 4/5 boundary
        self.zsl5to4 = ZSL5TO4 #Lower SL 4/5 boundary
        self.zsl5to6 = ZSL5TO6 #Upper SL 5/6 boundary
        self.zsl6to5 = ZSL6TO5 #Lower SL 5/6 boundary
        self.zsl6to7 = ZSL6TO7 #Upper SL 6/7 boundary
        self.zsl7to6 = ZSL7TO6 #Lower SL 6/7 boundary

        """Group alerter"""
        self.alerter_tmax = ALERTER_TMAX #Maximum time for alerter data to be considered valid
        self.alerter_tmin = ALERTER_TMIN #Minimum time for alerter data to be considered valid
        self.levoffaccx2 = LEVOFFACCX2 #Level off acceleration (x2) assumed by alerter logic

        """Group detect"""
        self.dmodtbl = DMODTBL #Incremental range protection
        self.h1tbl = H1TBL #Divergence range*range rate hyperbola
        self.lowfirmrz = LOWFIRMRZ #Alt. cross threshold on low firmness
        self.maxaltdiff = MAXALTDIFF #Max. altitude difference to issue a crossing RA when either own or intruder aircraft is level, or when their vertical rates have the same sign
        self.maxaltdiff2 = MAXALTDIFF2 #Max. altitude difference to issue a crossing RA when their vertical rates have opposite signs
        self.maxzdint = MAXZDINT #Max. altitude rate for issuing an RA
        self.nafrange = NAFRANGE #Minimum range to filter nuisance alarms
        self.rdthr = RDTHR #Small range rate for tau calc.
        self.rmax = RMAX #Maximum range for threat detection
        self.rrd_thr = RRD_THR #Range-range rate product counter threshold
        self.taurise_thr = 3 #cycles tau must rise to filter nuisance alarms
        self.trtetbl = TRTETBL #Range tau limit, equipped intrude
        self.trtutbl = TRTUTBL #Range tau limit, unequipped intruder
        self.tvpctbl = TVPCTBL #Max. projection for VMD calculation
        self.tvpetbl = TVPETBL #Max. projection modeling escape
        self.tvtetbl = TVTETBL #Altitude tau limit, equipped intruder
        self.tvtutbl = TVTUTBL #Altitude tau limit, unequipped intruder
        self.tvvtt_tbl = TVVTT_TBL #Altitude tau limit for Vertical Threshold Test (VTT)
        self.zdthr = ZDTHR #Small vertical rate to inhibit zero-divide for tau calc.
        self.zt = ZT #Immediate altitude threshold
        self.zt_ta = ZT_TA #Altitude threshold for Traffic Advisories

        """Group delay"""
        self.mintau = MINTAU #Lower limit for tau and value when diverging
        self.rabrdcst = 1 #Delay between one RA broadcast and the next
        self.sf = SF #Req'd sep. for bad firmness hit using vert rate limits
        self.tiethr = TIETHR #Delay threshold for tiebreaker reversal
        self.wtthr = 2 #Waiting threshold for receipt of TCAS threat's intent

        """Group model"""
        self.adeqsep = ADEQSEP #Min. sep needed for detection logic
        self.backdelay = BACKDELAY #Floor on (current time - begin-maneuver time)
        self.clmrt = CLMRT #Nominal rate of response to positive climb
        self.desrt = DESRT #Nominal rate of response to positive descent
        self.minrvstime = MINRVSTIME #Min.time for reversal for threat close in alt.
        self.min_ri_time = MINRITIME #Min.time to inhibit reversals and increases
        self.model_t = MODEL_T #Time limit for using modeled rather than tracked alt.
        self.model_zd = MODEL_ZD #Rate limit for using modeled rather than tracked alt.
        self.nozcross = NOZCROSS #Incr. sep req'd to cross alt when can't climb
        self.quikreac = QUIKREAC #Pilot delay time between RA's
        self.raccel = RACCEL #Acceleration response to Sense Reversal RA
        self.tmin = TMIN #Timer to display RA 5-sec minimum
        self.tv1 = TV1 #Response delay to first RA
        self.vaccel = VACCEL #Nominal acceleration responding to RA
        self.zdesbot = ZDESBOT #Own final altitude after leveloff at NODESLO

        """Group seladv"""
        self.al = AL #Positive advisory threshold
        self.ilev = ILEV #Vertical rate inducing immediate positive RA
        self.lev_rev = LEV_REV #Threshold for level-off/reversal in multiaircraft conflict
        self.mac_hist1 = MAC_HIST1 #Hysteresis for positive to dual negative RA test
        self.mac_hist2 = MAC_HIST2 #Hysteresis for RA reversal test
        self.mac_inc = MAC_INC #Threshold for increase rate in multiaircraft conflict
        self.maxdrate = MAXDRATE #Maximum displayable rate for modeling
        self.mindrate = MINDRATE #Minimum displayable rate for modeling
        self.newvsl = NEWVSL #Factor by which VSL assumed to be violated
        self.nodeshi = NODESHI #Ceiling on own alt.AGL to issue DESCEND RAs
        self.nodeslo = NODESLO #Floor on own alt. AGL to issue DESCEND RAs
        self.olev = OLEV #A "substantial" vertical rate
        self.strofir = STROFIR #Tau ceiling to delay stronger RA if bad firmness
        self.tnoweak = NOWEAK #Time advisory not allowed to weaken
        self.trvsnoweak = TRVSNOWEAK #Time adv. not allowed to weaken in reversals
        self.ttlorate = TTLORATE #Minimum vertical rate for own needed to force initial level-off against TCAS-equipped threat
        self.ttlosep = TTLOSEP #Minimum proj. separation with negative RA needed to force initial level-off against TCAS-equipped threat
        self.ttlozd = TTLOZD #Adverse change in vertical rate needed to reconsider positive strength against TCAS-equipped threat
        self.v1000 = V1000 #1000 ft/min limit
        self.v2000 = V2000 #2000 ft/min limit
        self.v500 = V500 #500 ft/min limit

        """Group eval"""
        self.avevalt = AVEVALT #Required separation to pass Increase Rate test
        self.avevtau = AVEVTAU #Tau ceiling to perform Increase Rate test
        self.inc_add_sep = INC_ADD_SEP #Required additional separation for Increase Rate RA
        self.inc_tau_thr = INC_TAU_THR #Tau threshold used in the Increase Rate RA logic
        self.initcount = INITCOUNT #Number of cycles immediately after initialization over which descend and increase descend inhibit are enforced regardless of altitude limits
        self.minfirm = 2 #Minimum intruder firmness used in detection, strength selection, Increase Rate, and Reversal logics
        self.zno_incdeshi = ZNOINCDESHI #Upper alt. limit to issue Increase Descent RAs
        self.zno_incdeslo = ZNOINCDESLO #Lower alt. limit to issue Increase Descent RAs

        """Group coordination"""
        self.hmapintent = HMAPINTENT #Map codes in coordination msg into horizontal INTENT array
        self.vmapintent = VMAPINTENT #Map codes in coordination msg into vertical INTENT array
        self.tcatres = TCATRES #Time to clean up stray TF entry
        self.trymax = TRYMAX #Interrogation limit when no response
        self.tunlock = 0.5 #Limit for coordination lock state
        self.ptableh = PTABLEH #HSB parity table to confirm validity of RA msg
        self.ptablev = PTABLEV #VSB parity table to confirm validity of RA msg

        """Group correct_prev"""
        self.climbgoal = CLIMBGOAL #Expected rate for climb sense RA
        self.desgoal = DESGOAL #Expected rate for desc. sense RA
        self.huge = HUGE #Large constant
        self.hystercor = HYSTERCOR #Hysteresis for corrective/preventive test

        """Group general"""
        self.crossthr = CROSSTHR #Altitude-crossing threshold
        self.crossthrl = 100*0.3048 #ft Large altitude-crossing threshold
        self.largeint = 100000 #General-purpose large integer
        self.tinit = -1. #Initial value for timer variables

        """Group display"""
        self.inc_clmrate = INC_CLMRATE #Climb rate for increase rate RA
        self.inc_desrate = INC_DESRATE #Descend rate for increase rate RA

        """Group traffic"""
        self.abovnmc = ABOVNMC #Max. alt. to display traffic adv. on int. not reporting alt.
        self.dmodta_tbl = DMODTA_TBL #Incremental range volume
        self.hiscore = HISCORE #TASCORE for $RA type
        self.h1ta_tbl = H1TA_TBL #Range*Range rate divergence
        self.loscore = LOSCORE #nominal TASCORE for proximity type
        self.medhiscore = MEDHISCORE #nominal TASCORE for nearest intruders
        self.medloscore = MEDLOSCORE #nominal TASCORE for diverging intruder
        self.medscore = 400. #nominal TASCORE for converging intruder
        self.mintatime = MINTATIME #Minimum display time for a TA
        self.proxa = PROXA #Altitude limit for proximity alert
        self.proxr = PROXR #Range limit for proximity alert
        self.rdthrta = RDTHRTA #Range rate limit for tau calc.
        self.tarhyst = TARHYST #Hysteresis for TA range threshold
        self.tinyscore = TINYSCORE #Nominal TASCORE for intruder with no advisory
        self.trthrta_tbl = TRTHRTA_TBL #Range tau for Threat alert
        self.tvthrta_tbl = TVTHRTA_TBL #Altitude tau for Threat alert
        self.zdthrta = ZDTHRTA #Alt. rate limit for tau calc.
        self.zno_auralhi = ZNO_AURALHI #Upper "aurals inhibited" boundary
        self.zno_aurallo = ZNO_AURALLO #Lower "aurals inhibited" boundary

        """Group mdf"""
        self.accthr = P_ACCTHR #Nominal acceleration threshold
        self.alphal = ALPHAL #Alphas for Cartesian tracker
        self.alphap = ALPHAP #Alphas for parabolic tracker
        self.alpharb = ALPHARB #Alphas for Range/Bearing tracker
        self.alpharessq = P_ALPHARESSQ #Alpha for smoothing square of range residuals
        self.alpha3d = P_ALPHA3D #Alpha for smoothing third derivative of range
        self.bbcc_disable_val = BBCC_DISABLE_VAL #HMD value that disables bearing based cross check
        self.bear_firm_sm_man = 4 #Bearing tracker firmness after small maneuver detected
        self.betal = BETAL #Betas for Cartesian tracker
        self.betap = BETAP #Betas for parabolic tracker
        self.betarb = BETARB #Betas for Range/Bearing Tracker
        self.coast_accel = COAST_ACCEL #Acceleration to decrement HMD projection during coast
        self.dmod_mdf = DMOD_MDF #DMOD value to initiate bearing tracker
        self.dpxconsec = 10 #Maximum number of consecutive same sign residuals
        self.gammal = GAMMAL #Gammas for Cartesian tracker
        self.gammap = GAMMAP #Gammas for parabolic tracker
        self.hmd_disable_val = HMD_DISABLE_VAL #Value for HMD prediction disabling MDF this cycle
        self.hmdmult = HMDMULT #Hysteresis value for HMD threshold when KHIT is set
        self.hmdthr = HMDTHR #Horizontal miss-distance thresholds for each SL
        self.inithoddthr = P_INITRHODDTHR #Initial range acceleration threshold
        self.maxf = 8 #Maximum horizontal firmness level
        self.maxrangeresid = P_MAXRANGERESID #Maximum range residual
        self.mininithfirm = 3 #Minimum horizontal firmness to stay initialized
        self.mnsigdpx = P_MINSIGDPX #Minimum number of variances in same sign residuals
        self.mnvr_shtdwn_tm = 10 #Number cycles MDF is disabled after maneuver detected
        self.mxsigdpx = P_MAXSIGDPX #Maximum number of variances in same sign residuals
        self.nsgsnct = NSGNCT #Minimum number of standard deviations cross track residual must exceed to begin count of same sign residuals
        self.p_noise_factor = P_P_NOISE_FACTOR #Number of standard deviations process noise is inflated by after a large maneuver is detected with bearing tracker
        self.procnoivar = P_PROCNOIVAR #Process noise variance
        self.rbratio = 2. #Ratio of acceptable bearing based to range based HMD projection
        self.rb_tau_thresh = 100. #TAUR threshold to enable bearing based tracking
        self.resdl_sigmas = P_RESDL_SIGMAS #Number of standard deviations cartesian residual must exceed for maneuver detection
        self.ressd_n = P_RESSD_N #Nominal standard deviation of range tracker residual
        self.ressd_c_exp_fact = P_RESSD_C_EXP_FACT #Expansion factor for nominal standard deviation of Cartesian residual
        self.tmin_mdf = TMIN_MDF #Cycles MDF must be satisfied to filter an existing RA
        self.vrbrng = P_VAR_BRNG #Bearing measurement variance


"""NLTF PARAMETERS"""
class Pn:
    def __init__(self):
        """Group general"""
        self.dt = DT #Nominal update time
        self.zdlarge = ZDLARGE #Steepest confidence limit on ZD
        self.zdlikely = ZDLIKELY #Most likely vertical rate after a transition

        """Group credibility"""
        self.credaccdiv2 = CREDACCDIV #Credible altitude acceleration divided by 2
        self.credinit = CREDINIT #Initial credibility window size
        self.credmindt = CREDMINDT #Minimum time to narrow credibility window
        self.credzderr = CREDZDERR #Credible altitude rate estimate error

        """Group no_transition"""
        self.delzdt = DELZDT #Minimum time for rate adjustment
        self.latelevel = LATELEVEL #Bincross discrepancy to declare ZD=0
        self.lateslack = LATESLACK #Bincross discrepancy to slacken ZD
        self.tgolev = TGOLEV #Interval of unchanged reports to declare ZD=0
        self.tinitzd = TINITZD #Time to obtain a reasonable rate estimate
        self.zddecay = 0.9 #Decay factor for ZD when CLASS=$GUESS

        """Group no_trans_firmness"""
        self.guesdu1 = GUESDU1 #Bin occupancy time to rule out steep rate
        self.guesdu2 = GUESDU2 #Bin occupancy time to rule out moderate rate
        self.guesdu3 = GUESDU3 #Bin occupancy time to imply leveloff
        self.overdue = OVERDUE #Time for a late transition to indicate leveloff

        """Group transition"""
        self.earlylate = EARLYLATE #Bincross discrepancy to ignore prior history, reinit. rate
        self.guesrate = GUESRATE #Vertical Rate estimate when bincross follows level
        self.longcoast = LONGCOAST #Time between successive reports for special handling
        self.maxbins = MAXBINS #Hard maximum value for BINSTHISZD
        self.maxzdtime = MAXZDTIME #Maximum time associated with the current rate
        self.residecay = RESIDECAY #RESID adjustment when substantial bincross discrepancy
        self.residimin = RESIDIMIN #RESID adjustment when slight bincross discrepancy
        self.sliteoff = SLITEOFF #Bincross discrepancy to adjust RESID
        self.tbinhi = TBINHI #Maximum bin crossing time to switch smoothing
        self.tbinlo = TBINLO #Minimum bin crossing time to switch smoothing
        self.tbinmin = TBINMIN #Minimum value for an initial estimate of TBIN
        self.ttrendmin = TTRENDMIN #Minimum time for a trend to be reliable
        self.zrjit = ZRJIT #Time near bin bndry when track vulnerable to spurious osc

        """Group transition_firmness"""
        self.delzthr = DELZTHR #Predicted altitude error threshold
        self.hi1 = HI1 #Excess in actual/expected bincross, poor firmness
        self.hi2 = HI2 #Excess in actual/expected bincross, good firmness
        self.hi3 = HI3 #Excess in actual/expected bincross, maximumfirmness
        self.lo1 = LO1 #Deficiency in actual/expected bincross, poor firmness
        self.lo2 = LO2 #Deficiency in actual/expected bincross, good firmness
        self.lo3 = LO3 #Deficiency in actual/expected bincross, maximum firmness
        self.out2 = OUT2 #Bincross discrepancy floor, good firmness
        self.out3 = OUT3 #Bincross discrepancy floor, maximum firmness
        self.slacken1 = SLACKEN1 #Bin occupancy time needed for poor firmness
        self.slacken2 = SLACKEN2 #Bin occupancy time needed for good firmness
        self.zdfracc = ZDFRACC #Uncertainty factor in ZD due to possible acceleration

        """Group select_smothing"""
        self.nbinsnl = NBINSNL #Value given to BINSTHISZD when switching back to bin occupancy smoothing

        """Group alpha_beta_smoothing"""
        self.alphaz = ALPHAZ #Altitude smoothing coefficient
        self.betaz = BETAZ #Altitude rate smoothing coefficient
        self.dtcoast = DTCOAST #Minimum coast time for firmness adjustment
        self.dzthr_100 = DZTHR_100 #Predicted altitude threshold for 100ft quantization
        self.dzthr_25 = DZTHR_25 #Predicted altitude threshold for 25ft quantization

        """Group alpha_beta_tracker"""
        self.bndac = BNDAC #Factor used in the calculation of the rate bounds
        self.bndzd = BNDZD #Difference between altitude rate and rate bound
        self.dtlong = DTLONG #Time since last transition to consider track level
        self.dtstart = DTSTART #Minimum time to initialize the altitude rate estimate
        self.gammaz = GAMMAZ #Smoothing coefficient for acceleration rough estimate
        self.hugedz = HUGEDZ #Size of prediction error causing re-initialization
        self.largedz = LARGEDZ #Large altitude prediction error for 25ft quantization
        self.minbins = MINBINS #Minimum value of BINSTHISZD
        self.smallzd = SMALLZD #Small ZD_AB estimate indistinguishable from 0
        self.tinyzd = TINYZD #Small ZD estimate indistinguishable from 0
        self.zdabthr = ZDABTHR #Rate threshold for small alpha-beta values
        self.zddabthr = ZDDABTHR #Acceleration threshold for rate bound adjustment


"""OWN DATA TO SURVEILLANCE"""
class Owndata_to_surv:
    def __init__(self):
        """Group altitude"""
        self.oogroun = None #Own aircraft on ground
        self.radarvalid = None #Validity of radar altitude; 1=valid, 0=invalid
        self.zown = None #Own barometric altitude in feet
        self.zradar = None #Own radar altitude in feet

        """Group data"""
        self.intmode = None #Interrogation enabled; 1=enabled


"""OWN DATA TO TRANSPONDER EVERY CYCLE"""
class Owndata_to_trans:
    def __init__(self):
        """Group sl_report"""
        self.ri = None #Air to air reply information
        self.sl = None #sensitivily level
        self.vi = None #Version Indicator; 1= TCAS is compatible with RTCA/DO-185A

        """Group datalink_capability_report"""
        self.bit_48 = None #data link subfield bit 48 in MB
        self.bit_69 = None #data link subfield bit 69 in MB
        self.bit_70 = None #data link subfield bit 70 in MB
        self.bit_71 = None #data link subfield bit 71 in MB
        self.bit_72 = None #data link subfield bit 72 in MB


"""RA OUTPUT TO DISPLAY AND AURAL SUBSYSTEM EVERY CYCLE"""
class To_disp_aural:
    def __init__(self):
        """Group ra_display_and_aural"""
        self.combined_control = None #combined control
        self.down_advisory = None #down_advisory
        self.rate = None #advisory rate to maintain
        self.up_advisory = None #up_advisory
        self.vertical_control = None #vertical_control

        """Group additional_aural"""
        self.crossing = None #crossing indication; 1=crossing, 0=not crossing


"""RA_OUTPUT TO MODE S TRANSPONDER EVERY CYCLE DURING RA"""
class Ra_to_trans:
    def __init__(self):
        """Group coordination_and_comm_b"""
        self.ara = np.full(14,False,dtype=bool) #active RA
        self.mte = None #multiple threat encounter
        self.rac = np.full(4,False,dtype=bool) #RA complement
        self.rai = None #RA indicator
        self.tid = np.full(26,False,dtype=bool) #threat identity data; ICAO 24-bit aircraft address or for non-Mode S aircraft, altitude, range and bearing
        self.tti = np.full(2,False,dtype=bool) #threat type indicator


"""RA BROADCAST OUTPUT TO GROUND STATIONS EVERY 8 cycles"""
class To_ground_station:
    def __init__(self):
        """Group ra_broadcast"""
        self.aid = np.full(13,False,dtype=bool) #Mode A identity code
        self.ara = np.full(14,False,dtype=bool) #active RA
        self.cac = np.full(13,False,dtype=bool) #Mode C altitude code
        self.mte = None #multiple threat encounter
        self.rac = np.full(4,False,dtype=bool) #RA complement
        self.rat = None #RA terminated indicator


"""RA INTENT OUTPUT TO THREAT WHEN RA IS IN EFFECT"""
class Intent_to_threat:
    def __init__(self):
        """Group ra_intent"""
        self.chc = None #cancel horizontal RAC
        self.cvc = None #cancel vertical RAC
        self.hrc = None #horizontal RAC
        self.hsb = None #horizontal sense bits subfield
        self.mid = None #ModeS address of the interrogating aircraft
        self.mtb = None #multiple threat bit
        self.vrc = None #vertical RAC
        self.vsb = None #vertical sense bits subfield


"""CREDIBILITY CHECK OUTPUT TO PERFORMANCE MONITOR"""
class Cas_to_monitor:
    def __init__(self):
        """Group check"""
        self.alt_credible = None #Altitude measurement found credible


"""COPY OF PREVIOUS CYCLE’S DATA FOR FINAL RA BROADCAST"""
class Brdcst_data:
    def __init__(self):
        """Group final_broadcast"""
        self.prv_aid = np.full(13,False,dtype=bool) #Previous cycle’s value of AID
        self.prv_ara = np.full(14,False,dtype=bool) #Previous cycle’s value of ARA
        self.prv_cac = np.full(13, False, dtype=bool) #Previous cycle’s value of CAC
        self.prv_mte = None #Previous cycle’s value of MTE
        self.prv_rac = np.full(4, False, dtype=bool) #Previous cycle’s value of RAC