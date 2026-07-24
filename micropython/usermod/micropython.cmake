# Top-level aggregator -- this is the file to point USER_C_MODULES at for
# CMake-based ports (rp2, esp32, ...):
#
#   cmake -B build -DUSER_C_MODULES=/path/to/a7p/micropython/usermod/micropython.cmake
#
# (For Make-based ports, point USER_C_MODULES at this directory instead --
# see a7p/micropython.mk.)
include(${CMAKE_CURRENT_LIST_DIR}/a7p/micropython.cmake)
