import numpy as np


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
    'tmp'       :('scalar', None, 'K',   'K',  ['temperature'  ]),
    'phi'       :('scalar', None, 'code_velocity**2',   'km**2/s**2',  ['potential'  ]),
  }

  @classmethod
  def show(cls):
    print(f'Field Name \t Unit       \t Alias')
    print('--------------------------------------')
    for key, value in cls.known_fields.items():
      print(f'{key:10s} \t {value[2]:10} \t {value[-1]}')

  @classmethod
  def info(cls, name):
    header = ['type', 'function', 'code unit', 'astro unit', 'dimension', 'alias']
    width = len(max(header, key=len))
    print('{1:{0}s}: \t {2:s}'.format(width+2, 'name'.title(), name))
    for h, v in zip(header, cls.known_fields[name]):
      print(f'{h.title():{width+2}}: \t {v}')

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

add_field = PlutoFluidInfo.add_field

def derived_field(name, type, **kwargs):
  return add_field(name, type, kwargs)