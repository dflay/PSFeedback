// Embedding python: call python functions from C 

#include <Python.h> 
#include <stdlib.h> 
#include <stdio.h> 
#include "yokogawa_constants.h"

int CheckPtr(char *name,PyObject *);
char *GetString(PyObject *);  
PyObject *CallMethod(PyObject *pInstance,char *method_name,char *arg);

int main(int argc,char *argv[]){

   Py_SetProgramName(argv[0]);                                          // optional but recommended  
   Py_Initialize();                                                     // initialize python interpreter 
   PySys_SetArgv(argc, argv);                                           // must call this to get sys.argv and relative imports

   PyObject *pName     = PyString_FromString(YOKOGAWA_SOURCE_NAME);       // build the name object 
   if ( CheckPtr("pName",pName)==1 )     return 1; 
   PyObject *pModule   = PyImport_Import(pName);                        // load the module 
   if ( CheckPtr("pModule",pModule)==1 ) return 1; 
   PyObject *pDict     = PyModule_GetDict(pModule);                     // get the dictionary 
   if ( CheckPtr("pDict",pDict)==1 )     return 1; 
   PyObject *pClass    = PyDict_GetItemString(pDict,YOKOGAWA_CLASS_NAME); // find the class in the dictionary 
   if ( CheckPtr("pClass",pClass)==1 )   return 1; 
   PyObject *pInstance = NULL;                                          // instance of the class  

   // yokogawa info 
   // build a python tuple to pass to the function 
   const int SIZE_1 = 1; 
   PyObject *pArgs = PyTuple_New(SIZE_1);
   PyTuple_SetItem( pArgs,0,PyString_FromString(YOKOGAWA_IP_ADDRESS) );  

   // check if we have a callable function 
   if ( PyCallable_Check(pClass) ){ 
      pInstance = PyObject_CallObject(pClass,pArgs); 
   } else {
      printf("ERROR: Can't make an instance of the '%s' class! \n",YOKOGAWA_CLASS_NAME); 
      PyErr_Print();
      return 1;  
   } 

   char *level = "2E-3"; 

   // Call some functions 
   // Note: 
   //  - getter methods return values (strings) 
   //  - setter methods do not return values 

   PyObject *pValue = CallMethod(pInstance,YOKOGAWA_OPEN_VXI_CONNECTION ,NULL); // the CallMethod function calls Py_INCREF()
   Py_DECREF(pValue);   // Need to call DECREF to decrease the reference count since we're done with it 
   pValue           = CallMethod(pInstance,YOKOGAWA_GET_DEVICE_ID       ,NULL);  
   Py_DECREF(pValue);
   pValue           = CallMethod(pInstance,YOKOGAWA_PRINT               ,NULL);  
   Py_DECREF(pValue);
   pValue           = CallMethod(pInstance,YOKOGAWA_GET_MODE            ,NULL); 
   Py_DECREF(pValue);
   printf("Mode = %s \n", GetString(pValue) );  
   pValue           = CallMethod(pInstance,YOKOGAWA_GET_OUTPUT_STATE    ,NULL); 
   Py_DECREF(pValue);
   printf("Output state = %s \n", GetString(pValue) );  
   printf("Setting the level to %s A \n",level); 
   pValue           = CallMethod(pInstance,YOKOGAWA_SET_LEVEL           ,level);  
   Py_DECREF(pValue);
   pValue           = CallMethod(pInstance,YOKOGAWA_GET_LEVEL           ,NULL);  
   Py_DECREF(pValue);
   printf("Level = %s \n", GetString(pValue) );  
   pValue           = CallMethod(pInstance,YOKOGAWA_CLOSE_VXI_CONNECTION,NULL);  
   Py_DECREF(pValue);
 
   // clean up memory 
   Py_DECREF(pModule); 
   Py_DECREF(pName); 
   Py_DECREF(pInstance); 
   Py_DECREF(pClass); 

   // close down python interpreter 
   Py_Finalize(); 

   return 0;
}
//______________________________________________________________________________
int CheckPtr(char *name,PyObject *ptr){
   if(ptr==NULL){
      printf("%s is NULL! \n",name);
      PyErr_Print(); 
      return 1;
   } else { 
      Py_INCREF(ptr); 
   } 
   return 0;
}
//______________________________________________________________________________
char *GetString(PyObject *pValue){
   char *my_str = (char *)PyString_AsString(pValue);
   return my_str;  
}
//______________________________________________________________________________
PyObject *CallMethod(PyObject *pInstance,char *method_name,char *arg){
   // // build argument list 
   // const int SIZE = 1; 
   // PyObject *pArgs = PyTuple_New(SIZE);
   // PyTuple_SetItem( pArgs,i,PyString_FromString(arg) ); 
   PyObject *pValue = NULL;  
   if (arg!=NULL) {
      pValue = PyObject_CallMethod(pInstance,method_name,"(s)",arg);  
   } else { 
      pValue = PyObject_CallMethod(pInstance,method_name,NULL);       
   }
   int is_valid = CheckPtr("pValue",pValue);
   if (is_valid==1) { 
      printf("[CallMethod]: Invalid pointer for use with method '%s' \n",method_name); 
      return NULL; 
   } 
   return pValue;  
}
