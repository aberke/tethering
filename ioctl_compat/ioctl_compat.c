/* 

Author: Neil Fulwiler
Date  : 11.27.2012
Usage : This file will be run by the python script
		in order to extract the appropriate numbers 
		for IOC_IN and IOC_OUT. Simply opens the 
		file (filename passed in as first argument)
		and then writes the values of IOC_IN and IOC_OUT
		to the file

*/

#include <sys/ioccom.h>
#include <stdio.h>

void usage(char** argv){
	printf("Usage: %s <filename>\n", argv[0]);
}

int main(int argc, char** argv){
/* check for appropriate args */
	if(argc < 2){
		usage(argv);
		return(1);
	}

/* open the file */
	char* filename = argv[1];
	FILE* f = fopen(filename, "w");
	if(!f){
		printf("Unable to open file '%s' for writing\n", filename);
		return(1);
	}

/* write the desired numbers to the file */
	fprintf(f, "IOC_IN:%u\n", IOC_IN);	
	fprintf(f, "IOC_OUT:%u\n", IOC_OUT);

/* clean up */
	fclose(f);
	return(0);
}
