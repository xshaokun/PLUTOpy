import numpy as np
import astropy.units as u

from ..pluto_fluid_info import PlutoFluidInfo


class Field(object):
  ''' Contain the information of fields '''

  __slots__ = [
    'snapshot',
    'primal_fields',
    'derived_fields',
    'cache_list',
    '_cache'
  ]

  def __init__(self, snapshot, data):
    self.snapshot = snapshot
    self.primal_fields = snapshot.field_list
    self.derived_fields = snapshot.derived_fields
    self._cache = {}
    for name in self.primal_fields:
      self._cache[name] = getattr(data, name).T
    self.cache_list = self.primal_fields

  def __getitem__(self, name):
    if name in self.cache_list:
      return self._cache[name]
    elif name in self.derived_fields:
      f = PlutoFluidInfo.known_fields[name][1]
      self.cache_list.append(name)
      self._cache[name] = f(self.snapshot)
      return self._cache[name]
    else:
      raise KeyError(f'The field {name} cannot be found in PlutoFluidInfo. Check the name or add by yourself.')

  def remove(self, name):
    del self._cache[name]
    self.cache_list.remove(name)

  def info(self, name):
    PlutoFluidInfo.info(name)

  def update_derived_fields(self):
    pluto_fields = PlutoFluidInfo.known_fields
    derived_cache_list = list(set(self.cache_list) - set(self.primal_fields))
    for key in derived_cache_list:
      f = PlutoFluidInfo.known_fields[key][1]
      self._cache[key] = f(self.snapshot).to(u.Unit(pluto_fields[key][3]))

  @staticmethod
  def _from_sph(theta, phi, v_r, v_th, v_phi):
    ''' from vectors in spherical coordinate to those in cartesian coordinate '''
    v_x = v_r * np.sin(theta) * np.cos(phi) + v_th * np.cos(theta) * np.cos(phi) - v_phi * np.sin(phi)
    v_y = v_r * np.sin(theta) * np.sin(phi) + v_th * np.cos(theta) * np.sin(phi) + v_phi * np.cos(phi)
    v_z = v_r * np.cos(theta) - v_th * np.sin(theta)
    return v_x, v_y, v_z

  @staticmethod
  def _from_cyl(phi, v_r, v_phi, v_z):
    ''' from vectors in cylindrical coordinate to those in cartesian coordinate '''
    v_x = v_r * np.cos(phi) - v_phi * np.sin(phi)
    v_y = v_r * np.sin(phi) + v_phi * np.cos(phi)
    return v_x, v_y, v_z

  def to_cart(self, field):
    ''' convert to cartesian coordinate system

    Args:
      field (str): 'grid' or 'velocity'

    Returns:
      tuple: the resulted three components
    '''

    v1 = getattr(self, field+'1')
    v2 = getattr(self, field+'2')
    v3 = getattr(self, field+'3')
    if self.snapshot.geometry == 'SPHERICAL':
      theta = self.snapshot.grid['x2']
      phi = self.snapshot.grid['x3']
      v1, v2, v3 = self._from_sph(theta, phi, v1, v2, v3)
    elif self.snapshot.geometry == 'POLAR':
      phi = self.snapshot.grid['x2']
      v1, v2, v3 = self._from_cyl(phi, v1, v2, v3)
    else:
      raise KeyError('Only support geometry of [SPHERICAL] and [POLAR].')

    return v1, v2, v3


  def in_code_unit(self):
    ''' Assign code units '''

    code_length = self.snapshot.code_unit['code_length']
    code_density = self.snapshot.code_unit['code_density']
    code_velocity = self.snapshot.code_unit['code_velocity']
    pluto_fields = PlutoFluidInfo.known_fields
    if self.snapshot.with_units:
      for key in self.primal_fields:
        self._cache[key] = self._cache[key].to(eval(pluto_fields[key][2]))
    else:
      for key in self.primal_fields:
        self._cache[key] *= eval(pluto_fields[key][2])

    self.update_derived_fields()


  def in_astro_unit(self):
    ''' convert the units to those commonly used in astro '''

    pluto_fields = PlutoFluidInfo.known_fields

    for key in self.primal_fields:
      self._cache[key] = self._cache[key].to(pluto_fields[key][3])

    self.update_derived_fields()
