import numpy as np
import astropy.units as u

class Grid(object):
  ''' Contain the information of grids '''

  __slots__ = [
    'snapshot',
    'h1', 'h2', 'h3',
    'x1', 'x2', 'x3',
    'x1r', 'x2r', 'x3r',
    'dx1', 'dx2', 'dx3',
    'dA1', 'dA2', 'dA3',
    'dV',
    'code_unit',
    'astro_unit'
  ]


  def __init__(self, snapshot):
    self.snapshot = snapshot
    self.x1, self.x2, self.x3 = np.meshgrid(snapshot.coord['x1'], snapshot.coord['x2'], snapshot.coord['x3'])
    self.dx1, self.dx2, self.dx3 = np.meshgrid(snapshot.coord['dx1'], snapshot.coord['dx2'], snapshot.coord['dx3'])
    self.x1r, self.x2r, self.x3r = np.meshgrid(snapshot.coord['x1r'], snapshot.coord['x2r'], snapshot.coord['x3r'])
    
    self.update_surf_vol()

    if snapshot.ndim !=3:
      for key in self.__slots__[4:13]:
        tmp = getattr(self, key)
        setattr(self, key, tmp.squeeze())

    code_length = u.def_unit('unit_length', represents=snapshot.code_unit['code_length'])
    if snapshot.geometry == 'CARTESIAN':
      self.code_unit = [code_length, code_length, code_length]
      self.astro_unit = [u.kpc, u.kpc, u.kpc]
    elif snapshot.geometry == 'POLAR':
      self.code_unit = [code_length, u.rad, code_length]
      self.astro_unit = [u.kpc, u.rad, u.kpc]
    elif snapshot.geometry == 'SPHERICAL':
      self.code_unit = [code_length, u.rad, u.rad]
      self.astro_unit = [u.kpc, u.rad, u.rad]


  def update_surf_vol(self):
    if self.snapshot.geometry == 'CARTESIAN':
      self.h1, self.h2, self.h3 = (1, 1, 1)
    elif self.snapshot.geometry == 'POLAR':
      self.h1, self.h2, self.h3 = (1, self.x1, 1)
    elif self.snapshot.geometry == 'SPHERICAL':
      self.h1, self.h2, self.h3 = (1, self.x1, self.x1*np.sin(self.x2))

    self.dA1 = self.h2 * self.h3 * self.dx2 * self.dx3
    self.dA2 = self.h1 * self.h3 * self.dx1 * self.dx3
    self.dA3 = self.h1 * self.h2 * self.dx1 * self.dx2
    self.dV = self.h1 * self.h2 * self.h3 * self.dx1 * self.dx2 * self.dx3


  @staticmethod
  def _from_sph(r, theta, phi):
    ''' from spherical coordinate to cartesian coordinate '''
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.cos(phi)
    z = r * np.cos(theta)
    return x, y, z


  @staticmethod
  def _from_cyl(r, phi, z):
    ''' from cylindrical coordinate to cartesian coordinate '''
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return x, y, z


  def to_cart(self):
    if self.snapshot.geometry == 'SPHERICAL':
      self.x1, self.x2, self.x3 = self._from_sph(self.x1, self.x2, self.x3)
    elif self.snapshot.geometry == 'POLAR':
      self.x1, self.x2, self.x3 = self._from_cyl(self.x1, self.x2, self.x3)
    else:
      raise KeyError('Only support geometry of [SPHERICAL] and [POLAR].')


  def in_code_unit(self):
    ''' Assign code units '''

    if self.snapshot.is_quantity:
      for key in self.__slots__[4:13]:
        if 'x1' in key:
          tmp = getattr(self, key).to(self.code_unit[0])
        elif 'x2' in key:
          tmp = getattr(self, key).to(self.code_unit[1])
        elif 'x3' in key:
          tmp = getattr(self, key).to(self.code_unit[2])
        
        setattr(self, key, tmp)
    else:
      for key in self.__slots__[4:13]:
        if 'x1' in key:
          tmp = getattr(self, key) * self.code_unit[0]
        elif 'x2' in key:  
          tmp = getattr(self, key) * self.code_unit[1]
        elif 'x3' in key:  
          tmp = getattr(self, key) * self.code_unit[2]
        
        setattr(self, key, tmp)

    self.update_surf_vol()


  def in_astro_unit(self):
    ''' convert the units to those commonly used in astro '''

    if not self.snapshot.is_quantity:
      self.in_code_unit()

    for key in self.__slots__[4:13]:
      if 'x1' in key:
        tmp = getattr(self, key).to(self.astro_unit[0])
      elif 'x2' in key:
        tmp = getattr(self, key).to(self.astro_unit[1])
      elif 'x3' in key:
        tmp = getattr(self, key).to(self.astro_unit[2])

    self.update_surf_vol()