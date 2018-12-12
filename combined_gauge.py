import PyTango,time

class CombinedGauge(object):
  def __init__(self,serial='bl/c/serial-30'):
    self.SERIAL = self.get_serial(serial)

  def get_serial(self,serial='bl/c/serial-30',dp=None):
    """ Note, we've had to set Serial conf to 9600,None,1StopBit"""
    if not dp: dp=PyTango.DeviceProxy(serial)
    return dp

  def read_param(self,param,arg='',dp=None):
    if dp is None: dp = self.SERIAL
    comm = '@253%s;FF'%(param+arg)

    #Using DevSerWriteChar instead of DevSerWriteString to avoid memory leaks in PyTango8
    dp.command_inout("DevSerWriteChar",map(ord,comm))
    #dp.command_inout("DevSerWriteString",comm)
    #dp.command_inout("DevSerWriteChar",[13])    
    
    time.sleep(.1)
    #result = dp.DevSerReadRaw()
    result = dp.command_inout("DevSerReadString",0)
    print result
    return result

  def read_pressure(self,channel=3):
    return self.read_param('PR%d?'%channel)

  def check_unit(self,unit=''):
    if unit: return self.read_param('U!',unit)
    else: return self.read_param('U?')

  def check_setpoint(self,n=1,setpoint=0,direction='',enable=None):
    """ Actually in BL22 the BELOW direction is used for having the proper logic. """
    if setpoint: result = self.read_param('SP%d!'%1,str(setpoint))
    else: result = self.read_param('SP%d?'%n)
    if direction: 
      if direction in 'ABOVE,BELOW'.split(','): self.read_param('SD%d!'%1,str(direction))
      else: raise Exception( 'DIRECTION MUST BE IN "ABOVE/BELOW"')
    else: print self.read_param('SD%d?'%n)
    if enable is not None: self.read_param('EN%d!'%1,('CMB' if enable else 'OFF'))
    else: 
        enable = self.read_param('EN%d?'%n) 
        if 'OFF' in enable and not setpoint: return '0'
    return result

  def check_calibration(self,calibration=''):
    valids=[s.strip() for s in 'NITROGEN, AIR, ARGON, HELIUM, HYDROGEN, H2O, NEON, CO2, XENON'.split(',')]
    if not calibration: return self.read_param('GT?')
    elif calibration not in valids:
      raise Exception('CALIBRATION must be in %s'%valids)
    else: return self.read_param('GT!',calibration)
