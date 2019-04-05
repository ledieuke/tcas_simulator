import time
import math as m

"""VALID"""
def threat_file_housekeeping(TF, realtime, p, DIL):
    for tf in TF:
        if(tf.poowrar == 0 and tf.pothrar[0] == 0 and tf.pothrar[1] == 0):
            if(tf.iptr != None):
                tf.iptr.tptr = None
            TF.remove(tf)
            tf = None
    for tf in TF:
        if(tf.tthlrcm >= 0):
            if((realtime.tclock - tf.tthlrcm) > p.tcatres):
                DIL.append(tf.pothrar[0])
                DIL.append(tf.pothrar[1])
                if(tf.poowrar == 0):
                    if(tf.iptr != None):
                        tf.iptr.tptr = None
                    TF.remove(tf)
                    tf = None
                else:
                    tf.pothrar[0], tf.pothrar[1] = 0, 0
                    tf.tthlrcm = p.tinit
"""VALID"""


"""VALID"""
def delete_intent(intind, TF, g):
    if(m.fabs(intind) > 1e-10):
        success = False
        for tf in TF:
            if(success != False):
                break
            if(m.fabs(intind - tf.pothrar[0]) < 1e-10 or m.fabs(intind - tf.pothrar[1]) < 1e-10):
                success = True
        if(success == True):
            pass
        else:
            g.intent[intind-1] = False
"""VALID"""


"""VALID"""
def resolution_advisory_housekeeping(TF, g, DIL):
    for dil in DIL:
        delete_intent(dil, TF, g)
"""VALID"""


"""VALID"""
def sensitivity_level_housekeeping(g, realtime, p, resvar):
    resvar.sit = 0
    while(resvar.sit <= p.sitmax):
        if(realtime.tclock - g.leveltim[resvar.sit] > p.stimout):
            g.leveltim[resvar.sit], g.levelsit[resvar.sit] = 0, 0
        resvar.sit += 1
"""VALID"""


"""VALID"""
def housekeeping(TF, g, realtime, p, DIL, resvar):
    time_lock_begin = time.time()
    while (g.colock == True):
        if ((time.time() - time_lock_begin) > p.tunlock):
            assert ()
        time.sleep(0.01)
    g.colock = True
    g.tlock = realtime.tclock
    threat_file_housekeeping(TF, realtime, p, DIL)
    resolution_advisory_housekeeping(TF, g, DIL)
    sensitivity_level_housekeeping(g, realtime, p, resvar)
    DIL.clear()
    g.colock = False
"""VALID"""