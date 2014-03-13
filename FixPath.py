import sublime, sublime_plugin
from os import environ
from subprocess import Popen, PIPE


fixPathSettings = None
originalEnv = {}


def getSysPath():
	command = "/usr/bin/login -fpql $USER $SHELL -l -c 'echo -n $PATH'"

	# Execute command with original environ. Otherwise, our changes to the PATH propogate down to
	# the shell we spawn, which re-adds the system path & returns it, leading to duplicate values.
	sysPath = Popen(command, stdout=PIPE, shell=True, env=originalEnv).stdout.read()

	# Decode the byte array into a string, remove trailing whitespace, remove trailing ':'
	return sysPath.decode("utf-8").rstrip().rstrip(':')


def fixPath():
	environ['PATH'] = getSysPath()

	for pathItem in fixPathSettings.get("additional_path_items", []):
		environ['PATH'] = pathItem + ':' + environ['PATH']


def plugin_loaded():
	global fixPathSettings
	fixPathSettings = sublime.load_settings("Preferences.sublime-settings")
	fixPathSettings.clear_on_change('fixpath-reload')
	fixPathSettings.add_on_change('fixpath-reload', fixPath)

	# Save the original environ (particularly the original PATH) to restore later
	global originalEnv
	for key in environ:
		originalEnv[key] = environ[key]

	fixPath()


def plugin_unloaded():
	# When we unload, reset PATH to original value. Otherwise, reloads of this plugin will cause
	# the PATH to be duplicated.
	environ['PATH'] = originalEnv['PATH']

	global fixPathSettings
	fixPathSettings.clear_on_change('fixpath-reload')


# Sublime Text 2 doesn't have loaded/unloaded handlers, so trigger startup code manually, first
# taking care to clean up any messes from last time.
if int(sublime.version()) < 3000:
	# Stash the original PATH in the env variable _ST_ORIG_PATH.
	if environ.has_key('_ST_ORIG_PATH'):
		# If _ST_ORIG_PATH exists, restore it as the true path.
		environ['PATH'] = environ['_ST_ORIG_PATH']
	else:
		# If it doesn't exist, create it
		environ['_ST_ORIG_PATH'] = environ['PATH']

	plugin_loaded()
