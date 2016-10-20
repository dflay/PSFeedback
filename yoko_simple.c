// Embedding python: call a python script from C 

#include <Python.h> 
#include <stdlib.h> 
#include <stdio.h> 

int main(int argc,char *argv[]){

   const int N = 3;  
   char *myArgs[N]; 
   myArgs[0] = "first"; 
   myArgs[1] = "192.168.5.160"; 
   myArgs[2] = "2.0654"; 

   // get python set up
   Py_SetProgramName(argv[0]);               // optional but recommended  
   Py_Initialize();                          // initialize python interpreter 
   // PySys_SetArgv(argc,argv);                 // must call this to get sys.argv and relative imports
   PySys_SetArgv(N,myArgs);                  // must call this to get sys.argv and relative imports

   // python file name    
   const int SIZE_100 = 100;  
   char *python_file_name = (char *)malloc( sizeof(char)*(SIZE_100+1) );
   sprintf(python_file_name  ,"%s","test3.py"); 

   // declare file object 
   FILE *myFile = fopen(python_file_name,"r");

   // run the python script 
   PyRun_SimpleFile(myFile,python_file_name);

   // free c pointers 
   free(python_file_name); 
   free(myFile); 

   // close down python interpreter 
   Py_Finalize(); 

   return 0;
}

