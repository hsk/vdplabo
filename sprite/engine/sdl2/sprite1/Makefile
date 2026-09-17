CXX = c++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra $(shell sdl2-config --cflags)
LDFLAGS = $(shell sdl2-config --libs)

stage1: stage1.cpp stage1.hpp
	$(CXX) $(CXXFLAGS) stage1.cpp -o stage1 $(LDFLAGS)

run: stage1
	./stage1

clean:
	rm -f stage1
