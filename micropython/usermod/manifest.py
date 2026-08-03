# Freezes ../src/a7p.py (the pure-Python uctypes wrapper) into the firmware
# image, alongside the `_a7p` C module usermod already compiles in -- so
# `import a7p` works right after flashing, with no separate file copy step.
#
# This is a fragment, not a complete FROZEN_MANIFEST by itself: a build's
# FROZEN_MANIFEST already points at that port's own default manifest (it
# freezes required stdlib bits like asyncio, and per-board extras), and
# pointing FROZEN_MANIFEST straight at this file instead would silently drop
# all of that. Write a small custom manifest that includes both, and pass
# *that* as FROZEN_MANIFEST:
#
#   # my_manifest.py
#   include("$(PORT_DIR)/boards/manifest.py")   # this port's own default --
#                                                # see README.md's table for
#                                                # the exact default path per
#                                                # port (it isn't always
#                                                # boards/manifest.py)
#   include("/path/to/a7p/micropython/usermod/manifest.py")
#
#   make BOARD=... USER_C_MODULES=/path/to/a7p/micropython/usermod \
#        FROZEN_MANIFEST=/path/to/my_manifest.py
#
# freeze()'s path argument is resolved relative to *this* file's own
# directory, so it works regardless of where the a7p repo sits on disk or
# which port includes it.
freeze("../src", "a7p.py")  # noqa: F821 -- manifest DSL global, injected by make_manifest.py
