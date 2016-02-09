from libcpp cimport bool
import numpy as np
cimport numpy as np

ctypedef np.int16_t I16TYPE_t
ctypedef np.uint8_t U8TYPE_t
ctypedef unsigned char u8 
ctypedef unsigned int u32
ctypedef unsigned int *uint_p "uint_p"
ctypedef float *float_p "float_p"

DEF MPX_MXR = 2
DEF MPX_TPX = 3

cdef extern from "common.h":
    cdef enum _Data_Types:
        TYPE_BOOL
        TYPE_CHAR
        TYPE_UCHAR
        TYPE_BYTE
        TYPE_I16
        TYPE_U16
        TYPE_I32
        TYPE_U32
        TYPE_FLOAT
        TYPE_DOUBLE
        TYPE_STRING
        TYPE_LAST
    ctypedef _Data_Types Data_Types

    ctypedef struct ItemInfo:
        Data_Types type
        u32 count
        u32 flags
        char *name
        char *descr
        void *data

    ctypedef ItemInfo HwInfoItem

    # Make std::string accessable
    cdef extern from "string" namespace "std":
        cdef cppclass string:
            string()
            string(char * str )
        
            char* c_str()

    cdef extern from "stdlib.h":
        void free(void* ptr)
        void* malloc(size_t size)
        void* realloc(void* ptr, size_t size)

# import the MpxModule class
cdef extern from "mpxmodule.h":
    cdef cppclass MpxModule:
        MpxModule(int id, 
            int mpx_type,
            int ndevices,
            int nrows,
            int first_chipnr)

        bool   ping()

        string chipName(int chipNr)
        int	chipCount()
        int	chipType( int chipnr )
        int chipPosition( int chipnr )
        int getFirmwareVersion( u32 *version, u8 *revision )
        int getDriverVersion( )
#        int readSwVersion (u32 *vercion)
        
        int configAcqMode(
            bool ext_trig,
            bool use_timer,
            double time_s )
            
        void setParReadout ( bool b )
        bool parReadout ( )

        int getHwInfo( int index, HwInfoItem *hw_item, int *sz )
        int setHwInfo( int index, void *data, int sz )

        int setFsr( int chipnr, int *dac, unsigned long col_testpulse_reg )
        int readFsr( int chipnr,    int *dacs,  int *sz)
        int refreshFsr( int chipnr )
        void setLogVerbose ( bool b )
        bool logVerbose()

        int init()
        
        int enableTimer( bool enable, int us )
        
        bool timerExpired()

        int enableExtTrigger( bool enable)

        int openShutter( bool open )
        
        int readMatrix(short * buf, int size)
        int resetMatrix()
        
        int readMatrixRaw(u8 *buf, u32 *size, int *l_r)

        int eraseDacs()
        int erasePixelsCfg()
        
        int setPixelsCfg( u8 *cfgs, int chipnr )
        
        int setPixelsCfg( string filename, int mode )
        int setPixelsCfg( int mode, int thresh1,int thresh2,bool test,bool mask )
                          
        int getMpxDac(int chipnr, double *value )
        
        string lastErrStr()
        
        int resetChips()
        
        int readChipId      ( int chipnr, u32 *id )
        int readTsensor( int t_nr, u32 *degrees)
        int testPulseEnable ( bool enable )
        int configTestPulse ( u32 low, u32 high, u32 freq_05khz, u32 count )
        int generateTestPulses( double pulse_height, double period, u32 count )

        int readReg( u32 offset, u32 *value )
        int writeReg( u32 offset, u32 value )
        bool newFrame(bool check, bool clear)
        int storeId( u32 idid )
        

        
# Create the wrapper
cdef class PyMpxModule:
    cdef MpxModule *thisptr
	
    def __cinit__(self, int id, 
            int mpx_type = MPX_TPX,
            int ndevices = 0,
            int nrows = 1,
            int first_chipnr = 0):
        self.thisptr = new MpxModule(id, mpx_type, ndevices, nrows, first_chipnr)
		

    def __dealloc__(self):
        del self.thisptr



    def getHwInfo( self, int index ):
        cdef HwInfoItem hw_item    
        cdef int sz = 65535
        cdef char dataout
        cdef char tmp[1024]
        hw_item.data = tmp
        hwparsi = [0, 1, 3, 5, 6, 11, 12, 13, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
        hwparsf = [7, 8, 9, 10, 14, 15]
        hwparss = [2, 4, 17]

        if index in hwparsi:
            rv = self.thisptr.getHwInfo( index, &hw_item, &sz)
            return (rv, <bytes>hw_item.name, (<int*>hw_item.data)[0])
        elif index in hwparsf:
            rv = self.thisptr.getHwInfo( index, &hw_item, &sz)
            return (rv, <bytes>hw_item.name, (<float*>hw_item.data)[0])
        elif index in hwparss:
            rv = self.thisptr.getHwInfo( index, &hw_item, &sz)
            return (rv, <bytes>hw_item.name, <bytes>(<char*>hw_item.data))
        else:
            return (-1, -1)
    
                           

    def setHwInfo( self, int index, data):   
        cdef int sz = 4
        cdef char dataout
        cdef char tmp[1024]
        cdef u32 uout
        cdef float fout
        hwparsi = [11, 12, 13, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
        hwparsf = [9, 10]

        if index in hwparsi:
            uout=<u32>data
            rv = self.thisptr.setHwInfo( index, <void*>(&uout), sz)
            return (rv)
        elif index in hwparsf:
            fout=<float>data
            rv = self.thisptr.setHwInfo( index, <void*>(&fout), sz)
            return (rv)
        else:
            return (-1)

    def storeId(self, int idid):
        cdef u32 id1
        id1=<u32>idid
        rv = self.thisptr.storeId(id1)
        return rv
                           
    def chipName(self, int nr):
        cdef string chip
        chip = self.thisptr.chipName(nr)
        return chip.c_str()
        

    def chipCount(self):
        return self.thisptr.chipCount()
    	

    def chipType(self, chipNr):
        return self.thisptr.chipType(chipNr)

    	
    def chipPosition(self, chipNr):
        return self.thisptr.chipPosition(chipNr)


    def configAcqMode(self, bool ext_trig,
            bool use_timer = False,
            double time_s = 0.0001):
        return self.thisptr.configAcqMode( ext_trig, use_timer, time_s )

    def readReg( self, offset):
        cdef u32 value
        rv = self.thisptr.readReg(<u32>offset,&value)
        return (rv, value)

    def writeReg( self, offset, value):
        rv = self.thisptr.writeReg(<u32>offset,<u32>value)
        return (rv)

    def newFrame( self, bool check, bool clear):
        return (self.thisptr.newFrame(check,clear))
    

    def setFsr( self, int chipnr, list dacList, unsigned long col_testpulse_reg = 0 ):

        cdef int dacArr[20]
        for i in range(len(dacList)):
            dacArr[i] = dacList[i]        
        rv = self.thisptr.setFsr( chipnr, &dacArr[0], col_testpulse_reg )
        
        return rv
        

    def refreshFsr( self, int chipnr ):
        return self.thisptr.refreshFsr( chipnr )


    def readFsr( self, int chipnr ):
        cdef int dacs[20]       # 20 should be enough    
        cdef int sz
        rv = self.thisptr.readFsr( chipnr, &dacs[0], &sz )
        if rv != 0:
            return (rv, [])
        ret = []
        for i in range(0, sz):
            ret.append(dacs[i])
        return (rv, ret)
        
                
    
    def setLogVerbose ( self, bool b ):
        self.thisptr.setLogVerbose( b )

    def logVerbose ( self ):
        return self.thisptr.logVerbose( )

    def setParReadout ( self, bool b ): 
        self.thisptr.setParReadout( b )

    def parReadout ( self ): 
        return self.thisptr.parReadout( )

        
        
    def getFirmwareVersion( self ):
        cdef u32 v = 0
        cdef u8 r = 0
        rv = self.thisptr.getFirmwareVersion( &v, &r )
        return (rv, v, r)


    def getDriverVersion( self ):
        return self.thisptr.getDriverVersion( )

    def init( self ):
        return self.thisptr.init()
             
    def readMatrix( self, np.ndarray[I16TYPE_t, ndim=2] nparr not None ):
        cdef s = nparr.shape[0] * nparr.shape[0] 
        self.thisptr.readMatrix( <short*> nparr.data, s)

    def readMatrixRaw( self, np.ndarray[U8TYPE_t, ndim=1] nparr not None ):
        cdef u32 s=nparr.shape[0]
        cdef int ls_r=0
        self.thisptr.readMatrixRaw( <u8*>nparr.data, &s ,&ls_r)
        return (<int>s, ls_r)


    def resetMatrix(self):
        return self.thisptr.resetMatrix()

    def eraseDacs(self):
        return self.thisptr.eraseDacs()

    def erasePixelsCfg(self):
        return self.thisptr.erasePixelsCfg()    

    def enableTimer( self, bool enable, int us = 10):
        return self.thisptr.enableTimer( enable, us)

    def timeExpired(self):
        return self.thisptr.timerExpired()

    def enableExtTrigger( self, bool enable):
        return self.thisptr.enableExtTrigger( enable)    

    def openShutter(self):
        return self.thisptr.openShutter(True)
        
    def closeShutter(self):
        return self.thisptr.openShutter(False)

    def testPulseEnable(self,bool enable):
        return self.thisptr.testPulseEnable(enable)
    
    def ping(self):
        return self.thisptr.ping()
        
    def setPixelsCfg( self, np.ndarray[U8TYPE_t, ndim=2] pixCfg, int chipNr = -1):
        return self.thisptr.setPixelsCfg(<unsigned char*>pixCfg.data, chipNr)

    def setPixelsCfgFromFile( self, char * filename, int mode = -1):
        return self.thisptr.setPixelsCfg(string(filename), mode)
    
    def setAllPixelsCfg( self, int mode, int thresh1, int thresh2, bool test = False, bool mask = True):
        return self.thisptr.setPixelsCfg( mode, thresh1, thresh2, test, mask )

    def getMpxDac( self, int chipNr ):
        cdef double v
        rv = self.thisptr.getMpxDac(chipNr, &v )
        return (rv, v)
        
    def lastErrStr(self):
        cdef string chip
        chip = self.thisptr.lastErrStr()
        return chip.c_str()

    def resetChips(self):
        return self.thisptr.resetChips()
    
    def readChipId(self, int chipNr):
        cdef u32 v
        rv = self.thisptr.readChipId(chipNr, &v )
        return (rv, v)
 
    def readTsensor(self,int t_nr):
        cdef u32 v
        rv = self.thisptr.readTsensor(t_nr, &v )
        return (rv, v)

    def configTestPulse (self, u32 low, u32 high, u32 freq_05khz, u32 count ):
        return self.thisptr.configTestPulse (low, high, freq_05khz, count )
    def generateTestPulses(self, double pulse_height, double period, u32 count ):
        return self.thisptr.generateTestPulses( pulse_height, period, count )

