# CMake fragment for CMake-based ports (rp2, esp32, ...). Included by
# ../micropython.cmake -- point USER_C_MODULES directly at that file:
#
#   cd micropython/ports/rp2
#   cmake -B build -DUSER_C_MODULES=/path/to/a7p/micropython/usermod/micropython.cmake
#   cmake --build build
#
# nanopb isn't vendored -- FetchContent below pulls the same pinned commit
# ../../natmod/Makefile's fetch-nanopb uses, at CMake configure time. This
# runs once per configure (FetchContent's own caching handles re-runs)
# regardless of which port/board includes this file, so setting
# USER_C_MODULES is the only step needed.

include(FetchContent)

file(STRINGS "${CMAKE_CURRENT_LIST_DIR}/../../NANOPB_COMMIT" A7P_NANOPB_COMMIT LIMIT_COUNT 1)

FetchContent_Declare(
    a7p_nanopb
    GIT_REPOSITORY https://github.com/nanopb/nanopb.git
    GIT_TAG        ${A7P_NANOPB_COMMIT}
)
# Populate only (download/checkout the source) -- deliberately not
# FetchContent_MakeAvailable(), which would also add_subdirectory() nanopb's
# own CMakeLists.txt: that pulls in its generator (needs a local `protoc`)
# and its own compiled library target, neither of which we want since we
# compile pb_common.c/pb_decode.c/pb_encode.c ourselves as plain sources
# below (matching how natmod/Makefile and ./micropython.mk use it too).
FetchContent_GetProperties(a7p_nanopb)
if(NOT a7p_nanopb_POPULATED)
    FetchContent_Populate(a7p_nanopb)
endif()

add_library(usermod_a7p INTERFACE)

target_sources(usermod_a7p INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/a7p_mod.c
    ${CMAKE_CURRENT_LIST_DIR}/../../src/profedit.pb.c
    ${CMAKE_CURRENT_LIST_DIR}/../../src/a7p_validate.c
    ${a7p_nanopb_SOURCE_DIR}/pb_common.c
    ${a7p_nanopb_SOURCE_DIR}/pb_decode.c
    ${a7p_nanopb_SOURCE_DIR}/pb_encode.c
)

target_include_directories(usermod_a7p INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/../../src
    ${a7p_nanopb_SOURCE_DIR}
)

# Same flags as natmod/Makefile / ./micropython.mk -- see the comment there.
target_compile_definitions(usermod_a7p INTERFACE
    PB_BUFFER_ONLY=1
    PB_WITHOUT_64BIT=1
)
target_compile_options(usermod_a7p INTERFACE -fno-short-enums)

target_link_libraries(usermod INTERFACE usermod_a7p)
