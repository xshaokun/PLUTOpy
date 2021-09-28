class PlutoDefConstants(object):
  ''' Physical constants in c.g.s units defined in $PLUTO_DIR/Src/pluto.h '''

  __pluto_def_constants = {
    'CONST_AH'  : 1.008     ,
    'CONST_AHe'   : 4.004     ,
    'CONST_AZ'  : 30.0      ,
    'CONST_amu'   : 1.66053886e-24  ,
    'CONST_au'  : 1.49597892e13   ,
    'CONST_c'   : 2.99792458e10   ,
    'CONST_e'   : 4.80320425e-10  ,
    'CONST_eV'  : 1.602176463158e-12,
    'CONST_G'   : 6.6726e-8     ,
    'CONST_h'   : 6.62606876e-27  ,
    'CONST_kB'  : 1.3806505e-16   ,
    'CONST_ly'  : 0.9461e18     ,
    'CONST_mp'  : 1.67262171e-24  ,
    'CONST_mn'  : 1.67492728e-24  ,
    'CONST_me'  : 9.1093826e-28   ,
    'CONST_mH'  : 1.6733e-24    ,
    'CONST_Msun'  : 2.e33       ,
    'CONST_Mearth': 5.9736e27     ,
    'CONST_NA'  : 6.0221367e23    ,
    'CONST_pc'  : 3.0856775807e18   ,
    'CONST_PI'  : 3.14159265358979  ,
    'CONST_Rearth': 6.378136e8    ,
    'CONST_Rgas'  : 8.3144598e7     ,
    'CONST_Rsun'  : 6.96e10       ,
    'CONST_sigma' : 5.67051e-5    ,
    'CONST_sigmaT': 6.6524e-25
  }

  def __init__(self):
    for key, value in self.__pluto_def_constants.items():
      setattr(self, key, value)