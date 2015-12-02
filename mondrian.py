import logging
import time
import threading
import argparse
from wx.lib.pubsub import pub as Publisher
import json

import jenkins_status
import gerrit
import monitor_view


SECONDS_BETWEEN_POLLS = 120


# TODO:
# Power save. Ideally, it should be on during office hours.
# Would also like to put screen to sleep outside office hours, and always on otherwise.
# Is it possible to ping the screen saver?
#
# Make it run on Pi.

class MonitorThread(threading.Thread):
    """Thread class for monitoring the various servers
       (initially Gerrit and Jenkins)."""

    def __init__(self, jenkins_instance, gerrit_instance, gerrit_for_review_limits, gerrit_reviewed_limits):
        threading.Thread.__init__(self)
        self.running = False
        self.jenkins = jenkins_instance
        self.gerrit = gerrit_instance
        self.gerrit_for_review_limits = gerrit_for_review_limits
        self.gerrit_reviewed_limits = gerrit_reviewed_limits
        self.start()

    # TODO: An exception here will (?) crash the monitor thread but leave the view hanging.
    # Would be nice to close.
    def run(self):
        self.running = True
        while self.running:
            worst_jenkins_build = self.jenkins.get_worst_build_status()
            self.post_build_status(worst_jenkins_build)
            if not self.running:
                break

            worst_jenkins_test = self.jenkins.get_worst_ci_test_status()
            self.post_ci_test_status(worst_jenkins_test)
            if not self.running:
                break

            worst_jenkins_test = self.jenkins.get_worst_other_tests_status()
            self.post_other_tests_status(worst_jenkins_test)
            if not self.running:
                break

            (gerrit_for_review, gerrit_reviewed) = self.gerrit.all_open_changes()

            rfr_status = len(gerrit_for_review)
            self.post_ready_for_review_status(rfr_status)
            reviewed_status = len(gerrit_reviewed)
            self.post_reviewed_status(reviewed_status)

            t0 = time.time()
            t = t0
            while self.running and ((t - t0) < SECONDS_BETWEEN_POLLS):
                time.sleep(0.2)
                t = time.time()

        logging.debug('done monitoring')

    def post_build_status(self, status):
        view_status = monitor_view.STATUS_GOOD if status else monitor_view.STATUS_BAD
        Publisher.sendMessage(monitor_view.UPDATE_BUILD_PUBSUB, status=view_status)

    def post_ci_test_status(self, status):
        view_status = monitor_view.STATUS_GOOD if status else monitor_view.STATUS_BAD
        Publisher.sendMessage(monitor_view.UPDATE_CI_TEST_PUBSUB, status=view_status)

    def post_other_tests_status(self, status):
        view_status = monitor_view.STATUS_GOOD if status else monitor_view.STATUS_BAD
        Publisher.sendMessage(monitor_view.UPDATE_OTHER_TESTS_PUBSUB, status=view_status)

    def post_ready_for_review_status(self, status):
        if status == self.gerrit_for_review_limits['good']:
            view_status = monitor_view.STATUS_GOOD
        elif status < self.gerrit_for_review_limits['almost_good']:
            view_status = monitor_view.STATUS_ALMOST_GOOD
        elif status < self.gerrit_for_review_limits['almost_bad']:
            view_status = monitor_view.STATUS_ALMOST_BAD
        else:
            view_status = monitor_view.STATUS_BAD
        Publisher.sendMessage(monitor_view.UPDATE_GERRIT_FOR_REVIEW_PUBSUB, status=view_status)

    def post_reviewed_status(self, status):
        if status == self.gerrit_reviewed_limits['good']:
            view_status = monitor_view.STATUS_GOOD
        elif status < self.gerrit_reviewed_limits['almost_good']:
            view_status = monitor_view.STATUS_ALMOST_GOOD
        elif status < self.gerrit_reviewed_limits['almost_bad']:
            view_status = monitor_view.STATUS_ALMOST_BAD
        else:
            view_status = monitor_view.STATUS_BAD
        Publisher.sendMessage(monitor_view.UPDATE_GERRIT_REVIEWED_PUBSUB, status=view_status)

    def stop(self):
        self.running = False


def read_config():
    with open('mondrian.json') as json_data_file:
        data = json.load(json_data_file)
    return data


def run_app(full_screen=True, top_window=False):
    config_data = read_config()

    jenkins_data = config_data['jenkins']
    jenkins = jenkins_status.JenkinsStatus(base_url=jenkins_data['base_url'],
                                           build_jobs=jenkins_data['build_job_names'],
                                           ci_test_jobs=jenkins_data['ci_test_job_names'],
                                           other_test_jobs=jenkins_data['other_test_job_names'])

    gerrit_data = config_data['gerrit']
    gerrit_instance = gerrit.Gerrit(base_url=gerrit_data['base_url'])
    monitor = MonitorThread(jenkins,
                            gerrit_instance,
                            gerrit_data['limits_ready_for_review'],
                            gerrit_data['limits_reviewed'])

    monitor_view.run(full_screen, top_window)
    monitor.stop()
    monitor.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Display a monitor of Jenkins and Gerrit status.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--fullscreen', action='store_true', default=False,
                       help='Start the monitor in full screen mode. Close with Esc key.')
    group.add_argument('-t', '--top', action='store_true', default=False,
                       help='Start as "heads up display", a small window always on top.' +
                            'Close with Esc key.')
    args = parser.parse_args()
    print args
    run_app(full_screen=args.fullscreen, top_window=args.top)
