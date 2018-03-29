prog: test.c
	gcc -Wall -pthread -o prog test.c -lpigpio -lrt

