import copy

from tcasClass import *

class Rcv_var:
    def __init__(self):
        """Group general"""
        self.intind = None #Numeric value of complement to cancel
        self.success = None #Matching entry found

        """Group message"""
        self.chc = None #3-bit subfield to cancel horizontal complement
        self.cvc = None #2-bit subfield to cancel vertical complement
        self.hrc = None #3-bit subfield to add horizontal complement
        self.hsb = None #5-bit subfield for horiz.sense parity protection
        self.iis = None #Mode S interrogator identification subfield
        self.l2bchc = None #Local variable to hold low order 2 bits of CHC
        self.l2bhrc = None #Local variable to hold low order 2 bits of HRC
        self.mid = None #ICAO 24-bit aircraft address of interrogating TCAS aircraft
        self.mtb = None #Multi-threat bit
        self.slc = None #Uplinked Sensitivity Level Command from Mode S sensor
        self.vrc = None #2-bit subfield to add vertical complement
        self.vsb = None #4-bit subfield for vert. sense parity protection
        self.bad_data = None #Parity error or illegal data in message
        self.parityh = None #Value from P.PTABLEH based on bits in message
        self.parityv = None #Value from P.PTABLEV based on bits in message


class TcasReceiver:
    def __init__(self):
        self.TF = None
        self.g = None
        self.p = None
        self.realtime = None

    """VALID2"""
    def find_threat_file_entry(self, TF, realtime, p, rcv_var):
        rcv_var.success = False
        tf = None
        for tf_c in TF:
            if(rcv_var.success != False):
                break
            if(tf_c.id == rcv_var.mid):
                rcv_var.success = True
                tf = tf_c
        if(rcv_var.success == False):
            tf = Tf()
            tf.iptr = None
            tf.id = rcv_var.mid
            tf.t_intent = realtime.tclock
            tf.tthlrcm = p.tinit
            tf.new = False
            tf.poowrar, tf.pothrar[0], tf.pothrar[1] = 0, 0, 0
            for i in range(len(tf.permtent)):
                tf.permtent[i] = False
            TF.append(tf)
        return tf
    """VALID2"""


    """VALID"""
    def delete_intent(self, intind, TF, g, rcv_var):
        if(intind != 0):
            rcv_var.success = False
            for tf in TF:
                if(rcv_var.success != False):
                    break
                if(intind == tf.pothrar[0] or intind == tf.pothrar[1]):
                    rcv_var.success = True
            if(rcv_var.success == True):
                pass
            else:
                g.intent[intind] = False
    """VALID"""


    """VALID"""
    def process_valid_data(self, tf, TF, g, p, rcv_var):
        if(rcv_var.cvc != 0 and p.vmapintent[rcv_var.cvc] == tf.pothrar[0]):
            tf.pothrar[0] = 0
            self.delete_intent(p.vmapintent[rcv_var.cvc], TF, g, rcv_var)
        if(rcv_var.l2bchc != 0 and p.hmapintent[rcv_var.l2bchc] == tf.pothrar[1]):
            tf.pothrar[1] = 0
            self.delete_intent(p.hmapintent[rcv_var.l2bchc], TF, g, rcv_var)
        if(rcv_var.vrc != 0):
            if(tf.pothrar[0] != p.vmapintent[rcv_var.vrc]):
                tf.pothrar[0] = p.vmapintent[rcv_var.vrc]
                g.intent[p.vmapintent[rcv_var.vrc]] = True
        if(rcv_var.l2bhrc != 0):
            if(tf.pothrar[1] != p.hmapintent[rcv_var.l2bhrc]):
                tf.pothrar[1] = p.hmapintent[rcv_var.l2bhrc]
                g.intent[p.hmapintent[rcv_var.l2bhrc]] = True
    """VALID"""


    """OK"""
    def process_threat_intent(self, TF, realtime, g, p, rcv_var):
        rcv_var.bad_data = False
        rcv_var.parityv = p.ptablev[int(bin(rcv_var.cvc)[2:]+bin(rcv_var.vrc)[2:], 2)]
        rcv_var.parityh = p.ptableh[int(bin(rcv_var.chc)[2:]+bin(rcv_var.hrc)[2:], 2)]
        rcv_var.l2bchc = int("0"*(len(bin(rcv_var.chc)[2:]) + 1) + bin(rcv_var.chc)[2:], 2)
        rcv_var.l2bhrc = int("0"*(len(bin(rcv_var.hrc)[2:]) + 1) + bin(rcv_var.hrc)[2:], 2)
        if(rcv_var.parityv != rcv_var.vsb):
            rcv_var.bad_data = True
        elif((rcv_var.cvc == 0) and (rcv_var.chc == 0) and (rcv_var.vrc == 0) and (rcv_var.hrc == 0)):
            rcv_var.bad_data = True
        elif((rcv_var.cvc == 3) or (rcv_var.vrc == 3) or ((rcv_var.cvc != 0) and (rcv_var.cvc == rcv_var.vrc)) or (rcv_var.l2bchc == 3) or (rcv_var.l2bhrc == 3)):
            rcv_var.bad_data = True
        if(rcv_var.bad_data == False):
            tf = self.find_threat_file_entry(TF, realtime, p, rcv_var)
            tf.tthlrcm = realtime.tclock
            self.process_valid_data(tf, TF, g, p, rcv_var)
    """OK"""


    """OK"""
    def resolution_message_processing(self, TF, g, p, realtime, rcv_var):
        if(g.colock == False):
            g.colock = True
            g.tlock = realtime.tclock
            self.process_threat_intent(TF, realtime, g, p, rcv_var)
            g.colock = False
    """OK"""


    """OK"""
    def receive(self, intent_to_threat):
        rcv_var = Rcv_var()
        rcv_var.chc = intent_to_threat.chc
        rcv_var.cvc = intent_to_threat.cvc
        rcv_var.hrc = intent_to_threat.hrc
        rcv_var.hsb = intent_to_threat.hsb
        rcv_var.mid = intent_to_threat.mid
        rcv_var.mtb = intent_to_threat.mtb
        rcv_var.vrc = intent_to_threat.vrc
        rcv_var.vsb = intent_to_threat.vsb
        self.resolution_message_processing(self.TF, self.g, self.p, self.realtime, rcv_var)
    """OK"""