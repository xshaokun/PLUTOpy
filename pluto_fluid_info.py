import numpy as np
import astropy.units as u


def setup(cls):
  cls.setup_derived_field()
  return cls

@setup
class PlutoFluidInfo(object):
  ''' Contain pre-defined fluid information in PLUTO '''

  known_fields = {
# variables output by simulation
# Variable name :(type, function, code_unit,             astro_unit,   [alias]      )
# -----------------------------------------------------------------------------------
    'rho'       :('scalar', None, 'code_density',          'g/cm**3'  , ['density'   ]),
    'vx1'       :('vector', None, 'code_velocity',           'km/s'   , ['velocity-1'  ]),
    'vx2'       :('vector', None, 'code_velocity',           'km/s'   , ['velocity-2'  ]),
    'vx3'       :('vector', None, 'code_velocity',           'km/s'   , ['velocity-3'  ]),
    'prs'       :('scalar', None, 'code_density*code_velocity**2',   'erg/cm**3',  ['pressure'  ]),
    'tr1'       :('scalar', None, '',    '', ['tracer-1']),
    'tr2'       :('scalar', None, '',    '', ['tracer-2']),
    'tr3'       :('scalar', None, '',    '', ['tracer-3']),
    'tmp'       :('scalar', None, 'K',   'K',  ['temperature'  ]),
    'phi'       :('scalar', None, 'code_velocity**2',   'km**2/s**2',  ['potential'  ]),
  }

  @classmethod
  def header(cls):
    # header must be consistent with that in known_fields
    header = ['type', 'function', 'code_unit', 'astro_unit', 'alias']
    return header

  @classmethod
  def type(cls, field):
    return cls.known_fields[field][0]

  @classmethod
  def function(cls, field):
    return cls.known_fields[field][1]

  @classmethod
  def code_unit(cls, field):
    return cls.known_fields[field][2]

  @classmethod
  def astro_unit(cls, field):
    return cls.known_fields[field][3]

  @classmethod
  def alias(cls, field):
    return cls.known_fields[field][-1]

  @classmethod
  def list(cls):
    """ list of field name """
    return list(cls.known_fields.keys())

  @classmethod
  def brief(cls):
    """ Brief of callable fields """
    print(f'Field Name \t Alias')
    print('--------------------------------------')
    for key in cls.list():
      print(f'{key:10s} \t ',cls.alias(key))

  @classmethod
  def info(cls, name):
    """ Information of a given field """
    width = len(max(cls.header(), key=len))
    print('{1:{0}s}: \t {2:s}'.format(width+2, 'Name', name))
    for h in cls.header():
      print(f'{h.title():{width+2}}: \t {getattr(cls,h)(name)}')

  @classmethod
  def add_field(cls, name, type, **kwargs):
    function = kwargs.get('function')
    code_unit = kwargs.get('code_unit')
    astro_unit = kwargs.get('astro_unit')
    alias = kwargs.get('alias')
    if function is None:
      def create_function(f):
        lst = (type, f, code_unit, astro_unit, alias)
        cls.known_fields[name] = lst
        return f
      return create_function

    else:
      lst = (type, function, code_unit, astro_unit, alias)
      cls.known_fields[name] = lst

  @classmethod
  def setup_derived_field(cls):
# Below predefine some in-built derived field functions
    def _speed(data):
      mod = data.fields['vx1']*data.fields['vx1'] + data.fields['vx2']*data.fields['vx2'] + data.fields['vx3']*data.fields['vx3']
      return np.sqrt(mod)

    cls.add_field(
      name ='speed',
      type = 'scalar',
      function=_speed,
      code_unit='code_velocity',
      astro_unit='km/s',
      alias=['speed']
    )

# Above predefine some in-built derived field functions

add_field = PlutoFluidInfo.add_field

def derived_field(name, type, **kwargs):
  return add_field(name, type, kwargs)


class field_register(object):
  pass