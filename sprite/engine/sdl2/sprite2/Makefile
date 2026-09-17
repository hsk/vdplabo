STAGES = stage1 stage2 stage3 stage4

CXX = c++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra $(shell sdl2-config --cflags)
LDFLAGS = $(shell sdl2-config --libs)

all: $(STAGES)

stage%: stage%.cpp stage%.hpp
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

run-%: %
	./$*

clean:
	rm -f $(STAGES)
