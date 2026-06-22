.DEFAULT_GOAL := check
.PHONY: __repository-make-authority build check lint root-test test verify
.SECONDEXPANSION:

override SHELL := /bin/sh
override .SHELLFLAGS := -c
build check lint root-test test verify __repository-make-authority: override SHELL := /bin/sh
build check lint root-test test verify __repository-make-authority: override .SHELLFLAGS := -c

ifneq ($(filter command line,$(origin MAKEFLAGS)),)
$(error MAKEFLAGS must not be overridden for repository verification)
endif
override REPOSITORY_MAKE_FIRST_FLAGS := $(firstword $(MAKEFLAGS))
ifneq ($(filter -%,$(REPOSITORY_MAKE_FIRST_FLAGS)),)
override REPOSITORY_MAKE_FIRST_FLAGS :=
endif
override REPOSITORY_MAKE_SHORT_FLAGS := $(REPOSITORY_MAKE_FIRST_FLAGS) $(filter-out --%,$(filter -%,$(MAKEFLAGS)))
ifneq ($(findstring n,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring t,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring q,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring i,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(filter --just-print --dry-run --recon --touch --question --ignore-errors,$(MAKEFLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif

override ROOT := $(shell path='$(subst ','"'"',$(value MAKEFILE_LIST))'; path=$$(/usr/bin/printf '%s' "$$path" | /usr/bin/sed 's/^ //'); [ -f "$$path" ] || exit 1; directory=$$(/usr/bin/dirname -- "$$path"); /usr/bin/printf '%s\n' "$$directory" | /usr/bin/grep -q '^/' || directory=./$$directory; CDPATH= cd "$$directory" && /bin/pwd -P)
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif
override PYTHON := $(ROOT)/scripts/run-python.sh
override XCODEBUILD := $(ROOT)/scripts/run-xcodebuild.sh
export PYTHON ROOT XCODEBUILD

build check lint root-test test verify:: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
build check lint root-test test verify:: $$(if $$(shell path=$$$$(/usr/bin/printf '%s' '$$(subst ','"'"',$$(MAKEFILE_LIST))' | /usr/bin/sed 's/^ //') && [ -f "$$$$path" ] && /usr/bin/printf '%s' ok),,$$(error repository Makefile must be loaded alone))
build check lint root-test test verify:: __repository-make-authority

__repository-make-authority::
	@:

root-test::
	@"$$PYTHON" "$$ROOT/scripts/test-make-trust-boundary.py"

lint::
	@"$$PYTHON" "$$ROOT/scripts/check-baseline.py"
	@"$$PYTHON" "$$ROOT/scripts/test-project-topology.py"

check:: lint

test:: check
	@if "$$XCODEBUILD" --available; then cd "$$ROOT" && "$$ROOT/scripts/run-tests.sh"; else /usr/bin/printf '%s\n' "Skipping XCTest: xcodebuild is not installed."; fi

build:: check

verify:: root-test test build
