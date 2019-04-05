import numpy as np

"""VALUES OF ITF.EQP"""
TCAS = 3 #TCAS-equipped with on-board RA capability
ATCRBS = 2 #all non-Mode-S
TCASTA = 1 #TCAS-equipped with NO on-board RA capability
MODES = 0 #Mode-S, possibly TCAS-I

"""VALUES OF ITF.TACODE"""
RA = 4 #Resolution advisory due to intruder
TAMC = 3 #Threat Traffic advisory, Mode-C intruder
TANMC = 2 #Threat Traffic advisory, non-Mode-C intruder
PA = 1 #Proximity advisory
NOTAPA = 0 #No advisory for intruder

"""VALUES OF ITF.SURVMODE"""
NORMAL = False #Surveillance nominally performed once every second
REDUCED = True #Surveillance nominally performed once every 5 seconds

"""WL.STATUS VALUES"""
CONT = 2 #Threat continuing from prior cycle
NEW = 1 #New threat this cycle
TERM = 0 #Threat status terminated this cycle

"""N.CLASS VALUES"""
NEW_TRACK = 4 #Track newly started for which no transition has occurred
TREND = 3 #Confirmed upward or downward trend
OSCIL = 2 #Transitions oscillating
LEVEL = 1 #Track is level: no transition for a long time
GUESS = 0 #Single transition, trend not confirmed

"""QUANT VALUES"""
ONEHUNDRED = False #Altitude report is quantized to 100 ft
TWENTY_FIVE = True #Altitude report is quantized to 25 ft

"""COMBINED_CONTROL VALUES"""
COMBINED_CONTROL_NONE = 4 #combined control no advisory
CLEAR_OF_CONFLICT = 3 #clear of conflict
CLIMB_CORR = 2 #climb corrective
DESCEND_CORR = 1 #descend corrective
PREVENTIVE = 0 #preventive

"""VERTICAL_CONTROL VALUES"""
VERTICAL_CONTROL_NONE = 4 #vertical control none of the following
CROSSING = 3 #crossing
REVERSE = 2 #reversal
INCREASE = 1 #increase
MAINTAIN = 0 #maintain

"""UP_ADVISORY VALUES"""
UP_ADVISORY_NONE = 5 #up advisory none
CLIMB = 4 #climb
DONT_DESCEND = 3 #don't descend
DONT_DESCEND500 = 2 #don't descend 500
DONT_DESCEND1000 = 1 #don't descend 1000
DONT_DESCEND2000 = 0 #don't descend 2000

"""DOWN_ADVISORY VALUES"""
DOWN_ADVISORY_NONE = 5 #down advisory none
DESCEND = 4 #descend
DONT_CLIMB = 3 #don't climb
DONT_CLIMB500 = 2 #don't climb 500
DONT_CLIMB1000 = 1 #don't climb 1000
DONT_CLIMB2000 = 0 #don't climb 2000

"""GLOBAL CONSTANT"""
AB_COEFF = 3
ABOVNMC = 15500*0.3048 #m
ADEQSEP = 100*0.3048 #m
ALERTER_TMAX = 300 #s
ALERTER_TMIN = 5 #s
ALFAO = 0.58
AVEVALT = 200*0.3048 #m
BACKDELAY = -2.5 #s
BBCC_DISABLE_VAL = 100*1852 #m
BETAO = 0.25
CLMRT = (1500*0.3048)/60 #m/s
COAST_ACCEL = 32.2*0.3048 #m/s^2
CREDACCDIV = 20.0*0.3048 #m/s^2
CREDINIT = 200*0.3048 #m/s
CREDMINDT = 5.5 #s
CREDZADC = 65.0*0.3048 #m
CREDZDERR = 30.0*0.3048 #m/s
CROSSTHR = 100*0.3048 #m
DELZDT = 4.0 #s
DELZTHR = 20.0*0.3048 #m
DESRT = -(1500*0.3048)/60 #m/s
DMOD_MDF = 18000*0.3048 #m
DT = 1.0 #s
DTCOAST = 2.5 #s
DTLONG = 6.5 #s
DTSTART = 2.5 #s
DZTHR_100 = 60.0*0.3048 #m
DZTHR_25 = 22.5*0.3048 #m
EARLYLATE = 1.5 #s
GAMMAZ = 0.5
GUESDU1 = 4.5 #s
GUESDU2 = 9.5 #s
GUESDU3 = 14.5 #s
GUESRATE = (480*0.3048)/60 #m/s
HI1 = 2.0
HI2 = 1.5
HI3 = 1.25
HISCORE = 1200
HMD_DISABLE_VAL = -1*0.3048 #m
HMD_RB_TAU_THRESHOLD = 100 #s
HMDMULT = 1.05
HUGE = (100000*0.3048)/60 #m/s
HUGEDZ = 75*0.3048 #m
HYSTERCOR = (300*0.3048)/60 #m/s
ILEV = (1000*0.3048)/60 #m/s
INC_ADD_SEP = 50*0.3048 #m
INC_CLMRATE = (2500*0.3048)/60 #m/s
INC_DESRATE = (-2500*0.3048)/60 #m/s
INC_TAU_THR = 6 #s
INITCOUNT = 5
LARGEDZ = 22.5*0.3048 #m
LATELEVEL = 4.5 #s
LATESLACK = 0.5 #s
LEVOFFACCX2 = 8.0*0.3048 #m/s^2
LO1 = 0.0
LO2 = 0.667
LO3 = 0.8
LONGCOAST = 3.5 #s
LOSCORE = 100
LOWFIRMRZ = 150*0.3048 #m
MAXALTDIFF = 600*0.3048 #m
MAXALTDIFF2 = 850*0.3048 #m
MAXBINS = 8
MAXDRATE = (4400*0.3048)/60 #m/s
MAXSOFT = 5
MAXZDINT = (10000*0.3048)/60 #m/s
MAXZDTIME = 17.0 #s
MEDHISCORE = 500
MEDLOSCORE = 300
MEDSCORE = 400
MINBINS = 3
MINDRATE = (-4400*0.3048)/60 #m/s
MINFIRM = 2
MINRITIME = 4.0 #s
MINRVSTIME = 10.0 #s
MINTATIME = 8 #s
MINTAU = 0 #s
MODEL_T = 9 #s
MODEL_ZD = (2500*0.3048)/60 #m/s
NAFRANGE = 1.7 #nmi
NBINSNL = 5
NEWVSL = 75*0.3048 #m
NODESHI = 1200*0.3048 #m
NODESLO = 1000*0.3048 #m
NOWEAK = 10 #s
NOZCROSS = 100*0.3048 #m
NSGNCT = 0.1
OLEV = (600*0.3048)/60 #m/s
OUT2 = 1.1 #s
OUT3 = 0.55 #s
OVERDUE = 3.5 #s
P_ACCTHR = 1.5*0.3048 #m/s^2
P_ALPHA3D = 0.1
P_ALPHARESSQ = 0.1
P_INITRHODDTHR = 9999
P_MAXRANGERESID = 150*0.3048 #m
P_MAXSIGDPX = 3
P_MINSIGDPX = 0.7
P_P_NOISE_FACTOR = 100.0
P_PROCNOIVAR = 2.56*0.3048*0.3048 #(m/s^2)^2
P_RESDL_SIGMAS = -3
P_RESSD_C_EXP_FACT = 1.2
P_RESSD_N = 35*0.3048 #m
P_VAR_BRNG = 7.569e-3
PROXA = 1200*0.3048 #m
PROXR = 6.0 #nmi
Q100 = 100*0.3048 #m
Q25 = 25*0.3048 #m
Q50 = 50*0.3048 #m
QUIKREAC = 2.5 #s
RACCEL = 11.2*0.3048 #m/s^2
RADARLOST = 10
RDTHR = 10*0.3048 #m/s
RDTHRTA = 10*0.3048 #m/s
RESIDECAY = 0.5
RESIDIMIN = 0.8
RMAX = 12.0*1852 #m
RRD_THR = 10
SLACKEN1 = 3.5 #s
SLACKEN2 = 6.5 #s
SLITEOFF = 1.35 #s
SMALLZD = 5.0*0.3048 #m/s
STIMOUT = 240 #s
STROFIR = 20 #s
TARHYST = 0.20*1852 #m
TBINHI = 1.1 #s
TBINLO = 0.9 #s
TBINMIN = 2.0 #s
TCATRES = 6 #s
TGOLEV = 20.5 #s
TIETHR = 3 #s
TINITZD = 5.5 #s
TINYSCORE = 40
TINYZD = 2.5*0.3048 #m/s
TTLORATE = (1000*0.3048)/60 #m/s
TTLOSEP = 800*0.3048 #m
TTLOZD = (600*0.3048)/60 #m/s
TMIN = 4.5 #s
TRVSNOWEAK = 5 #s
TRYMAX = 6 #Between 6 and 12 (manufacturer specific)
TTRENDMIN = 2.5 #s
TV1 = 5 #s
V0 = 0 #m/s
V1000 = (1000*0.3048)/60 #m/s
V2000 = (2000*0.3048)/60 #m/s
V500 = (500*0.3048)/60 #m/s
VACCEL = 8*0.3048 #m/s^2
VELOCITY_THRESHOLD = -10*0.3048 #m/s
ZDABTHR = 7.0*0.3048 #m/s
ZDDABTHR = 2.0*0.3048 #m/s^2
ZDDECAY = 0.9
ZDESBOT = 900*0.3048 #m
ZDFRACC = 1.3
ZDLARGE = 12000*0.3048/60 #m/s
ZDLIKELY = 3000*0.3048/60 #m/s
ZDTHR = -1*0.3048 #m/s
ZDTHRTA = -1*0.3048 #m/s
ZLARGE = 100000*0.3048 #m
ZLIMITL = 50*0.3048 #m
ZLIMITU = 60*0.3048 #m
ZNO_AURALHI = 600*0.3048 #m
ZNO_AURALLO = 400*0.3048 #m
ZNOINCDESHI = 1650*0.3048 #m
ZNOINCDESLO = 1450*0.3048 #m
ZRJIT = 0.24
ZSL2TO3 = 1100*0.3048 #m
ZSL3TO2 = 900*0.3048 #m
ZSL3TO4 = 2550*0.3048 #m
ZSL4TO3 = 2150*0.3048 #m
ZSL4TO5 = 5500*0.3048 #m
ZSL5TO4 = 4500*0.3048 #m
ZSL5TO6 = 10500*0.3048 #m
ZSL6TO5 = 9500*0.3048 #m
ZSL6TO7 = 20500*0.3048 #m
ZSL7TO6 = 19500*0.3048 #m

"""Table constant"""
VMAPINTENT = np.array([0,1,2,0]) # 0=none 1=DON'T DESCEND 2=DON'T CLIMB
HMAPINTENT = np.array([0,3,4,0]) # 0=none 3=DON'T TURN LEFT 4=DON'T TURN RIGHT
PTABLEV = np.array([0,14,7,9,11,5,12,2,13,3,10,4,6,8,1,15]) #PARITY CODES FOR COMBINED 4-BIT VRC & CVC FIELDS
PTABLEH = np.array([0,11,19,24,28,23,15,4,13,6,30,21,17,26,2,9,21,30,6,13,9,2,26,17,24,19,11,0,4,15,23,28,25,18,10,1,5,14,22,29,20,31,7,12,8,3,27,16,12,7,31,20,16,27,3,8,1,10,18,25,29,22,14,5]) #PARITY CODES FOR COMBINED 6-BIT HRC AND CHC FIELDS
BOT = np.array([None,-6000*0.3048,2150*0.3048,4500*0.3048,9500*0.3048,19500*0.3048,41500*0.3048]) #m index=g.layer
TOP = np.array([None,2550*0.3048,5500*0.3048,10500*0.3048,20500*0.3048,42500*0.3048,600000*0.3048]) #m index=g.layer
AL = np.array([None,300*0.3048,300*0.3048,350*0.3048,400*0.3048,600*0.3048,700*0.3048]) #m index=g.layer
SF = np.array([None,200*0.3048,200*0.3048,200*0.3048,240*0.3048,400*0.3048,480*0.3048]) #m index=g.layer
ZT = np.array([None,600*0.3048,600*0.3048,600*0.3048,600*0.3048,700*0.3048,800*0.3048]) #m index=g.layer
ZT_TA = np.array([None,850*0.3048,850*0.3048,850*0.3048,850*0.3048,850*0.3048,1200*0.3048]) #m index=g.layer
LEV_REV = np.array([None,200*0.3048,200*0.3048,300*0.3048,350*0.3048,400*0.3048,470*0.3048]) #m index=g.layer
MAC_INC = np.array([None,200*0.3048,200*0.3048,250*0.3048,300*0.3048,350*0.3048,400*0.3048]) #m index=g.layer
MAC_HIST1 = np.array([None,50*0.3048,50*0.3048,75*0.3048,75*0.3048,100*0.3048,100*0.3048]) #m index=g.layer
MAC_HIST2 = np.array([None,65*0.3048,65*0.3048,100*0.3048,100*0.3048,150*0.3048,150*0.3048]) #m index=g.layer
ALPHAZ = np.array([0.6,0.5,0.4]) #index=k
BETAZ = np.array([0.257,0.167,0.1]) #index=k
BNDZD = np.array([15*0.3048,10*0.3048,7*0.3048,5*0.3048]) #ft/s index=casfirm
BNDAC = np.array([11*0.3048,9*0.3048,7*0.3048,5*0.3048]) #ft/s index=casfirm
ALPHAL = np.array([1.,1.,0.83,0.7,0.6,0.46,0.4,0.4,0.4])
BETAL = np.array([0.,1.,0.5,0.3,0.2,0.11,0.1,0.1,0.1])
GAMMAL = np.array([0.,0.,0.16,0.07,0.035,0.013,0.01,0.01,0.01])
ALPHAP = np.array([1.,1.,0.83,0.7,0.6,0.46,0.4,0.4,0.4])
BETAP = np.array([0.,1.,0.5,0.3,0.2,0.11,0.1,0.1,0.1])
GAMMAP = np.array([0.,0.,0.16,0.07,0.035,0.013,0.01,0.01,0.01])
ALPHARB = np.array([1.,1.,0.83,0.7,0.6,0.46,0.39,0.31,0.278])
BETARB = np.array([0.,1.,0.5,0.3,0.2,0.11,0.07,0.05,0.0453])
DMODTBL = np.array([None,None,None,0.2*1852,0.35*1852,0.55*1852,0.8*1852,1.1*1852]) #m index=itf.lev
H1TBL = np.array([None,None,None,0.002*1852*1852,0.00278*1852*1852,0.00278*1852*1852,0.00278*1852*1852,0.004*1852*1852]) #m^2/s index=itf.lev
TRTETBL = np.array([None,None,None,15,20,25,30,35]) #s index=itf.lev
TRTUTBL = np.array([None,None,None,15,20,25,30,35]) #s index=itf.lev
TVTETBL = np.array([None,None,None,15,20,25,30,35]) #s index=itf.lev
TVTUTBL = np.array([None,None,None,15,20,25,30,35]) #s index=itf.lev
TVPCTBL = np.array([None,None,None,35,40,40,45,48]) #s index=itf.lev
TVPETBL = np.array([None,None,None,25,30,30,35,40]) #s index=itf.lev
TVVTT_TBL = np.array([None,None,None,15,18,20,22,25]) #s index=itf.lev
TMIN_MDF = np.array([None,None,None,9999,4,4,4,4]) #index=sensitivity level
HMDTHR = np.array([[None],
                   [None],
                   [None],
                   [None,1215*0.3048,1215*0.3048,1215*0.3048,1215*0.3048,1215*0.3048,1215*0.3048,1215*0.3048,1215*0.3048,1215*0.3048,1215*0.3048,1215*0.3048,1215*0.3048,1215*0.3048,1215*0.3048,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                   [None,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,2126*0.3048,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                   [None,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,3342*0.3048,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                   [None,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,4861*0.3048,0,0,0,0,0,0,0,0,0,0,0],
                   [None,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,6683*0.3048,0,0,0,0,0,0,0]]) #m first index=sl second index=time to cpa s
AVEVTAU = np.array([None,None,None,13,18,20,24,26])
DMODTA_TBL = np.array([None,None,None,0.3*1852,0.33*1852,0.48*1852,0.75*1852,1.*1852,1.3*1852]) #m index=itf.lev
H1TA_TBL = np.array([None,None,None,0.004*1852*1852,0.004*1852*1852,0.005*1852*1852,0.006*1852*1852,0.006*1852*1852,0.006*1852*1852]) #m^2/s index=itf.lev
TRTHRTA_TBL = np.array([None,None,None,20,25,30,40,45,48]) #s index=itf.lev
TVTHRTA_TBL = np.array([None,None,None,20,25,30,40,45,48]) #s index=itf.lev
CLIMBGOAL = np.array([None,(-2000*0.3048)/60,(-1000*0.3048)/60,(-500*0.3048)/60,0,None,None,None,(1500*0.3048)/60]) #mps index=value of raind
DESGOAL = np.array([None,(2000*0.3048)/60,(1000*0.3048)/60,(500*0.3048)/60,0,None,None,None,(-1500*0.3048)/60]) #mps index=value of raind
