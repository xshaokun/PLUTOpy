import os
import pandas as pd
import astropy.units as u
import pyPLUTO.pload as pp

from ..pluto_def_constants import PlutoDefConstants
from ..pluto_fluid_info import PlutoFluidInfo
from ..utilities.tools import nearest 
from .grid import Grid
from .field import Field


class Dataset(object):
  ''' Pluto data work directory

  Args:
    w_dir (str): path to the directory where data files locate. Default is './'.
    datatype (str): type of data files. Default is 'vtk'.
    init_file (str): init file including the parameters for simulation. Default is 'pluto.ini'.

  Attributes:
    wdir (str): absolute path to the dirctory.
    init_file (str):
    datatype (str):
    filetype (str):
    endianess (str):
    geometry (str):
    ndim (int):
    code_unit (dict):
    field_list (list):
    derived_fields (list):

  Methods:
    info():
  '''

  __slots__=[
    'wdir',
    'init_file',
    'datatype',
    'filetype',
    'endianess',
    'geometry',
    'ndim',
    'code_unit',
    'field_list',
    'derived_fields',
    '__log_file',
    '__ds'
  ]

  def __init__(self, w_dir='./', datatype='vtk', init_file='pluto.ini'):
    self.wdir = os.path.abspath(w_dir) + '/'
    self.init_file = init_file
    self.datatype = datatype

    varfile = self.wdir+self.datatype+'.out'
    with open(varfile,'r') as vfp:
      varinfo = vfp.read().splitlines()
      lastline = varinfo[-1].split()
      self.filetype = lastline[4]
      self.endianess = lastline[5]
      self.field_list = lastline[6:]
      self.derived_fields = []
      self.geometry = 'CARTESIAN'

    for k, v in PlutoFluidInfo.known_fields.items():
      if v[0] is not None:
        self.derived_fields.append(k)

    # Three base units and default values in pluto code
    self.code_unit={
      'code_density' : 1.0 * u.g/u.cm**3,
      'code_length'  : 1.0 * u.cm,
      'code_velocity': 1.0 * u.cm/u.s
    }

    if 'definitions.h' in os.listdir(self.wdir):
      with open(self.wdir+'definitions.h','r') as df:
        for line in df.readlines():
          if line.startswith('#define  GEOMETRY'):
            self.geometry = line.split()[-1]
          if line.startswith('#define  DIMENSION'):
            self.ndim = int(line.split()[-1])
          if line.startswith('#define  UNIT'):
            name = line.split()[1]
            expr = line.split()[-1]
            var = name.split('_')[-1]
            key = 'code_'+var.lower()
            if 'CONST' in expr:
              expr = expr.replace('CONST', 'PlutoDefConstants().CONST')
            self.code_unit[key] = eval(expr) * self.code_unit[key].unit
    else:
      print('Could not open definitions.h! \
        The values of attributes [geometry, code_units] did not update,\
        you can specifiy them later, \
        and assign units by in_code_unit() manually.')


  def __getitem__(self, index):
    # index: int or time
    ns = self._number_step(index)
    ds = Snapshot(ns, w_dir=self.wdir, datatype=self.datatype, init_file=self.init_file)
    return ds


  def info(self):
    for attr in self.__slots__:
      if hasattr(self, attr):
        print(f'{attr:15}:  {getattr(self, attr)}')


  def _number_step(self, ns):
    ''' find number step of data file

    Args:
      ns (int/float): should be a integer in default, \
          but if it is a negative integer, return the last number step or if it is a float, \
          it is assumed to be time, and return the nearst number step
    '''

    hdr = ['time','dt','Nstep']
    log_file = pd.read_table(self.wdir+self.datatype+'.out',sep=' ', usecols=[1,2,3], names=hdr)

    if type(ns) is int:
      if ns < 0:
        return log_file.index[-1]
      else:
        return ns
    elif type(ns) is float:     #  given a specific [time], find [ns] corresponding nearst existed data [time].
      return nearest(log_file['time'],ns)
    else:
      raise TypeError(f'ns({ns}) should be int or float, now it is {type(ns)}.')


class Snapshot(Dataset):
  ''' Pluto output snapshot data structure

  Args:
    ns (int/float): the index of snapshot. It should be a integer in default, \
        but if it is a negative integer, return the last snapshot. \
        Or if it is a float, it is assumed to be the time, and return the nearst snapshot
    Other arguements refer to Dataset() class

  Attributes:
    Include all attributes of Dataset() class, besides:
    nstep: (int)
    time: (int/units.Quantity)
    dt: (float)
    is_quantity: (bool)
    index: (dict)
    coord: (dict)
    grids: (dict)
    fields: (dict)

  Methods:
    info() :
    in_code_unit():
    in_astro_unit():
    slice2d(field, x1=None, x2=None, x3=None):
    slice1d(field, x1=None, x2=None, x3=None):
    to_cart(field):
  '''

  __slots__= Dataset.__slots__ + [
    'nstep',
    'time',
    'dt',
    'is_quantity',
    'index',
    'coord',
    'grids',
    'fields'
  ]

  def __init__(self, ns, w_dir, datatype,init_file):
    super().__init__(w_dir, datatype, init_file)

    ds = pp.pload(ns, w_dir=self.wdir, datatype=self.datatype)
    self.nstep = ds.NStep
    self.time = ds.SimTime
    self.dt = ds.Dt
    self.is_quantity = False

    # initialize Snapshot.index
    grids_info = [
      'n1','n2','n3',         # number of computational cells
      'n1_tot','n2_tot','n3_tot',   # total cells including ghost cells
    ]
    self.index = {}
    for key in grids_info:
      self.index[key] = getattr(ds, key)

    # initialize Snapshot.coord
    coord_info = [
      'x1','x2','x3',   # cell center coordinate
      'dx1','dx2','dx3',  # cell width
      'x1r','x2r','x3r'  # cell edge coordinate
    ]
    self.coord = {}
    for key in coord_info:
      self.coord[key] = getattr(ds, key)

    # initialize Snapshot.grids
    self.grids = Grid(self)

    # initialize Snapshot.field
    self.fields = Field(self, ds)


  def info(self):
    for attr in self.__slots__:
      if hasattr(self, attr):
        value = getattr(self, attr)
        if not type(value) is dict:
          print(f'{attr:15}:  {value}')


  def in_code_unit(self):
    ''' Assign code units '''

    code_length = u.def_unit('unit_length', represents=self.code_unit['code_length'])
    code_density = u.def_unit('unit_density', represents=self.code_unit['code_density'])
    code_velocity = u.def_unit('unit_velocity', represents=self.code_unit['code_velocity'])
    u.add_enabled_units(code_length, code_density, code_velocity)

    self.grids.in_code_unit()
    self.fields.in_code_unit()

    if self.is_quantity:  # in case units are already assigned
      self.time = self.time.to(code_length/code_velocity)
      self.dt = self.dt.to(code_length/code_velocity)
    else:
      self.time *= code_length/code_velocity
      self.dt *= code_length/code_velocity

    self.is_quantity = True


  def in_astro_unit(self):
    ''' convert the units to those commonly used in astro '''

    if not self.is_quantity:  # in case not quantity, assign code_unit first
      self.in_code_unit()

    self.grids.in_astro_unit()
    self.fields.in_astro_unit()
    self.time = self.time.to(u.yr)
    self.dt = self.dt.to(u.yr)


  def slice2d(self, field, x1=None, x2=None, x3=None):
    ''' Slice 3-D array and return 2-D array

    coordinate of one dimension should be specified

    Args:
      field (str): output variable name listed in attribute `field_list`
      x1 (float): rough coordinate (optional)
      x2 (float): rough coordinate (optional)
      x3 (float): rough coordinate (optional)

    Returns:
      arr (numpy.ndarray): in 2-D
    '''

    offset = [x1,x2,x3]
    i = 0
    for coord in offset:
      if coord is not None:  # find the direction
        dim = 'x'+str(i+1)
        if self.is_quantity:
          x = self.coord[dim].value
        else:
          x = self.coord[dim]
        offset[i] = nearest(x, coord)  # convert coord to index
        break
      i+=1
    index = str(offset).replace('None',':')
    arr = eval('self.fields[field]' + index)
    return arr


  def slice1d(self, field, x1=None, x2=None, x3=None):
    ''' Slice 3-D array and return 1-D array

    coordinates of two dimensions should be specified

    Args:
      field (str): output variable name listed in attribute `field_list`
      x1 (float): rough coordinate (optional)
      x2 (float): rough coordinate (optional)
      x3 (float): rough coordinate (optional)

    Returns:
      arr (numpy.ndarray): in 1-D
    '''

    if self.ndim == 3:
      offset = [x1,x2,x3]
    else:
      offset = [x1,x2]

    i = 0
    for coord in offset:
      dim = 'x'+str(i+1)
      if self.is_quantity:
        x = self.coord[dim].value
      else:
        x = self.coord[dim]

      if coord is not None:
        offset[i] = nearest(x, coord)
      else:
        offset[i] = None
      i+=1
    index = str(offset[::-1]).replace('None',':')
    arr = eval('self.fields[field]'+index)
    return arr