EXEC_FILE=tether
SRC_DIR=src
BUILD_DIR=build
INC_DIR=include

CC=gcc
CFLAGS=-ggdb -Wall


_OBJS=main.o
OBJS=$(patsubst %.o, $(BUILD_DIR)/%.o, $(_OBJS))

_INCL=$(INC_DIR)
INCL=$(patsubst %, -I%, $(_INCL))


#<< TARGETS >>#

build: $(OBJS)
	$(CC) $(CFLAGS) $(INCL) -o $(EXEC_FILE) $(OBJS)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) $(INCL) -o $@ -c $<

rebuild: clean build

clean: 
	rm -f $(BUILD_DIR)/*.o
	rm -f $(EXEC_FILE)
