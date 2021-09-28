import os
import fire
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from pluto_def_constants import PlutoDefConstants
from pluto_fluid_info import PlutoFluidInfo
from data_structs import Dataset, Snapshot
from operations import to_cart, slice2d, slice1d


class Preview(object):
  ''' Class for previewing data results.

  Args:
    wdir (str): absolute path to the dirctory.
    datatype (str): type of data files. Default is 'vtk'.
  '''

  # matplotlib setup
  mpl.rcParams['mathtext.fontset'] = 'cm'
  mpl.rcParams['font.family'] = 'serif'

  def __init__(self, wdir='./', datatype='vtk'):
    self.wdir = os.path.abspath(wdir)+'/'
    self.datatype = datatype

    self.fig = plt.figure(figsize=(5,4), tight_layout=True)


  def show(self):
    ''' show figure in prompt window '''

    return plt.show()


  def save(self, name=None, path='./', **kwargs):
    ''' save figure

    Args:
      name (str): specifiy filename. If it is None, the filename will be "field+index-model.jpg". (optional) Default is None
      path (str): path to save figure. (optional) Default is './'

    Returns:
      jpg file: with name of 'name-model.jpg', model is name of dirctory
    '''

    model = self.wdir.split('/')[-2]
    if name is None:
      plt.savefig(path+f'{self.field}{self.index}-{model}.jpg',bbox_inches='tight', pad_inches=0.02, dpi=kwargs.get('dpi',300))
    else:
      plt.savefig(path+name+'.jpg',bbox_inches='tight', pad_inches=0.02, dpi=kwargs.get('dpi',300))


  def display(self, ns, field, x1=None, x2=None, x3=None, log=True, **kwargs):
    ''' Display a 2D data using the matplotlib's pcolormesh

    Args:
      ns (int/float): should be a integer in default, \
          but if it is a negative integer, return the last number step or if it is a float, \
          it is assumed to be time, and return the nearst number step
      field: variable that needs to be displayed
      x1 (float): (optional) rough coordinate
      x2 (float): (optional) rough coordinate
      x3 (float): (optional) rough coordinate

    **kwargs:
      wdir (str): path to the directory which has the data files
      datatype (str): type of data files. Default is 'vtk'.
      vmin (float): The minimum value of the 2D array (Default : min(field))
      vmax (float): The maximum value of the 2D array (Default : max(field))
      cmap (str): color scheme of the colorbar
      title (str): Sets the title of the image.
      size (float): fontsize of title
    '''

    ds = Dataset(w_dir=kwargs.get('wdir', self.wdir), datatype=kwargs.get('datatype', self.datatype))
    ss = ds[ns]
    self.field = field
    self.index = ss.nstep

    if ss.geometry != 'CARTESIAN':
      ss = to_cart(ss)

    if kwargs.get('in_astro_unit'):
      ss.in_astro_unit()

    offset = [x1,x2,x3]
    label = ['x1','x2','x3']

    if ss.ndim==3:
      arr = ss.slice2d(field, x1=x1, x2=x2, x3=x3)
      for i in range(3):  # find the dirction
        if offset[i] is not None:
          dim = 'x'+str(i+1)
          label.remove(dim)
          break
      x1 = ss.coord[label[0]]
      x2 = ss.coord[label[1]]
    elif ss.ndim==2:
      arr = ss.fields[field]
      x1 = ss.grid['x1']
      x2 = ss.grid['x3']

    ax1 = self.fig.add_subplot(111)
    ax1.set_aspect('equal')
    if ss.is_quantity:  # pcolormesh does not support Quantity
      x1 = x1.value
      x2 = x2.value
      arr = arr.value
    ax1.axis([np.amin(x1),np.amax(x1),np.amin(x2),np.amax(x2)])
    if log:
      pcm = ax1.pcolormesh(x1,x2,arr,vmin=kwargs.get('vmin'),vmax=kwargs.get('vmax'), \
        cmap=kwargs.get('cmap'), shading='auto', norm=mpl.colors.LogNorm())
    else:
      pcm = ax1.pcolormesh(x1,x2,arr,vmin=kwargs.get('vmin'),vmax=kwargs.get('vmax'), \
        cmap=kwargs.get('cmap'), shading='auto')

    plt.title(kwargs.get('title',f't = {ss.time:.3e}'),size=kwargs.get('size'))

    # Add a new axes beside the plot to present colorbar
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes('right', size='5%', pad=0.0)
    cb = plt.colorbar(pcm, cax=cax,orientation='vertical')
    defined_fields = PlutoFluidInfo.known_fields
    if log:
      cb.ax.set_ylabel(r'$\log\;$'+defined_fields.get(field)[-1][0])
    else:
      cb.ax.set_ylabel(defined_fields.get(field)[-1][0])

    return self


  def line(self, ns, field, x1=None, x2=None, x3=None, **kwargs):
    ''' Show 1D profile

    Args:
      ns (int/float): should be a integer in default, \
          but if it is a negative integer, return the last number step or if it is a float, \
          it is assumed to be time, and return the nearst number step
      field: variable that needs to be displayed
      x1 (float): (optional) rough coordinate
      x2 (float): (optional) rough coordinate
      x3 (float): (optional) rough coordinate

    **kwargs:
      wdir (str): path to the directory which has the data files
      datatype (str): type of data files. Default is 'vtk'.
      xlog (bool): set x-axis in log scale
      ylog (bool): set x-axis in log scale
    '''

    ds = Dataset(w_dir=kwargs.get('wdir', self.wdir), datatype=kwargs.get('datatype', self.datatype))
    ss = ds[ns]
    self.field = field
    self.index = ss.nstep
    indx = [x1,x2,x3]
    label = ['x1','x2','x3']
    for i in range(3):
      if indx[i] is None:
        dim = label[i]
        x = ss.coord[dim]
        break

    value = ss.slice1d(field,x1=x1,x2=x2,x3=x3)

    plt.plot(x, value, label=f't={ss.time:.3e}')

    plt.title(kwargs.get('title','Title'),size=kwargs.get('size'))

    if kwargs.get('xlog'): plt.xscale('log')
    if kwargs.get('ylog'): plt.yscale('log')

    plt.legend(frameon=False)

    return self


  def hist(self, *var, op=None, **kwargs):  # in construction
    ''' Preview temperal evolution stored in hist.dat file '''

    hist = pd.read_csv(self.wdir+'hist.dat', sep='\s+', index_col='t')
    hist = hist[list(var)]

    if op is None:
      ax = plt.plot(hist)
      plt.legend(ax,var)
    elif op == 'diff':
      ax = plt.plot(hist-hist.iloc[[0]].values)
      plt.legend(ax,[f'{v}-{v}(0)' for v in var])
    elif op == 'norm':
      ax = plt.plot(hist/hist.iloc[[0]].values)
      plt.legend(ax,[f'{v}/{v}(0)' for v in var])
    else:
      raise KeyError(f'Operation [{op}] has not defined yet.')

    plt.title(kwargs.get('title','Title'),size=kwargs.get('size'))
    plt.xlabel(kwargs.get('label1','Time (code unit)'),size=kwargs.get('size'))
    plt.ylabel(kwargs.get('label2','Ylabel'),size=kwargs.get('size'))

    if kwargs.get('xlog'): plt.xscale('log')
    if kwargs.get('ylog'): plt.yscale('log')

    return self

if __name__ == '__main__':
  fire.Fire(Preview)