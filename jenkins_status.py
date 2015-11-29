from array import *
import argparse
from jenkinsapi.jenkins import Jenkins


# TODO:
# More nuanced output than True/False. How about Jenkins levels, Success, unstable, and error?

class JenkinsStatus(object):

    def __init__(self, base_url, build_jobs=None, ci_test_jobs=None, other_test_jobs=None):
        self.jenkins_url = base_url
        self.server = None
        self.build_jobs = build_jobs
        self.ci_test_jobs = ci_test_jobs
        self.other_test_jobs = other_test_jobs

    def get_server_instance(self):
        if not self.server:
            self.server = Jenkins(self.jenkins_url)
        return self.server

    def get_latest_job(self, jenkins_job):
        server = self.get_server_instance()
        job = server[jenkins_job]
        latest = job.get_build(job.get_last_completed_buildnumber())
        return latest

    def get_latest_job_status(self, jenkins_job):
        job = self.get_latest_job(jenkins_job)
        status = job.get_status()
        return status

    def get_worst_build_status(self):
        return self.get_worst_status(self.build_jobs)

    def get_worst_ci_test_status(self):
        return self.get_worst_status(self.ci_test_jobs)

    def get_worst_other_tests_status(self):
        return self.get_worst_status(self.other_test_jobs)

    def get_worst_status(self, jobs, printout=False):
        worst_status = True
        for job in jobs:
            if printout:
                print 'Jenkins Job: ' + job
                print self.get_latest_job(job)
            status = self.get_latest_job_status(job)
            if status != 'SUCCESS':
                worst_status = False
            if printout:
                print status
                print
        return worst_status

    def get_all_jobs(self):
        return self.get_server_instance().get_jobs()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get Jenkins status.')
    parser.add_argument('url')
    parser.add_argument('-j', '--job', required=False)
    args = parser.parse_args()

    jobs = [args.job] if args.job else None
    j = JenkinsStatus(base_url=args.url, build_jobs=jobs)
    if jobs:
        j.get_worst_status(jobs, True)
    else:
        for job in j.get_all_jobs():
            print job[0]
