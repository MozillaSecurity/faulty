#!/usr/bin/env python3
"""
Resources:
https://github.com/mozillasecurity/mozilla-build-configs
https://build.fuzzing.mozilla.org/job/faulty/
https://github.com/mozillasecurity/faulty
https://fuzzmanager.fuzzing.mozilla.org/crashmanager/crashes/?&tool__name=faulty
"""
import re
import os
import sys
import shutil
import pprint
import datetime
import argparse
import tempfile
import subprocess

try:
    import psutil
except ImportError as ex:
    sys.exit("Run: pip3 install psutil")


asan_options = {
    "debug": 1,
    "strict_init_order": 1,
    "strict_memcmp": 1,
    "allow_user_poisoning": 1,
    "check_malloc_usable_size": 0,
    "alloc_dealloc_mismatch": 0,
    "allocator_may_return_null": 1,
    "detect_stack_use_after_return": 0,
    "detect_stack_use_after_scope": 1,
    "check_initialization_order": 1,
    "detect_invalid_pointer_pairs": 1,
    "start_deactivated": 1,
    "allow_addr2line": 1,
    "handle_ioctl": 1,
    "detect_deadlocks": 1,
    "intercept_tls_get_addr": 1,
    "strict_string_checks": 1,
    "print_cmdline": 1,
    "strip_path_prefix": "/srv/jenkins/jobs/faulty/workspace/"
}


firefox_environ = {
    "MOZ_IPC_MESSAGE_LOG": 1
}

faulty_environ = {
    "FAULTY_ENABLE_LOGGING": 1,
    "FAULTY_PROBABILITY": 5000,
    "FAULTY_PICKLE": 1,
    "FAULTY_PIPE": 0,
    "FAULTY_PARENT": 1,
    "FAULTY_CHILDREN": 1
}


class Faulty(object):

    @staticmethod
    def setup_environ(context=None):
        env = {}
        if context is None:
            return env
        for key, val in context.items():
            if isinstance(val, dict):
                env[key] = ','.join('{!s}={!r}'.format(k, v) for (k, v) in val.items())
            else:
                env[key] = str(val)
        return env

    @staticmethod
    def kill(proc_pid):
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()

    @staticmethod
    def setup_bucket_dir():
        logdir = os.path.join("sessions", datetime.datetime.now().strftime('%Y-%m-%d_%H-%M'))
        os.makedirs(logdir, exist_ok=True)
        return logdir


def main(args):
    environ = os.environ
    environ.update(Faulty.setup_environ(faulty_environ))
    environ.update(Faulty.setup_environ(firefox_environ))
    environ.update(Faulty.setup_environ({"ASAN_OPTIONS": asan_options}))
    environ.update(Faulty.setup_environ({"ASAN_SYMBOLIZER_PATH": "/root/firefox/llvm-symbolizer"}))
    environ.update({"DISPLAY": ":1"})

    profile_folder = tempfile.mkdtemp()
    profile_name = os.path.basename(profile_folder)
    command = [args.binary, '-no-remote', '-CreateProfile', '{} {}'.format(profile_name, profile_folder)]
    subprocess.call(command)
    shutil.copyfile("prefs.js", os.path.join(profile_folder, 'user.js'))

    command = [
        '/usr/bin/xvfb-run', '-e', '/dev/stdout', '-s', "'-screen 0 1024x768x24'",
        'rr record',
        args.binary, '-P', profile_name, '-no-remote', args.target, '-height', '300', '-width', '300'
    ]
    print("Running: {}".format(" ".join(command)))
    print("Environemnt:")
    pprint.pprint(dict(environ), width=1)

    proc = subprocess.Popen(
        " ".join(command),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        env=environ)
    try:
        proc.wait(timeout=args.process_timeout)
    except subprocess.TimeoutExpired:
        Faulty.kill(proc.pid)

    result = proc.stdout.read()

    print(result)

    if any(x in result for x in ["ABORT", "MOZ_CRASH", "ERROR: AddressSanitizer", "Assertion failure"]):
        path = Faulty.setup_bucket_dir()
        session_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        with open(os.path.join(path, "session-{}.txt".format(session_time)), "w") as fo:
            fo.write(result)
        with open(os.path.join(path, "environ-{}.txt".format(session_time)), "w") as fo:
            pprint.pprint(dict(environ), width=1, stream=fo)

        if "ERROR: AddressSanitizer" in result:
            regex = "(ERROR: AddressSanitizer:.*[Stats:|ABORTING|ERROR: Failed])"
            crashdata = re.findall(regex, result, re.DOTALL)[0]
            with open(os.path.join(path, "trace-{}.txt".format(session_time)), "w") as fo:
                fo.write(crashdata)

        if args.create_testcase:
            print("Preparing testcase, this will take a while...")
            subprocess.call(["tar", "cJfh", "testcase.tar.xz", "/root/.local/share/rr/latest-trace"], env={"XZ_OPT":"-9e"})
            shutil.move("testcase.tar.xz", path)
            print("Testcase created.")

        if args.publish_fuzzmanager:
            env = " ".join('{!s}={!r}'.format(k, v) for (k,v) in faulty_environ.items())
            env += " ASAN_OPTIONS=" + ",".join('{!s}={!r}'.format(k, v) for (k,v) in asan_options.items())
            subprocess.call([
                "python", "FuzzManager/Collector/Collector.py",
                "--serverauthtokenfile", "serverauthtoken.txt",
                "--serverhost", "fuzzmanager.fuzzing.mozilla.org",
                "--serverport", "443",
                "--serverproto", "https",
                "--tool", "faulty",
                "--sigdir", "/root/signatures",
                "--clientid", "159.203.206.233",
                "--env", env,
                "--submit",
                "--stdout", "{}/session-{}.txt".format(path, session_time),
                "--stderr", "{}/environ-{}.txt".format(path, session_time),
                "--crashdata", "{}/trace-{}.txt".format(path, session_time),
                "--binary", "/root/{}".format(args.binary)])

    if os.path.isdir(profile_folder):
        shutil.rmtree(profile_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Faulty Harness',
        prefix_chars='-',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-target', dest='target', metavar='name', default='www.google.com',
                        help='target application')
    parser.add_argument('-publish-fuzzmanager', dest='publish_fuzzmanager', action='store_true', default=False,
                        help='whether or not to publish results to FuzzManager.')
    parser.add_argument('-create_testcase', dest='create_testcase', action='store_true', default=False,
                        help='wheather or not to create a testcase with rr.')
    parser.add_argument('-process_timeout', dest='process_timeout', type=int, default=50,
                        help='the amount of the time the process shall live.')
    parser.add_argument('-binary', dest='binary', metavar='path', default='firefox/firefox',
                        help='target application')

    args = parser.parse_args()

    main(args)
