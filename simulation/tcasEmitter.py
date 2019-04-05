import time

from tcasClass import *

class Snd_var:
    def __init__(self):
        """Group coordination"""
        self.complement = None #Numeric value of complement of intent
        self.success = None #Flag indicating success of action (msg. transfer,etc)
        self.try_ = None #Number of failed coordination attempts


class TcasEmitter:
    def __init__(self):
        #Dictionary of TCAS receiver in range
        self.tcasReceiverInRange = {}


    """VALID"""
    def send_initial_intent(self, wl, g, realtime, p,intent_to_threat, snd_var):
        itf = wl.iptr
        if(itf.eqp == TCAS):
            time_lock_begin = time.time()
            while (g.colock == True):
                if ((time.time() - time_lock_begin) > p.tunlock):
                    assert ()
                time.sleep(0.01)
            g.colock = True
            g.tlock = realtime.tclock
            intent_to_threat.chc, intent_to_threat.hrc = 0, 0
            intent_to_threat.hsb = 0
            intent_to_threat.mtb = g.macflg
            if(wl.status == TERM):
                if(itf.permtent_copy[6] == True):
                    snd_var.complement = 1
                else:
                    snd_var.complement = 2
            else:
                if(itf.tptr.permtent[6] == True):
                    snd_var.complement = 1
                else:
                    snd_var.complement = 2
            if(wl.status == TERM):
                intent_to_threat.cvc = snd_var.complement
                intent_to_threat.vrc = 0
            else:
                intent_to_threat.vrc = snd_var.complement
                intent_to_threat.cvc = 0
                if(itf.tiebreaker_reversal == True or itf.rev_geom == True):
                    if(itf.tptr.permtent[6] == True):
                        snd_var.complement = 2
                    else:
                        snd_var.complement = 1
                    intent_to_threat.cvc = snd_var.complement
            intent_to_threat.vsb = p.ptablev[int(bin(intent_to_threat.cvc)[2:]+bin(intent_to_threat.vrc)[2:], 2)]
            intent_to_threat.mid = g.idown
            self.tcasReceiverInRange[itf.idint].receive(intent_to_threat)
            g.colock = False
    """VALID"""