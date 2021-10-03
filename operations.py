from .data_structs.dataset import Snapshot


def to_cart(data):
  ''' convert to cartesian coordinate system

  Currently only support converting:
    grids['x1']
    grids['x2']
    grids['x3']
    fields['vx1']
    fields['vx2']
    fields['vx3']

  Args:
    data (Snapshot): data needed to be converted geometry

  Returns:
    Snapshot: new Snapshot is as the same as the older one,
              except for grid and velocity arrays have been transformed to cartesian system
  '''

  ds = data
  ds.grid['x1'], ds.grid['x2'], ds.grid['x3'] = data.grids.to_cart()
  ds.fields['vx1'], ds.field['vx2'], ds.field['vx3'] = data.fields.to_cart()

  return ds


def slice2d(data, x1=None, x2=None, x3=None):
  ''' Slice all 3-D field arrays in original data return 2-D

  coordinate of one dimension should be specified

  Args:
    data (Snapshot): 3-D data
    x1 (float): rough coordinate (optional)
    x2 (float): rough coordinate (optional)
    x3 (float): rough coordinate (optional)
  '''

  if not type(data) is Snapshot:
    raise TypeError(f'The input data is a {type(data)}, it should be Snapshot class!')

  for var in data.field_list:
    data.fields[var] = data.slice2d(var, x1=x1, x2=x3, x3=x3)


def slice1d(data, x1=None, x2=None, x3=None):
  ''' Slice all 3-D fields array in original data return 1-D

  coordinates of two dimensions should be specified

  Args:
    data (Snapshot): 3-D data
    x1 (float): rough coordinate (optional)
    x2 (float): rough coordinate (optional)
    x3 (float): rough coordinate (optional)
  '''

  if not type(data) is Snapshot:
    raise TypeError('The input data should be Snapshot class!')

  for var in data.field_list:
    data.fields[var] = data.slice1d(var, x1=x1, x2=x3, x3=x3)
