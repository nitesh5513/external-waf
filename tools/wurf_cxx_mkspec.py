#!/usr/bin/env python
# encoding: utf-8

import os, sys, inspect, ast

from waflib import Utils
from waflib import Context
from waflib import Options
from waflib import Errors

from waflib.Configure import conf
from waflib.Configure import ConfigurationContext

###############################
# ToolchainConfigurationContext
###############################

class ToolchainConfigurationContext(ConfigurationContext):
    '''configures the project'''
    cmd='configure'

    def init_dirs(self):
        # Waf calls this function to set the output dir.
        # Waf sets the output dir in the following order
        # 1) Check whether the -o option has been specified
        # 2) Check whether the wscript has an out varialble defined
        # 3) Fallback and use the name of the lockfile
        #
        # In order to not suprise anybody we will disallow the out variable
        # but allow our output dir to be overwritten by using the -o option

        assert(getattr(Context.g_module,Context.OUT,None) == None)

        if not Options.options.out:
            if Options.options.cxx_mkspec:
                self.out_dir = "build/"+Options.options.cxx_mkspec
            else:
                build_platform = Utils.unversioned_sys_platform()
                self.out_dir = "build/" + build_platform

        super(ToolchainConfigurationContext, self).init_dirs()

def options(opt):
    toolchain_opts = opt.add_option_group('mkspecs')

    toolchain_opts.add_option(
        '--cxx-mkspec', default = None,
        dest='cxx_mkspec',
        help="Select a specific cxx_mkspec. "+
             "Example: --cxx_mkspec=cxx_linux_x86-64_gxx4.6")

    toolchain_opts.add_option(
        '--cxx-mkspec-options', default = None, action="append",
        dest='cxx_mkspec_options',
        help="Some mkspec requires addtional options. Example: "+
             "--cxx-mkspec-options=NDK_DIR=~/.android-standalone-ndk/gcc4.4/bin"
        )

    opt.load("compiler_cxx")

def read_options(conf):
    conf.env["cxx_mkspec_options"] = {}
    if conf.options.cxx_mkspec_options:
        for option in conf.options.cxx_mkspec_options:
            try:
                key, value = option.split('=')
            except Exception, e:
                conf.fatal("cxx-mkspec-options has to have the format 'KEY=VALUE'"
                           ", you specified %r,"
                           "which resulted in Error:'%s'" %(option, e))
            conf.env["cxx_mkspec_options"][key] = value

def configure(conf):
    # Which mkspec should we use, by default, use the default one.
    mkspec = "cxx_default"

    if conf.options.cxx_mkspec:
        mkspec = conf.options.cxx_mkspec

    #Check to see if the given mkspec is allowed in this project.
    if filter and not filter(mkspec):
        raise Errors.WafError(
            msg="Unsupported mkspec, the mkspec must comply with:\n"+
            inspect.getsource(filter))

    #Where should we look for the mkspec?

    cxx_mkspec_path = "."
    try:
        cxx_mkspec_path = conf.env["BUNDLE_DEPENDENCIES"]["mkspec"]
    except Exception, e:
        # Just use the current directory then.
        pass

    read_options(conf)

    conf.load(mkspec, cxx_mkspec_path)
    conf.msg('Setting cxx_mkspec path to:', cxx_mkspec_path)
    conf.msg('Using the mkspec:', mkspec)

filter = None

@conf
def filter_mkspec(self, f):
    global filter
    filter = f